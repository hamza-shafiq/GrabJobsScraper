from scrape import Scraper
import json


if __name__ == '__main__':
    data = Scraper().extract_questions()
    print(data)
    with open('applicants.json', 'r') as file:
        demo_json = json.load(file)

    Scraper().fill_job(demo_json)
