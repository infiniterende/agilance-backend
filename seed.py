from models import Patient
from sqlalchemy import create_engine, MetaData, Index, Table
from sqlalchemy.orm import sessionmaker
import os
import pandas as pd

from db import engine, Base, SessionLocal

from dotenv import load_dotenv

from pathlib import Path

dotenv_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=dotenv_path)
DATABASE_URL = os.getenv("SUPABASE_DATABASE_URL")

print(DATABASE_URL)
# engine = create_engine(DATABASE_URL)


Base.metadata.create_all(bind=engine)
# Drop the index if it exists
# Drop all tables
# Base.metadata.drop_all(bind=engine)

# Reflect all tables
# Load and insert CSV data
df = pd.read_csv("clean_patients.csv")


# Convert 'Yes'/'No' strings to booleans
for col in ["stress", "sob", "hypertension", "diabetes", "hyperlipidemia", "smoking"]:
    df[col] = df[col].fillna(False)  # or True depending on your app
    df[col] = df[col].astype(bool)  # cast to actual boolean type
    # df[col] = df[col].map({"Yes": True, "yes": True, "no": False, "No": False})

for col in ["age", "probability"]:
    df["age"] = df["age"].fillna(0).astype(int)
    df["probability"] = df["probability"].fillna(0).astype(int)
# Insert rows into the database
# for _, row in df.iterrows():
#     patient = Patient(
#         name=row["name"],
#         age=row["age"],
#         gender=row["gender"],
#         phone_number=row["phone_number"],
#         pain_quality=row["pain_quality"],
#         location=row["location"],
#         stress=row["stress"],
#         sob=row["sob"],
#         hypertension=row["hypertension"],
#         diabetes=row["diabetes"],
#         hyperlipidemia=row["hyperlipidemia"],
#         smoking=row["smoking"],
#         probability=row["probability"],
#     )
#     print(patient.name)
#     session.add(patient)

# session.commit()


def seed():
    db: Session = SessionLocal()
    for _, row in df.iterrows():
        patient = Patient(
            name=row["name"],
            age=row["age"],
            gender=row["gender"],
            phone_number=row["phone_number"],
            pain_quality=row["pain_quality"],
            location=row["location"],
            stress=row["stress"],
            sob=row["sob"],
            hypertension=row["hypertension"],
            hyperlipidemia=row["hyperlipidemia"],
            diabetes=row["diabetes"],
            smoking=row["smoking"],
            probability=row["probability"],
        )
        print(patient.probability)
        db.add(patient)
        db.commit()
    db.close()
    print("✅ Seed data inserted into Supabase!")


seed()
