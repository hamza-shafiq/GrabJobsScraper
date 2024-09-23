import os
import json
from scrape import Scraper
from utils.resume_parser import PDFParser
from utils.openai_service import OpenAIHelper


if __name__ == '__main__':

    applicants_data = []

    for file_name in os.listdir('./static/resume'):
        if file_name.endswith('.pdf'):
            resume_parser = PDFParser(file_name=f"static/resume/{file_name}")
            resume_data = resume_parser.extract_text()

            openai_helper = OpenAIHelper()
            ai_response = openai_helper.get_ai_response(resume_data)

            applicant_data = json.loads(ai_response)
            applicants_data.append(applicant_data)
    
    with open('static/applicants.json', 'w') as json_file:
        json.dump(applicants_data, json_file, indent=4)

    data = Scraper().extract_questions()
    print(data)
    with open('applicants.json', 'r') as file:
        demo_json = json.load(file)

    Scraper().fill_job(demo_json)
