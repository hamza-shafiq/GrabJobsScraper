import os
import openai
from dotenv import load_dotenv

load_dotenv()

class OpenAIHelper:

    def __init__(self):
        self.openai_model = os.getenv("OPENAI_MODEL")
    
    def _get_system_prompt(self):
        return """
        You are an AI assistant responsible for helping users fill out job application forms based on their resumes.
        """
    
    def _get_prompt(self, resume: str):
        return f"""
            You will be provided with a resume and you have to fill in the form privded in json form containing questions.

            Your task is to extract relevant information from the resume to answer the form's questions. If the information is not available in the resume, generate a generic, reasonable response.

            Use the following rules:
            1. If the resume contains specific information for a question, use that information.
            2. If no information is found in the resume, provide an empty string for personal details like middle name or phone number, or generate a general response for other questions.
            3. Ensure that you never leave any field empty, except when dealing with personal information that the resume does not provide.

            The format should be a JSON object like this:

            
                "title": "<job title>",
                "Location of Residence and Language:": "<city and country>",
                "question": 
                    "First Name*": "<First Name>",
                    "Last Name*": "<Last Name>",
                    "Email*": "<Email>",
                    "Middle Name": "<Middle Name or ''>",
                    "Address*": "<Address or ''>",
                    "City*": "<City or ''>",
                    "State/Province*": "<State or ''>",
                    "Country*": "<Country>",
                    "Zip/Postal Code": "<Zip Code or ''>",
                    "Primary Phone*": "<Phone Number or ''>",
                    "How did you find out about this opportunity?*": "<How did you hear about this opportunity>",
                    "Employee Name, if employee referral": "<Employee Name or ''>",
                    "Are you legally authorized to work in the country where the position is located?": "Yes or No",
                    "Can you after receipt of an employment offer, present documents that show you have a right to lawfully work for Logitech in the country where position is located?": "Yes or No",
                    "Have you been previously employed with Logitech?": "Yes or No",
                    "Please include your dates of employment and previous manager.": "<Employment Details or ''>",
                    "What are your compensation expectations?": "<Compensation expectations>"
                
            The JSON should be well-structured and contain no missing fields.

            Resume:
            {resume}
        """
    
    def get_ai_response(self, resume):

        messages = [
            {
                "role": "system",
                "content": self._get_system_prompt()
            },             
            {
                "role": "user",
                "content": self._get_prompt(resume)
            }
        ]

        response = openai.chat.completions.create(
            model=self.openai_model,
            messages=messages,
            response_format={"type": "json_object"}
        )

        return response.choices[0].message.content
