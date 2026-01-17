from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import Server
from .schemas import ServerCreate, ServerResponse
from .auth import get_current_user
from .ssh_service import execute_ssh_command
from .models import CommandLog
from app.email_utils import send_email
from fastapi import BackgroundTasks

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
    
    background_tasks: BackgroundTasks,
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
    
    background_tasks.add_task(
        send_email,
        "pavanmore@yopmail.com",
        "SSH Command Executed",
        str(result)
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

import smtplib
from email.message import EmailMessage

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = "Client Email"
EMAIL_PASSWORD = "Client Password"


def send_email(to_email: str, subject: str, body: str):
    msg = EmailMessage()
    msg["From"] = EMAIL_SENDER
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)

        return True

    except Exception as e:
        print("Email Error:", e)
        return False
