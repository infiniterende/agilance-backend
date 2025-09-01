# view_data.py

from models import Patient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

# Query all patients
patients = session.query(Patient).all()
print(patients)
for patient in patients:
    print(
        f"{patient.id}: {patient.name}, {patient.age}, {patient.gender}, "
        f"{patient.phone_number}, {patient.pain_quality}, {patient.location}, "
        f"Stress: {patient.stress}, SOB: {patient.sob}, HTN: {patient.hypertension}, "
        f"DM: {patient.diabetes}, HLD: {patient.hyperlipidemia}, Smoke: {patient.smoking}, "
        f"Prob: {patient.probability}"
    )
