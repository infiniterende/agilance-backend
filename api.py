# from livekit.agents import llm
# import enum
# from typing import Annotated
# import logging
# from db_driver import DatabaseDriver
# from typing import List, Optional, Dict, Any

# logger = logging.getLogger("user-data")
# logger.setLevel(logging.INFO)

# DB = DatabaseDriver()


# class ChestPainTriageSystem:
#     def __init__(self):
#         self.risk_factors = {
#             "crushing": 3,
#             "pressure": 3,
#             "elephant": 3,
#             "radiating": 2,
#             "shortness": 2,
#             "sweating": 2,
#             "diaphoresis": 2,
#             "nausea": 1,
#             "heart_disease": 3,
#             "diabetes": 2,
#             "smoking": 1,
#             "severe_pain": 2,
#             "worst_pain": 3,
#             "dying": 3,
#             "arm_pain": 2,
#             "jaw_pain": 2,
#             "back_pain": 1,
#         }

#         self.questions = [
#             "How old are you?",
#             "Are you male or female?",
#             "Can you describe your chest pain? Is it sharp, crushing, burning, squeezing or pressure-like?",
#             "Where is the pain located?  Is it center of left side of chest, possibly spreading to your arm, neck, jaw, or back?",
#             "Does the pain come on with physical activity or emotional stress? For example when climbing stiars or walking uphill?",
#             "Does it go away with rest or nitroglycerin?",
#             "When did the pain start? Is it constant or does it come and go?",
#             "On a scale of 1 to 10, how severe is your pain?",
#             "Do you have any shortness of breath, nausea, sweating, or pain radiating to your arm, jaw, or back?",
#             "Do you have any history of heart disease, diabetes, high blood pressure, or smoking?",
#             "Are you currently taking any medications, especially heart medications?",
#             "Have you had similar episodes before? If so, what happened?",
#             "Are you experiencing any dizziness, lightheadedness, or feeling faint?",
#         ]

#         self.emergency_keywords = [
#             r"can\'?t breathe|cannot breathe|difficulty breathing",
#             r"worst pain|never felt pain like this|most severe",
#             r"think I\'?m dying|feel like I\'?m dying|going to die",
#             r"crushing|elephant on chest|heavy weight",
#             r"heart attack|having a heart attack",
#             r"chest tightness with sweating",
#             r"pain down.*arm|arm pain with chest|jaw pain with chest",
#         ]

#         self.medical_patterns = {
#             "location": r"crushing|elephant|heavy pressure|weight on chest|vice|pressure|tight|squeezing|band around chest|constricting|radiating|spreading|arm pain|jaw pain|back pain|left arm|shoulder pain|center of my chest|middle of my chest|left side of my chest|pressure|squeezing|tightness|heavy|",
#             "trigger": r"exercise|climbing|stairs|hurry|uphill|physical activity|stress|anxiety",
#             "relief": r"rest|stop|nitro|nitroglycerin|goes away in a few minutes|better after resting",
#             "associated_symptoms": r"short of breath|can\'?t breathe|breathing difficulty|dyspnea",
#             "autonomic_symptoms": r"sweating|diaphoresis|clammy|cold sweat|nausea|vomiting",
#             "cardiac_history": r"heart disease|cardiac|coronary|heart attack|myocardial|angina|stent|bypass",
#             "risk_factors": r"diabetes|diabetic|smoking|high blood pressure|hypertension",
#             "severity_high": r"10.*10|worst pain|unbearable|excruciating|severe",
#             "duration": r"(\d+)\s*(minute|hour|day)s?\s*ago|started\s*(\d+)",
#         }

#     def analyze_transcript(
#         self, transcript: str, conversation_context: Dict = None
#     ) -> Dict:
#         """Analyze the patient's transcript for medical risk factors"""
#         transcript_lower = transcript.lower()
#         risk_score = 0
#         detected_factors = []

#         # Check for emergency keywords first
#         for pattern in self.emergency_keywords:
#             if re.search(pattern, transcript_lower):
#                 return {
#                     "risk_score": 10,
#                     "risk_level": "emergency",
#                     "is_emergency": True,
#                     "detected_factors": ["emergency_keywords"],
#                     "recommendation": "EMERGENCY: Call 911 immediately or go to the nearest emergency room. Do not drive yourself.",
#                 }

#         # Analyze medical patterns

