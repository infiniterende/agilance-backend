from sqlalchemy.orm import Session
from livekit.agents import llm
from typing import Annotated
from models import Patient
from db_driver import DatabaseDriver

from db import SessionLocal

DB = DatabaseDriver()

from calculate_cad_score import cadc_clinical_risk


class AssistantFnc(llm.FunctionContext):
    def __init__(self):
        super().__init__()
        self._patient_details = {
            "age": None,
            "name": None,
            "gender": None,
            "phone_number": None,
            "pain_quality": None,
            "location": None,
            "stress": None,
            "sob": None,
            "hypertension": None,
            "hyperlipidemia": None,
            "diabetes": None,
            "smoking": None,
            "probability": 0,
        }

    @llm.ai_callable(
        description="Extract structured patient data from a free-form transcript"
    )
    def extract_patient_data(self, transcript: str) -> dict:
        """
        Uses the LLM to parse the transcript into structured patient info.
        Returns a dictionary matching the Patient model.
        """
        prompt = f"""
        You are a medical assistant. Extract the following patient information from the transcript:

        Fields:
        - name
        - age
        - gender 
        - phone_number
        - pain_quality
        - location (True/False) True if substernal else False
        - stress (True/False)
        - sob (True/False)
        - hypertension (True/False)
        - hyperlipidemia (True/False)
        - diabetes (True/False)
        - smoking (True/False)
        - probability (float)

        Transcript:
        {transcript}

        Output JSON with keys exactly as listed above.
        """
        response = llm.openai.Completion.create(
            prompt=prompt,
            temperature=0,
            max_tokens=300,
        )

        # Parse LLM output as JSON
        import json

        try:
            data = json.loads(response.choices[0].text)
            print(data)
        except Exception as e:
            data = {}
            print("Failed to parse LLM response:", e)

        return data

    @llm.ai_callable(
        description="Create and save a patient record with chest pain and medical history"
    )
    def create_patient(
        self,
        name,
        gender,
        age,
        phone_number,
        pain_quality,
        location,
        stress,
        sob,
        hypertension,
        hyperlipidemia,
        diabetes,
        smoking,
    ):
        db = SessionLocal()

        male = 1 if gender == "male" else 0

        risk_probability = cadc_clinical_risk(
            age,
            male=male,
            chest_pain_type=classify_chest_pain(
                location,
                trigger,
                relief,
            ),
            diabetes=diabetes,
            hypertension=hypertension,
            dyslipidaemia=hyperlipidemia,
            smoking=smoking,
        )

        print(risk_probability)
        try:
            patient = Patient(
                name=name,
                gender=gender,
                age=age,
                phone_number=phone_number,
                pain_quality=pain_quality,
                location=location,
                stress=stress,
                sob=sob,
                hypertension=hypertension,
                hyperlipidemia=hyperlipidemia,
                diabetes=diabetes,
                smoking=smoking,
                probability=int(risk_probability * 100),
            )
            db.add(patient)
            db.commit()
            db.refresh(patient)
            return f"✅ Patient {patient.name} (ID: {patient.id}) created successfully."
        except Exception as e:
            db.rollback()
            return f"❌ Failed to create patient: {str(e)}"
        finally:
            db.close()

    # class AssistantFnc(llm.FunctionContext):
    #     def __init__(self):
    #         super().__init__()

    @llm.ai_callable(
        description="Create and save a patient record with chest pain and medical history"
    )
    def create_patient(
        self,
        age: Annotated[int, llm.TypeInfo(description="The age of the patient")],
        name: Annotated[str, llm.TypeInfo(description="The name of the patient")],
        gender: Annotated[str, llm.TypeInfo(description="The gender of the patient")],
        phone_number: Annotated[
            str, llm.TypeInfo(description="The phone number of the patient")
        ],
        pain_quality: Annotated[
            str, llm.TypeInfo(description="The chest pain quality")
        ],
        location: Annotated[
            str, llm.TypeInfo(description="The location of chest pain")
        ],
        stress: Annotated[
            bool, llm.TypeInfo(description="Whether patient is under stress")
        ],
        sob: Annotated[
            bool, llm.TypeInfo(description="Whether patient has shortness of breath")
        ],
        hypertension: Annotated[
            bool, llm.TypeInfo(description="Whether patient has hypertension")
        ],
        hyperlipidemia: Annotated[
            bool, llm.TypeInfo(description="Whether patient has hyperlipidemia")
        ],
        diabetes: Annotated[
            bool, llm.TypeInfo(description="Whether patient has diabetes")
        ],
        smoking: Annotated[bool, llm.TypeInfo(description="Whether patient smokes")],
        probability: Annotated[
            int, llm.TypeInfo(description="Calculated CAD probability")
        ],
    ):
        db = SessionLocal()
        try:
            patient = Patient(
                name=name,
                gender=gender,
                age=age,
                phone_number=phone_number,
                pain_quality=pain_quality,
                location=location,
                stress=stress,
                sob=sob,
                hypertension=hypertension,
                hyperlipidemia=hyperlipidemia,
                diabetes=diabetes,
                smoking=smoking,
                probability=probability,
            )
            db.add(patient)
            db.commit()
            db.refresh(patient)
            return f"✅ Patient {patient.name} (ID: {patient.id}) created successfully."
        except Exception as e:
            db.rollback()
            return f"❌ Failed to create patient: {str(e)}"
        finally:
            db.close()


