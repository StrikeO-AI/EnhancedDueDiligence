import os
from openai import OpenAI
import json
import random
from datetime import datetime

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Training scenarios based on AUSTRAC typologies
TRAINING_CATEGORIES = [
    "Transaction Monitoring",
    "Customer Due Diligence",
    "Suspicious Matter Reporting",
    "Risk Assessment",
    "Regulatory Reporting"
]

class TrainingModule:
    def __init__(self):
        self.current_scenario = None
        self.score = 0
        self.scenarios_completed = 0

    def generate_scenario(self, category=None):
        """Generate a new training scenario using OpenAI."""
        try:
            # Create prompt for scenario generation
            prompt = f"""Create a realistic AML/CTF compliance training scenario based on AUSTRAC typologies.
            If specified, focus on this category: {category if category else 'any category'}
            
            Format the response as JSON with the following structure:
            {{
                "scenario": "detailed description of the situation",
                "category": "compliance category",
                "red_flags": ["list of red flags to look for"],
                "question": "what action should be taken?",
                "options": ["4 possible actions to take"],
                "correct_answer": "index of correct option (0-3)",
                "explanation": "detailed explanation of why the correct answer is best"
            }}
            
            Base the scenario on real AUSTRAC typologies and compliance requirements."""

            # Call OpenAI API
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an AML/CTF compliance training expert."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )

            # Parse and store the scenario
            self.current_scenario = json.loads(response.choices[0].message.content)
            return self.current_scenario

        except Exception as e:
            return {
                "error": f"Failed to generate scenario: {str(e)}",
                "status": "error"
            }

    def evaluate_response(self, user_answer):
        """Evaluate user's response to the current scenario."""
        if not self.current_scenario:
            return {"error": "No active scenario", "status": "error"}

        correct = int(user_answer) == int(self.current_scenario['correct_answer'])
        self.scenarios_completed += 1
        if correct:
            self.score += 1

        return {
            "correct": correct,
            "explanation": self.current_scenario['explanation'],
            "score": self.score,
            "total": self.scenarios_completed,
            "status": "success"
        }

    def get_progress(self):
        """Get current training progress."""
        return {
            "score": self.score,
            "completed": self.scenarios_completed,
            "percentage": (self.score / self.scenarios_completed * 100) if self.scenarios_completed > 0 else 0
        }

    def analyze_performance(self):
        """Generate performance analysis and recommendations."""
        try:
            progress = self.get_progress()
            
            prompt = f"""Based on this training performance data:
            - Score: {progress['score']} correct out of {progress['completed']} scenarios
            - Success Rate: {progress['percentage']}%

            Provide a brief analysis and recommendations for improvement.
            Format as JSON with:
            {{
                "performance_level": "Excellent/Good/Needs Improvement",
                "analysis": "brief analysis of performance",
                "recommendations": ["list of specific recommendations"],
                "focus_areas": ["suggested areas to focus on"]
            }}"""

            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a compliance training assessment expert."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )

            return json.loads(response.choices[0].message.content)

        except Exception as e:
            return {
                "error": f"Failed to analyze performance: {str(e)}",
                "status": "error"
            }
