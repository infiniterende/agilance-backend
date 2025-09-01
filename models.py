import os
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Boolean,
    Text,
    TIMESTAMP,
    func,
    text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv

load_dotenv()
# Read the database URL from environment variable
DATABASE_URL = os.getenv("SUPABASE_DATABASE_URL")
# Create engine
print(DATABASE_URL)
engine = create_engine(DATABASE_URL)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()
# Base class for declarative models
Base = declarative_base()


# Define your model class (example for patients table)
class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    name = Column(String(100))
    gender = Column(String(100))
    age = Column(Integer, nullable=False)
    phone_number = Column(String(100))
    pain_quality = Column(Text, nullable=False)
    location = Column(Text, nullable=False)
    stress = Column(Text, nullable=False)
    sob = Column(Text, nullable=False)  # shortness of breath
    hypertension = Column(Text, nullable=False)
    diabetes = Column(Text, nullable=False)
    hyperlipidemia = Column(Text, nullable=False)
    smoking = Column(Text, nullable=False)
    probability = Column(Integer, nullable=False)


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)


# Drop all tables
# Base.metadata.drop_all(bind=engine)

with engine.begin() as conn:
    conn.execute(text("DROP TABLE IF EXISTS patients CASCADE;"))
    conn.execute(text("DROP TABLE IF EXISTS doctors CASCADE;"))
# Recreate all tables
Base.metadata.create_all(bind=engine)
print("All tables created.")


# Create tables in the database
def init_db():
    Base.metadata.create_all(bind=engine)

    patients = session.query(Patient).all()
    doctors = session.query(Doctor).all()
    for patient in patients:
        print(
            f"{patient.id}: {patient.name}, {patient.age}, {patient.gender}, "
            f"{patient.phone_number}, {patient.pain_quality}, {patient.location}, "
            f"Stress: {patient.stress}, SOB: {patient.sob}, HTN: {patient.hypertension}, "
            f"DM: {patient.diabetes}, HLD: {patient.hyperlipidemia}, Smoke: {patient.smoking}, "
            f"Prob: {patient.probability}"
        )


if __name__ == "__main__":
    init_db()
    print("Tables created!")