# from livekit.agents import llm
# import enum
# from typing import Annotated
# import logging
# from db import SessionLocal

# logger = logging.getLogger("user-data")
# logger.setLevel(logging.INFO)

# DB = SessionLocal()


# class CarDetails(enum.Enum):
#     VIN = "vin"
#     Make = "make"
#     Model = "model"
#     Year = "year"


# class AssistantFnc(llm.FunctionContext):
#     def __init__(self):
#         super().__init__()

#         self._car_details = {
#             CarDetails.VIN: "",
#             CarDetails.Make: "",
#             CarDetails.Model: "",
#             CarDetails.Year: "",
#         }

#     def get_car_str(self):
#         car_str = ""
#         for key, value in self._car_details.items():
#             car_str += f"{key}: {value}\n"

#         return car_str

#     @llm.ai_callable(description="lookup a car by its vin")
#     def lookup_car(
#         self,
#         vin: Annotated[str, llm.TypeInfo(description="The vin of the car to lookup")],
#     ):
#         logger.info("lookup car - vin: %s", vin)

#         result = DB.get_car_by_vin(vin)
#         if result is None:
#             return "Car not found"

#         self._car_details = {
#             CarDetails.VIN: result.vin,
#             CarDetails.Make: result.make,
#             CarDetails.Model: result.model,
#             CarDetails.Year: result.year,
#         }

#         return f"The car details are: {self.get_car_str()}"

#     @llm.ai_callable(description="get the details of the current car")
#     def get_car_details(self):
#         logger.info("get car  details")
#         return f"The car details are: {self.get_car_str()}"

#     @llm.ai_callable(description="create a new car")
#     def create_car(
#         self,
#         vin: Annotated[str, llm.TypeInfo(description="The vin of the car")],
#         make: Annotated[str, llm.TypeInfo(description="The make of the car ")],
#         model: Annotated[str, llm.TypeInfo(description="The model of the car")],
#         year: Annotated[int, llm.TypeInfo(description="The year of the car")],
#     ):
#         logger.info(
#             "create car - vin: %s, make: %s, model: %s, year: %s",
#             vin,
#             make,
#             model,
#             year,
#         )
#         result = DB.create_car(vin, make, model, year)
#         if result is None:
#             return "Failed to create car"

#         self._car_details = {
#             CarDetails.VIN: result.vin,
#             CarDetails.Make: result.make,
#             CarDetails.Model: result.model,
#             CarDetails.Year: result.year,
#         }

#         return "car created!"

#     def has_car(self):
#         return self._car_details[CarDetails.VIN] != ""
