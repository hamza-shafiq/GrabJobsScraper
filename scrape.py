import os
import json
import time

from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

job_links = [
    "https://jobs.jobvite.com/logitech/job/o6Hsufwt",
    "https://jobs.jobvite.com/logitech/job/oTCtufwc"
]


class Scraper:
    def __init__(self):
        self.driver = self.get_chrome_browser()

    def get_chrome_browser(self):
        """
        Initializes and returns a headless Chrome browser with specific options
        and potentially a proxy.

        Args:
          proxy (str, optional): A string representing the proxy server to be
            used. If not provided, no proxy will be used.

        Returns:
          Returns a webdriver.Chrome instance with the specified options and
          potentially a proxy.
        """
        options = webdriver.ChromeOptions()
        service = Service(ChromeDriverManager().install())
        service.start()

        driver = webdriver.Chrome(service=service, options=options)
        return driver

    @staticmethod
    def scroll_to_element(driver, element):
        """Scrolls the web page until the element is in view."""
        driver.execute_script("arguments[0].scrollIntoView();", element)

    def select_country(self, country, is_extract=False):

        """Selects a country from the dropdown."""
        self.driver.find_element(By.ID, "jv-country-select").click()
        element = self.driver.find_element(By.XPATH, f"//option[contains(text(), '{country}')]")
        self.scroll_to_element(self.driver, element)
        element.click()
        time.sleep(2)
        if is_extract:
            options = self.driver.find_elements(By.TAG_NAME, "option")[1:]
            options_text = [option.text for option in options if option.text != "Select an option..."]
            return options_text

    def extract_questions(self):
        driver = self.driver
        all_questions = []

        for link in job_links:
            questions = {}

            try:
                driver.get(link)
                time.sleep(2)
            except:
                driver.refresh()
                time.sleep(2)

            questions["title"] = driver.find_element(By.CLASS_NAME, "jv-header").text
            logger.info(f"Start scrape questions for the job title: {questions['title']}")
            apply_btn = driver.find_element(By.CLASS_NAME, "jv-button-apply")
            apply_btn.click()
            label_for_country = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[for='jv-country-select']"))
            ).text
            driver.find_element(By.ID, "jv-country-select").click()
            questions[label_for_country] = self.select_country("Spain", is_extract=True)
            logger.info("Select Country: Spain")
            driver.find_element(By.CSS_SELECTOR, "[type='submit']").click()
            apply_page = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.CLASS_NAME, "jv-apply-step"))
            )
            if apply_page:
                logger.info("Start extracting question for job")
                questions["question"] = {}
                for each in driver.find_elements(By.CLASS_NAME, "jv-form-field"):
                    element = each.find_element(By.CLASS_NAME, "jv-form-field-label")
                    self.scroll_to_element(driver, element)
                    label = element.text

                    questions["question"][label] = None
                    try:
                        select_element = each.find_element(By.TAG_NAME, "select")
                        options = select_element.find_elements(By.TAG_NAME, "option")[1:]
                        options_text = [option.text for option in options if option.text != "Select an option..."]
                        questions["question"][label] = options_text
                    except NoSuchElementException:
                        pass

            all_questions.append(questions)
        logger.info("Successfully Fetched Questions")

        driver.quit()
        return all_questions

    def fill_job(self, answers_json):
        for link in job_links:
            try:
                self.driver.get(link)
                time.sleep(2)
            except:
                self.driver.refresh()
                time.sleep(2)

            job_title = self.driver.find_element(By.CLASS_NAME, "jv-header").text
            apply_btn = self.driver.find_element(By.CLASS_NAME, "jv-button-apply")
            apply_btn.click()
            country_select = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[for='jv-country-select']"))
            ).text
            job_data = next((job for job in answers_json if job['title'] == job_title), None)

            if not job_data:
                logger.error(f"No matching data found for job title: {job_title}")
                continue
            if country_select:
                self.select_country(job_data[country_select])
                self.driver.find_element(By.CSS_SELECTOR, "[type='submit']").click()
                apply_page = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "jv-apply-step"))
                )
                if apply_page:
                    logger.info("Start fill fields for apply job")
                    div_element = self.driver.find_element(By.ID, "attachResume")
                    div_element.find_element(By.TAG_NAME, "button").click()
                    file_input = self.driver.find_element(By.ID, "file-input-0")
                    file_path = os.path.abspath(f"static/resume/{job_data['question']['First Name*']} {job_data['question']['Last Name*']}.pdf")
                    file_input.send_keys(file_path)
                    file_save = WebDriverWait(self.driver, 10).until(
                        EC.invisibility_of_element_located((By.CLASS_NAME, "jv-spinner ng-hide"))
                    )
                    if file_save:
                        logger.info("Successfully upload resume")
                        time.sleep(5)
                        for each in self.driver.find_elements(By.CLASS_NAME, "jv-form-field"):
                            element = each.find_element(By.CLASS_NAME, "jv-form-field-label")
                            self.driver.execute_script("arguments[0].scrollIntoView();", element)
                            label = element.text
                            try:
                                select_element = each.find_element(By.TAG_NAME, "select")
                            
                                option_to_select = select_element.find_element(By.XPATH,
                                                                                f"//option[contains(text(), '{job_data.get('question')[label]}')]")
                                option_to_select.click()
                                time.sleep(5)
                            except NoSuchElementException:
                                try:
                                    input_field = each.find_element(By.TAG_NAME, "input")
                                    input_value = input_field.get_attribute("value")
                                    time.sleep(5)
                                    if input_value:
                                        input_field.clear()
                                        input_field.send_keys(job_data.get('question')[label])
                                        time.sleep(1)
                                except NoSuchElementException:
                                    each.find_element(By.TAG_NAME, "textarea").send_keys(job_data.get('question')[label])
                                    time.sleep(3)

                    self.driver.find_element(By.CSS_SELECTOR, "[type='submit']").click()
                    time.sleep(2)
                    logger.info(f"Successfully Apply for job title: {job_data['title']}")
        self.save_to_json(answers_json)

        self.driver.quit()

    @staticmethod
    def save_to_json(data):
        """ Write updated data back to applicants.json """
        with open('applicants.json', 'w') as json_file:
            json.dump(data, json_file, indent=4)
        logger.info("Updated JSON saved to applicants.json")
