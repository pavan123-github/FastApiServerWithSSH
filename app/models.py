from sqlalchemy import Column, Integer, String,DateTime
from .database import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)

class Server(Base):
    __tablename__ = "servers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    host = Column(String, nullable=False)
    username = Column(String, nullable=False)
    port = Column(Integer, default=22)
    

class CommandLog(Base):
    __tablename__ = "command_logs"

    id = Column(Integer, primary_key=True)
    server_id = Column(Integer)
    command = Column(String)
    output = Column(String)
    error = Column(String)
    executed_at = Column(DateTime, default=datetime.utcnow)