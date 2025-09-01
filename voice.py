# Backend: Python Flask API with OpenAI Whisper
# app.py

from flask import Flask, request, jsonify
from flask_cors import CORS
import whisper
import tempfile
import os
import re
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Load Whisper model (you can use different sizes: tiny, base, small, medium, large)
# For production, consider using the larger models for better accuracy
model = whisper.load_model("base")


class ChestPainTriageSystem:
    def __init__(self):
        self.risk_factors = {
            "crushing": 3,
            "pressure": 3,
            "elephant": 3,
            "radiating": 2,
            "shortness": 2,
            "sweating": 2,
            "diaphoresis": 2,
            "nausea": 1,
            "heart_disease": 3,
            "diabetes": 2,
            "smoking": 1,
            "severe_pain": 2,
            "worst_pain": 3,
            "dying": 3,
            "arm_pain": 2,
            "jaw_pain": 2,
            "back_pain": 1,
        }

        self.questions = [
            "Can you describe your chest pain? Is it sharp, crushing, burning, or pressure-like?",
            "When did the pain start? Is it constant or does it come and go?",
            "On a scale of 1 to 10, how severe is your pain?",
            "Do you have any shortness of breath, nausea, sweating, or pain radiating to your arm, jaw, or back?",
            "Do you have any history of heart disease, diabetes, high blood pressure, or smoking?",
            "Are you currently taking any medications, especially heart medications?",
            "Have you had similar episodes before? If so, what happened?",
            "Are you experiencing any dizziness, lightheadedness, or feeling faint?",
        ]

        self.emergency_keywords = [
            r"can\'?t breathe|cannot breathe|difficulty breathing",
            r"worst pain|never felt pain like this|most severe",
            r"think I\'?m dying|feel like I\'?m dying|going to die",
            r"crushing|elephant on chest|heavy weight",
            r"heart attack|having a heart attack",
            r"chest tightness with sweating",
            r"pain down.*arm|arm pain with chest|jaw pain with chest",
        ]

        self.medical_patterns = {
            "crushing_pain": r"crushing|elephant|heavy pressure|weight on chest|vice",
            "pressure_pain": r"pressure|tight|squeezing|band around chest|constricting",
            "radiating_pain": r"radiating|spreading|arm pain|jaw pain|back pain|left arm|shoulder pain",
            "associated_symptoms": r"short of breath|can\'?t breathe|breathing difficulty|dyspnea",
            "autonomic_symptoms": r"sweating|diaphoresis|clammy|cold sweat|nausea|vomiting",
            "cardiac_history": r"heart disease|cardiac|coronary|heart attack|myocardial|angina|stent|bypass",
            "risk_factors": r"diabetes|diabetic|smoking|high blood pressure|hypertension",
            "severity_high": r"10.*10|worst pain|unbearable|excruciating|severe",
            "duration": r"(\d+)\s*(minute|hour|day)s?\s*ago|started\s*(\d+)",
        }

    def analyze_transcript(
        self, transcript: str, conversation_context: Dict = None
    ) -> Dict:
        """Analyze the patient's transcript for medical risk factors"""
        transcript_lower = transcript.lower()
        risk_score = 0
        detected_factors = []

        # Check for emergency keywords first
        for pattern in self.emergency_keywords:
            if re.search(pattern, transcript_lower):
                return {
                    "risk_score": 10,
                    "risk_level": "emergency",
                    "is_emergency": True,
                    "detected_factors": ["emergency_keywords"],
                    "recommendation": "EMERGENCY: Call 911 immediately or go to the nearest emergency room. Do not drive yourself.",
                }

        # Analyze medical patterns
        for factor, pattern in self.medical_patterns.items():
            if re.search(pattern, transcript_lower):
                if factor == "crushing_pain":
                    risk_score += self.risk_factors["crushing"]
                    detected_factors.append("crushing chest pain")
                elif factor == "pressure_pain":
                    risk_score += self.risk_factors["pressure"]
                    detected_factors.append("pressure-type chest pain")
                elif factor == "radiating_pain":
                    risk_score += self.risk_factors["radiating"]
                    detected_factors.append("radiating pain")
                elif factor == "associated_symptoms":
                    risk_score += self.risk_factors["shortness"]
                    detected_factors.append("breathing difficulty")
                elif factor == "autonomic_symptoms":
                    risk_score += self.risk_factors["sweating"]
                    detected_factors.append("associated symptoms")
                elif factor == "cardiac_history":
                    risk_score += self.risk_factors["heart_disease"]
                    detected_factors.append("cardiac history")
                elif factor == "risk_factors":
                    risk_score += self.risk_factors["diabetes"]
                    detected_factors.append("cardiovascular risk factors")
                elif factor == "severity_high":
                    risk_score += self.risk_factors["severe_pain"]
                    detected_factors.append("severe pain")

        # Extract pain severity score if mentioned
        severity_match = re.search(r"(\d+)\s*(?:out of|/|\s)\s*10", transcript_lower)
        if severity_match:
            severity = int(severity_match.group(1))
            if severity >= 8:
                risk_score += 3
                detected_factors.append(f"severe pain ({severity}/10)")
            elif severity >= 6:
                risk_score += 2
                detected_factors.append(f"moderate-severe pain ({severity}/10)")

        # Determine risk level
        if risk_score >= 6:
            risk_level = "emergency"
            is_emergency = True
        elif risk_score >= 4:
            risk_level = "high"
            is_emergency = False
        elif risk_score >= 2:
            risk_level = "medium"
            is_emergency = False
        else:
            risk_level = "low"
            is_emergency = False

        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "is_emergency": is_emergency,
            "detected_factors": detected_factors,
        }

    def get_recommendation(self, analysis: Dict, question_count: int) -> str:
        """Generate appropriate medical recommendation based on risk analysis"""
        risk_level = analysis["risk_level"]

        if risk_level == "emergency":
            return "Based on your symptoms, this appears to be a medical emergency. Call 911 immediately or have someone drive you to the nearest emergency room. Do not drive yourself. Time is critical for heart attacks."

        elif risk_level == "high":
            return "Your symptoms are concerning and suggest you should seek immediate medical attention. Please go to an emergency room or call 911 if symptoms worsen. Do not wait - chest pain with these characteristics needs urgent evaluation."

        elif risk_level == "medium":
            return "Your symptoms warrant prompt medical evaluation. Please contact your doctor immediately or visit an urgent care center within the next 2-4 hours. If symptoms worsen or you develop new symptoms, go to the emergency room."

        else:  # low risk
            if question_count < 3:
                return "Thank you for that information. While your symptoms may be lower risk, chest pain should always be evaluated by a healthcare professional. Let me ask a few more questions to better assess your situation."
            else:
                return "Based on our discussion, your symptoms appear to be lower risk, but chest pain should still be evaluated by a healthcare professional. Please schedule an appointment with your primary care doctor within the next day or two. If symptoms worsen, seek immediate care."

    def get_next_question(self, question_count: int, analysis: Dict) -> Optional[str]:
        """Get the next appropriate question based on current assessment"""
        if analysis["is_emergency"] or question_count >= len(self.questions):
            return None

        return self.questions[question_count]