#         for factor, pattern in self.medical_patterns.items():
#             if re.search(pattern, transcript_lower):
#                 if factor == "location":
#                     risk_score += self.risk_factors["crushing"]
#                     detected_factors.append("crushing chest pain")
#                 elif factor == "pressure_pain":
#                     risk_score += self.risk_factors["pressure"]
#                     detected_factors.append("pressure-type chest pain")
#                 elif factor == "radiating_pain":
#                     risk_score += self.risk_factors["radiating"]
#                     detected_factors.append("radiating pain")
#                 elif factor == "associated_symptoms":
#                     risk_score += self.risk_factors["shortness"]
#                     detected_factors.append("breathing difficulty")
#                 elif factor == "autonomic_symptoms":
#                     risk_score += self.risk_factors["sweating"]
#                     detected_factors.append("associated symptoms")
#                 elif factor == "cardiac_history":
#                     risk_score += self.risk_factors["heart_disease"]
#                     detected_factors.append("cardiac history")
#                 elif factor == "risk_factors":
#                     risk_score += self.risk_factors["diabetes"]
#                     detected_factors.append("cardiovascular risk factors")
#                 elif factor == "severity_high":
#                     risk_score += self.risk_factors["severe_pain"]
#                     detected_factors.append("severe pain")

#         # Extract pain severity score if mentioned
#         severity_match = re.search(r"(\d+)\s*(?:out of|/|\s)\s*10", transcript_lower)
#         if severity_match:
#             severity = int(severity_match.group(1))
#             if severity >= 8:
#                 risk_score += 3
#                 detected_factors.append(f"severe pain ({severity}/10)")
#             elif severity >= 6:
#                 risk_score += 2
#                 detected_factors.append(f"moderate-severe pain ({severity}/10)")

#         # Determine risk level
#         if risk_score >= 6:
#             risk_level = "emergency"
#             is_emergency = True
#         elif risk_score >= 4:
#             risk_level = "high"
#             is_emergency = False
#         elif risk_score >= 2:
#             risk_level = "medium"
#             is_emergency = False
#         else:
#             risk_level = "low"
#             is_emergency = False

#         return {
#             "risk_score": risk_score,
#             "risk_level": risk_level,
#             "is_emergency": is_emergency,
#             "detected_factors": detected_factors,
#         }

#     def get_recommendation(self, analysis: Dict, question_count: int) -> str:
#         """Generate appropriate medical recommendation based on risk analysis"""
#         risk_level = analysis["risk_level"]

#         if risk_level == "emergency":
#             return "Based on your symptoms, this appears to be a medical emergency. Call 911 immediately or have someone drive you to the nearest emergency room. Do not drive yourself. Time is critical for heart attacks."

#         elif risk_level == "high":
#             return "Your symptoms are concerning and suggest you should seek immediate medical attention. Please go to an emergency room or call 911 if symptoms worsen. Do not wait - chest pain with these characteristics needs urgent evaluation."

#         elif risk_level == "medium":
#             return "Your symptoms warrant prompt medical evaluation. Please contact your doctor immediately or visit an urgent care center within the next 2-4 hours. If symptoms worsen or you develop new symptoms, go to the emergency room."

#         else:  # low risk
#             if question_count < 3:
#                 return "Thank you for that information. While your symptoms may be lower risk, chest pain should always be evaluated by a healthcare professional. Let me ask a few more questions to better assess your situation."
#             else:
#                 return "Based on our discussion, your symptoms appear to be lower risk, but chest pain should still be evaluated by a healthcare professional. Please schedule an appointment with your primary care doctor within the next day or two. If symptoms worsen, seek immediate care."

#     def get_next_question(self, question_count: int, analysis: Dict) -> Optional[str]:
#         """Get the next appropriate question based on current assessment"""
#         if analysis["is_emergency"] or question_count >= len(self.questions):
#             return None

#         return self.questions[question_count]


# # Initialize triage system
# triage_system = ChestPainTriageSystem()


# class AssistantFnc(llm.FunctionContext):
#     def __init__(self):
#         super().__init__()

#         self._patient_details = {
#             "age": 0,
#             "name": "",
#             "gender": "",
#             "phone_number": "",
#             "pain_quality": "",
#             "location": "",
#             "stress": False,
#             "sob": False,
#             "hypertension": False,
#             "hyperlipidemia": False,
#             "diabetes": False,
#             "smoking": False,
#         }

#     def get_patient_details_str(self):
#         patient_str = ""
#         for key, value in self.patient_details.items():
#             patient_str += f"{key}: {value}\n"

#         return patient_str

