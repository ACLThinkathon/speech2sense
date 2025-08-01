from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from databaseLib.models import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./speech2sense.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

