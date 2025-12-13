import sqlite3
from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy import event, Engine
from typing import Generator
from dotenv import load_dotenv
import logging
import os  

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL"))

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session