#     @llm.ai_callable(
#         description="get a description of patient's chest pain and relevant medical history and details"
#     )
#     def create_patient(
#         self,
#         age: Annotated[int, llm.TypeInfo(description="The age of the patient")],
#         name: Annotated[str, llm.TypeInfo(description="The name of theh patient")],
#         gender: Annotated[str, llm.TypeInfo(description="The gender of the patient")],
#         phone_number: Annotated[
#             str, llm.TypeInfo(description="The phone number of the patient")
#         ],
#         pain_quality: Annotated[
#             str, llm.TypeInfo(description="The chest pain quality")
#         ],
#         location: Annotated[
#             str, llm.TypeInfo(description="The location of chest pain")
#         ],
#         stress: Annotated[
#             bool,
#             llm.TypeInfo(
#                 description="check whether the patient under emotional stress"
#             ),
#         ],
#         sob: Annotated[
#             bool,
#             llm.TypeInfo(
#                 description="check whether the patient has shortness of breath"
#             ),
#         ],
#         hypertension: Annotated[
#             bool,
#             llm.TypeInfo(description="check whether the patient has hypertension"),
#         ],
#         hyperlipidemia: Annotated[
#             bool,
#             llm.TypeInfo(description="check whether the patient has hyperlipidemia"),
#         ],
#         diabetes: Annotated[
#             bool,
#             llm.TypeInfo(description="check whether the patient has diabetes"),
#         ],
#         smoking: Annotated[
#             bool,
#             llm.TypeInfo(description="check whether the patient smokes"),
#         ],
#     ):
#         logger.info(
#             "create patient - name: %s, phone_number: %s,age: %s",
#             name,
#             phone_number,
#             age,
#         )
#         result = DB.create_patient(
#             name,
#             gender,
#             age,
#             pain_quality,
#             location,
#             stress,
#             sob,
#             hypertension,
#             diabetes,
#             hyperlipidemia,
#             smoking,
#         )
#         if result is None:
#             return "Failed to create patient"

#         self._patient_details = {
#             age: result.age,
#             name: result.name,
#             gender: result.gender,
#             phone_number: result.phone_number,
#             pain_quality: result.pain_quality,
#             location: result.location,
#             stress: result.stress,
#             sob: result.sob,
#             hypertension: result.hypertension,
#             hyperlipidemia: result.hyperlipidemia,
#             diabetes: result.diabetes,
#             smoking: result.smoking,
#         }

#         return "patient created!"

from livekit.agents import llm
import enum
from typing import Annotated
import logging
from db_driver import DatabaseDriver

logger = logging.getLogger("user-data")
logger.setLevel(logging.INFO)

DB = DatabaseDriver()


class CarDetails(enum.Enum):
    VIN = "vin"
    Make = "make"
    Model = "model"
    Year = "year"


class AssistantFnc(llm.FunctionContext):
    def __init__(self):
        super().__init__()

        self._car_details = {
            CarDetails.VIN: "",
            CarDetails.Make: "",
            CarDetails.Model: "",
            CarDetails.Year: "",
        }

    def get_car_str(self):
        car_str = ""
        for key, value in self._car_details.items():
            car_str += f"{key}: {value}\n"

        return car_str

    @llm.ai_callable(description="lookup a car by its vin")
    def lookup_car(
        self,
        vin: Annotated[str, llm.TypeInfo(description="The vin of the car to lookup")],
    ):
        logger.info("lookup car - vin: %s", vin)

        result = DB.get_car_by_vin(vin)
        if result is None:
            return "Car not found"

        self._car_details = {
            CarDetails.VIN: result.vin,
            CarDetails.Make: result.make,
            CarDetails.Model: result.model,
            CarDetails.Year: result.year,
        }

        return f"The car details are: {self.get_car_str()}"

    @llm.ai_callable(description="get the details of the current car")
    def get_car_details(self):
        logger.info("get car  details")
        return f"The car details are: {self.get_car_str()}"

    @llm.ai_callable(description="create a new car")
    def create_car(
        self,
        vin: Annotated[str, llm.TypeInfo(description="The vin of the car")],
        make: Annotated[str, llm.TypeInfo(description="The make of the car ")],
        model: Annotated[str, llm.TypeInfo(description="The model of the car")],
        year: Annotated[int, llm.TypeInfo(description="The year of the car")],
    ):
        logger.info(
            "create car - vin: %s, make: %s, model: %s, year: %s",
            vin,
            make,
            model,
            year,
        )
        result = DB.create_car(vin, make, model, year)
        if result is None:
            return "Failed to create car"

        self._car_details = {
            CarDetails.VIN: result.vin,
            CarDetails.Make: result.make,
            CarDetails.Model: result.model,
            CarDetails.Year: result.year,
        }

        return "car created!"

    def has_car(self):
        return self._car_details[CarDetails.VIN] != ""
