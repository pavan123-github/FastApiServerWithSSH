from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.auth import get_current_user
from app.server import router as server_router
from .models import CommandLog
from .schemas import CommandRequest 




app = FastAPI(
    title="Fastapi job project with ssh",
    description="Fastapi project for job + real world use",
    version='1.0.0'
)
app.include_router(server_router)

@app.get('/')
def root():
    return {'message':'Fastapi is running successully!'}

@app.get('/health')
def health_check():
    return {'status':'ok'}

from .database import Base, engine
from .models import User
from .schemas import UserCreate, UserLogin
from .auth import hash_password, verify_password, create_access_token
from .deps import get_db

Base.metadata.create_all(bind=engine)



@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    hashed = hash_password(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed
    )
    db.add(new_user)
    db.commit()
    return {"msg": "User registered successfully"}

@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": db_user.username})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/protected")
def protected_route(user: str = Depends(get_current_user)):
    return {
        "message": "You are authenticated",
        "user": user
    }

@server_router.post("/{server_id}/execute")
def execute_command(
    server_id: int,
    data: CommandRequest,
    db: Session = Depends(get_db),
    user: str = Depends(get_current_user)
):
    try:
        output = "SSH timeout (Windows local testing)"
        status = "failed"

        log = CommandLog(
            server_id=server_id,
            command=data.command,
            output=output,
            status=status
        )
        db.add(log)
        db.commit()

        return {
            "message": "Command logged successfully",
            "status": status
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))