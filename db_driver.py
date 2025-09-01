import sqlite3
from typing import Optional
from dataclasses import dataclass
from contextlib import contextmanager


@dataclass
class Patient:
    id: str
    age: int
    name: str
    gender: str
    phone_number: str
    pain_quality: str
    location: str
    stress: bool
    sob: bool
    hypertension: bool
    hyperlipidemia: bool
    diabetes: bool
    smoking: bool
    probability: int


class DatabaseDriver:
    def __init__(self, db_path: str = "auto_db.sqlite"):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Create cars table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS patients (
                    id SERIAL PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    name VARCHAR(100),
                    gender VARCHAR(100),
                    age TEXT NOT NULL,
                    phone_number VARCHAR(100),
                    pain_quality TEXT NOT NULL,
                    location TEXT NOT NULL,
                    stress BOOLEAN NOT NULL,
                    sob BOOLEAN NOT NULL,
                    hypertension BOOLEAN NOT NULL,
                    diabetes BOOLEAN NOT NULL,
                    hyperlipidemia BOOLEAN NOT NULL,
                    smoking BOOLEAN NOT NULL,
                    probability INTEGER 
                )
            """
            )
            conn.commit()

    def create_patient(
        self,
        name,
        gender,
        age,
        pain_quality,
        location,
        stress,
        sob,
        hypertension,
        diabetes,
        hyperlipidemia,
        smoking,
        probability,
    ) -> Patient:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
    INSERT INTO patients (
        name, gender, age, pain_quality, location, stress, sob, hypertension, diabetes, hyperlipidemia, smoking, probability
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
                (
                    name,
                    gender,
                    age,
                    pain_quality,
                    location,
                    stress,
                    sob,
                    hypertension,
                    diabetes,
                    hyperlipidemia,
                    smoking,
                    probability,
                ),
            )
            conn.commit()
            return Patient(
                name,
                gender,
                age,
                pain_quality,
                location,
                stress,
                sob,
                hypertension,
                diabetes,
                hyperlipidemia,
                smoking,
                probability,
            )

    def get_patients(self) -> Optional[Patient]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM patients")
            rows = cursor.fetchall()
            return rows
