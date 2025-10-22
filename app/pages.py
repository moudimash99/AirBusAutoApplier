# app/pages.py
from pathlib import Path
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait as W
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from app.file_uploader import upload_files_example
import app.path as loc  # your existing locators

class JobPage:
    def __init__(self, ux: "UX"):
        self.u = ux

    def start_application(self):
        self.u.click(loc.apply_button_path)
        # “Use last application” optional
        try: self.u.click(loc.use_last_button_path)
        except: pass
        # Sometimes an extra sign-in click
        try: self.u.click(loc.signin2_xpath)
        except: pass
    def experience_page(self, cv_path: Path):
        
        # Delete any pre-uploaded CVs
        for _ in range(2):
            try:
                self.u.click(loc.delete_file)
            except:
                break

        upload_files_example( self.u.d, [cv_path])
        self.u.click(loc.save_cont_path)
        
    def select_source(self):
        self.u.click(loc.how_hear_path)
        self.u.click(loc.career_website_button_path)
        # Worked at Airbus before?
        # self.u.click(loc.worked_no)
        # self.u.click(loc.worked_yes)

        driver = self.u.d
        YES = driver.find_element(By.CSS_SELECTOR, "input[name='candidateIsPreviousWorker'][value='true']")
        NO  = driver.find_element(By.CSS_SELECTOR, "input[name='candidateIsPreviousWorker'][value='false']")

        # 1) Click No via its label (avoids hidden/overlay issues)
        no_label = driver.find_element(By.CSS_SELECTOR, f"label[for='{NO.get_attribute('id')}']")
        no_label.click()
        import time;
        time.sleep(1)  # wait for any dynamic changes
        driver.find_element(By.CSS_SELECTOR, "label[for='%s']" % YES.get_attribute('id')).click()
        time.sleep(1)  # wait for any dynamic changes
        self.u.type(loc.worker_code_id, "580323")  # if yes, fill employee ID
        
        self.u.click(loc.save_cont_path)

        # Some flows have an intermediate "Save and Continue"
        

class ApplicationWizard:
    def __init__(self, driver, ux: "UX", data):
        self.d = driver
        self.u = ux
        self.data = data

    def fill_education(self):
        self.u.type(loc.semester_level_path, self.data.semester_level)
        self.u.type(loc.uni_name_path,      self.data.university)
        self.u.type(loc.course_path,        self.data.course)
        self.u.type(loc.finish_studies,     self.data.finish_studies)

    def set_contract(self):

        kind_internship = "(//button[@id='primaryQuestionnaire--ac8482cbac9710014b9fd5af795f0000'])[1]"
        kind_internship_answer = "(//div[contains(text(),'I am looking for an internship in the frame of my ')])[1]"
        compulsary_internship = "(//button[@id='primaryQuestionnaire--d88b76473de410014b353bd4d28a0004'])[1]"
        compulsary_internship_answer = "(//div[contains(text(),'yes, my internship is mandatory to validate my yea')])[1]"
        single_period_internship = "(//button[@id='primaryQuestionnaire--d88b76473de410014b353c6e9e690000'])[1]"
        single_period_internship_answer = "(//div[normalize-space()='My internship takes place over a single period'])[1]"
        duration_internship = "(//textarea[@id='primaryQuestionnaire--d88b76473de410014b353c6e9e690003'])[1]"
        level_study = "(//textarea[@id='primaryQuestionnaire--d88b76473de410014b353c6e9e690004'])[1]"
        self.u.click(kind_internship)
        self.u.click(kind_internship_answer)
        self.u.click(compulsary_internship)
        self.u.click(compulsary_internship_answer)
        self.u.click(single_period_internship)
        self.u.click(single_period_internship_answer)
        self.u.type(duration_internship, self.data.duration)
        self.u.type(level_study, self.data.level)


    def set_languages(self):
        self.u.click(loc.eng_rate); self.u.click(loc.fluent)
        self.u.click(loc.fen_rate); self.u.click(loc.intm)

    def final_page(self):
        # ensure in view
        W(self.d, self.u.timeout).until(EC.presence_of_element_located((By.XPATH, loc.add_nat)))
        # birth date via calendar control
        self.u.click(loc.bd)
        ActionChains(self.d).send_keys(self.data.birth_ddmmyyyy).perform()
        # nationality
        self.u.click(loc.nation)
        self.u.click(loc.liban)
        self.u.click(loc.accept)
        # need to do gender too
        self.u.click(loc.gend)
        self.u.click(loc.male)
        self.u.click(loc.save_cont_path)

    def submit(self):
        self.u.click(loc.submit)
