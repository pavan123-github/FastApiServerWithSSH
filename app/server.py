from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import Server
from .schemas import ServerCreate, ServerResponse
from .auth import get_current_user
from .ssh_service import execute_ssh_command
from .models import CommandLog

router = APIRouter(
    prefix="/servers",
    tags=["Servers"]
)

# DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=ServerResponse)
def create_server(
    server: ServerCreate,
    db: Session = Depends(get_db),
    user: str = Depends(get_current_user)
):
    new_server = Server(**server.dict())
    db.add(new_server)
    db.commit()
    db.refresh(new_server)
    return new_server


@router.get("/", response_model=list[ServerResponse])
def list_servers(
    db: Session = Depends(get_db),
    user: str = Depends(get_current_user)
):
    return db.query(Server).all()


@router.post("/{server_id}/execute")
def execute_command(
    server_id: int,
    command: dict,
    db: Session = Depends(get_db),
    user: str = Depends(get_current_user)
):
    server = db.query(Server).filter(Server.id == server_id).first()
    if not server:
        return {"error": "Server not found"}

    result = execute_ssh_command(
        host=server.host,
        username=server.username,
        port=server.port,
        password="YOUR_SERVER_PASSWORD",
        command=command["command"]
    )

    log = CommandLog(
        server_id=server.id,
        command=command["command"],
        output=result.get("output"),
        error=result.get("error")
    )
    db.add(log)
    db.commit()

    return result