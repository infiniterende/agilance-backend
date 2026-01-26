from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path
from dotenv import load_dotenv
import os

dotenv_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=dotenv_path)
DATABASE_URL = os.getenv("SUPABASE_DATABASE_URL")
# Replace with your actual database URL
DATABASE_URL = os.getenv("SUPABASE_DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