# Initialize triage system
triage_system = ChestPainTriageSystem()


@app.route("/api/triage", methods=["POST"])
def process_triage():
    try:
        # Check if audio file is present
        if "audio" not in request.files:
            return jsonify({"error": "No audio file provided"}), 400

        audio_file = request.files["audio"]
        conversation_context = json.loads(
            request.form.get("conversation_context", "{}")
        )

        # Save audio file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_file:
            audio_file.save(temp_file.name)
            temp_filename = temp_file.name

        try:
            # Transcribe with Whisper
            logger.info("Starting Whisper transcription...")
            result = model.transcribe(
                temp_filename,
                language="en",
                prompt="Medical consultation about chest pain symptoms. Patient describing symptoms to healthcare provider.",
                temperature=0.0,  # Lower temperature for more consistent results
            )

            transcript = result["text"].strip()
            logger.info(f"Transcription completed: {transcript[:100]}...")

            if not transcript:
                return jsonify({"error": "No speech detected in audio"}), 400

            # Analyze the transcript for medical risk factors
            analysis = triage_system.analyze_transcript(
                transcript, conversation_context
            )

            # Count previous questions asked
            messages = conversation_context.get("messages", [])
            question_count = len(
                [msg for msg in messages if msg.get("sender") == "agent"]
            )

            # Get recommendation
            recommendation = triage_system.get_recommendation(analysis, question_count)

            # Get next question if appropriate
            next_question = triage_system.get_next_question(question_count, analysis)

            # Prepare response
            response = {
                "transcript": transcript,
                "risk_score": analysis["risk_score"],
                "risk_level": analysis["risk_level"],
                "recommendation": recommendation,
                "is_emergency": analysis["is_emergency"],
                "detected_factors": analysis["detected_factors"],
                "next_question": next_question,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(
                f"Analysis complete - Risk: {analysis['risk_level']}, Score: {analysis['risk_score']}"
            )
            return jsonify(response)

        finally:
            # Clean up temporary file
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    except Exception as e:
        logger.error(f"Error processing triage request: {str(e)}")
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify(
        {
            "status": "healthy",
            "model": "whisper-base",
            "timestamp": datetime.now().isoformat(),
        }
    )


@app.route("/api/questions", methods=["GET"])
def get_questions():
    """Get all triage questions"""
    return jsonify(
        {
            "questions": triage_system.questions,
            "total_questions": len(triage_system.questions),
        }
    )


if __name__ == "__main__":
    # In production, use a proper WSGI server like gunicorn
    app.run(debug=True, host="0.0.0.0", port=5000)
