from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    ElementClickInterceptedException,
    ElementNotInteractableException,
    StaleElementReferenceException,
)
import re
from typing import Tuple

def extract_job_description(driver, link : str , timeout: int = 15, expand_show_more: bool = True) -> Tuple[str, str]:
    """
    Wait for the job description container, optionally expand "show more" blocks,
    and return a tuple (job_description_text, job_description_html).

    Raises:
        TimeoutException: if the description container isn't visible within `timeout` seconds.
    """
    driver.get(link)
    if expand_show_more:
        buttons = driver.find_elements(
            By.XPATH,
            '//button[.//text()[contains(.,"Show more") or contains(.,"Voir plus") or contains(.,"Read more") or contains(.,"Afficher plus")]]'
        )
        for b in buttons:
            try:
                b.click()
            except (ElementClickInterceptedException, ElementNotInteractableException, StaleElementReferenceException):
                try:
                    driver.execute_script("arguments[0].scrollIntoView(true);", b)
                    b.click()
                except Exception:
                    # ignore buttons that cannot be clicked
                    continue

    desc_el = WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, '[data-automation-id="jobPostingDescription"]'))
    )
    job_description_text = re.sub(r'\n{3,}', '\n\n', desc_el.text or '').strip()
    job_description_html = desc_el.get_attribute('innerHTML') or ''
    return job_description_text, job_description_html
