# app/pages.py
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait as W
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import path as loc  # your existing locators

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

    def select_source(self):
        self.u.click(loc.how_hear_path)
        self.u.click(loc.career_website_button_path)
        self.u.click(loc.save_cont_path)
        # Some flows have an intermediate "Save and Continue"
        try: self.u.click(loc.save_cont_path)
        except: pass

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
        self.u.click(loc.contract_type)
        self.u.click(loc.drop_dwn_path)
        self.u.type(loc.third_part_financ, "/")
        self.u.click(loc.mand)
        self.u.type(loc.availb, self.data.availability)
        self.u.type(loc.dur_int, self.data.duration)

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
        self.u.click(loc.save_cont_path)

    def submit(self):
        self.u.click(loc.submit)
