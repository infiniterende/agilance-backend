# seed_supabase.py
import os
import pandas as pd
from pathlib import Path
from sqlalchemy import Column, Integer, String, Boolean, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

# ----------------------------
# 1. Load .env
# ----------------------------
dotenv_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

DATABASE_URL = os.getenv("DATABASE_URL")
assert DATABASE_URL, "❌ SUPABASE_DATABASE_URL is not set!"

# ----------------------------
# 2. Database setup
# ----------------------------
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

Base.metadata.drop_all(bind=engine)


# ----------------------------
# 3. Patient model
# ----------------------------
class Patient(Base):
    __tablename__ = "patients"
    _table_args__ = {"schema": "public"}  # <-- explicitly use public schema
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    pain_quality = Column(String, nullable=True)
    location = Column(String, nullable=True)
    stress = Column(Boolean, nullable=True)
    sob = Column(Boolean, nullable=True)
    hypertension = Column(Boolean, nullable=True)
    diabetes = Column(Boolean, nullable=True)
    hyperlipidemia = Column(Boolean, nullable=True)
    smoking = Column(Boolean, nullable=True)
    probability = Column(Float, nullable=True)


# Create table in Supabase if it doesn't exist
Base.metadata.create_all(bind=engine)

# ----------------------------
# 4. Example DataFrame
# ----------------------------
data = {
    "name": ["Alice Smith", "Bob Johnson"],
    "age": ["45", "60"],
    "gender": ["Female", "Male"],
    "phone_number": ["555-123-1111", "555-123-2222"],
    "pain_quality": ["Sharp", "Pressure-like"],
    "location": ["Left chest", "Center chest"],
    "stress": ["Yes", "Yes"],
    "sob": ["No", "Yes"],
    "hypertension": ["Yes", "Yes"],
    "diabetes": ["No", "Yes"],
    "hyperlipidemia": ["Yes", "Yes"],
    "smoking": ["No", "Yes"],
    "probability": ["0.65", "0.92"],
}
df = pd.DataFrame(data)

# ----------------------------
# 5. Data cleaning
# ----------------------------
bool_cols = ["stress", "sob", "hypertension", "diabetes", "hyperlipidemia", "smoking"]
for col in bool_cols:
    df[col] = (
        df[col]
        .fillna(False)
        .map(
            {
                "Yes": True,
                "yes": True,
                "No": False,
                "no": False,
                True: True,
                False: False,
            }
        )
        .astype(bool)
    )

df["age"] = df["age"].fillna(0).astype(int)
df["probability"] = df["probability"].fillna(0).astype(float)


# ----------------------------
# 6. Seed function
# ----------------------------
def seed():
    db: Session = SessionLocal()
    try:
        patients = [
            Patient(
                name=row["name"],
                age=row["age"],
                gender=row["gender"],
                phone_number=row["phone_number"],
                pain_quality=row["pain_quality"],
                location=row["location"],
                stress=row["stress"],
                sob=row["sob"],
                hypertension=row["hypertension"],
                diabetes=row["diabetes"],
                hyperlipidemia=row["hyperlipidemia"],
                smoking=row["smoking"],
                probability=row["probability"],
            )
            for _, row in df.iterrows()
        ]
        db.add_all(patients)
        db.commit()
        print("✅ Seed data inserted into Supabase!")
    except Exception as e:
        db.rollback()
        print("❌ Error:", e)
    finally:
        db.close()


# ----------------------------
# 7. Run
# ----------------------------

seed()
