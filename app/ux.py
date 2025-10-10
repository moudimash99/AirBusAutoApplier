# app/ux.py
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as W
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, ElementClickInterceptedException, StaleElementReferenceException
)

class UX:
    def __init__(self, driver, timeout: int, micro_wait: float):
        self.d = driver
        self.timeout = timeout
        self.micro = micro_wait

    def find(self, xpath: str):
        return W(self.d, self.timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))

    def click(self, xpath: str):
        el = W(self.d, self.timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        self.d.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        time.sleep(self.micro)
        for attempt in (1, 2):
            try:
                el.click()
                time.sleep(self.micro)
                return el
            except (ElementClickInterceptedException, StaleElementReferenceException):
                if attempt == 2:
                    # JS fallback
                    self.d.execute_script("arguments[0].click();", el)
                    time.sleep(self.micro)
                    return el

    def type(self, xpath: str, text: str):
        el = self.find(xpath)
        self.d.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        time.sleep(self.micro)
        try: el.clear()
        except: pass
        el.send_keys(text)
        time.sleep(self.micro)
        return el
