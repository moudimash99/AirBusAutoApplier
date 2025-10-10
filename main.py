# main.py
from __future__ import annotations
import time
import traceback
from pathlib import Path
from typing import Iterable, Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

import path
import link_getter

# -------------------------
# Chrome profile (dedicated)
# -------------------------
USER_DATA_DIR = Path(r"C:\SeleniumProfiles\SeleniumAirbus")
PROFILE_NAME  = "Default"  # with a custom user-data-dir, the profile folder is "Default"

SHORT_WAIT = 0.4
TIMEOUT    = 20

def _clean_stale_locks():
    prof = USER_DATA_DIR / PROFILE_NAME
    prof.mkdir(parents=True, exist_ok=True)
    for p in prof.glob("Singleton*"):
        try: p.unlink()
        except: pass

def build_driver() -> webdriver.Chrome:
    _clean_stale_locks()
    opts = webdriver.ChromeOptions()
    opts.add_argument(f"--user-data-dir={USER_DATA_DIR}")
    opts.add_argument(f"--profile-directory={PROFILE_NAME}")
    # stability
    opts.add_argument("--remote-debugging-port=0")
    opts.add_argument("--disable-backgrounding-occluded-windows")
    opts.add_argument("--no-first-run")
    opts.add_argument("--no-default-browser-check")
    # Let Selenium Manager pick the right driver automatically
    driver = webdriver.Chrome(options=opts)
    driver.implicitly_wait(0.5)
    return driver

# -------------------------
# Small helpers
# -------------------------
def wait_click(driver, xpath: str, timeout: int = TIMEOUT, scroll: bool = True):
    el = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))
    if scroll:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        time.sleep(SHORT_WAIT)
    el.click()
    time.sleep(SHORT_WAIT)
    return el

def wait_type(driver, xpath: str, text: str, timeout: int = TIMEOUT):
    el = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
    time.sleep(SHORT_WAIT)
    try: el.clear()
    except: pass
    el.send_keys(text)
    time.sleep(SHORT_WAIT)
    return el

def type_calendar_ddmmyyyy(driver, xpath: str, ddmmyyyy: str):
    el = wait_click(driver, xpath)
    ActionChains(driver).send_keys(ddmmyyyy).perform()
    time.sleep(SHORT_WAIT)
    return el

# -------------------------
# Your original domain steps (cleaned)
# -------------------------
def sign_in(driver):
    # Idempotent sign-in sequence (if already signed in, it just times out gracefully)
    try:
        wait_click(driver, path.signin_xpath, timeout=8)
        wait_click(driver, path.signin_xpath, timeout=8)
        wait_click(driver, path.signin2_xpath, timeout=8)
    except TimeoutException:
        pass  # likely already signed in

def apply_stage(driver):
    # Education
    wait_type(driver, path.semester_level_path, "M1")
    wait_type(driver, path.uni_name_path, "UNIVERSITÉ TOULOUSE III - PAUL SABATIER")
    wait_type(driver, path.course_path, "Master’s In Computer Science for Aerospace")
    wait_type(driver, path.finish_studies, "06/24")

    # Contract
    wait_click(driver, path.contract_type)
    wait_click(driver, path.drop_dwn_path)
    wait_type(driver, path.third_part_financ, "/")
    wait_click(driver, path.mand)
    wait_type(driver, path.availb, "1/1/2023 - 1/9/2023")
    wait_type(driver, path.dur_int, "Until 23/9/2023")

    # Languages
    wait_click(driver, path.eng_rate)
    wait_click(driver, path.fluent)
    wait_click(driver, path.fen_rate)
    wait_click(driver, path.intm)

def final_page(driver):
    # Move into view
    add_nat_el = WebDriverWait(driver, TIMEOUT).until(EC.presence_of_element_located((By.XPATH, path.add_nat)))
    ActionChains(driver).move_to_element(add_nat_el).perform()

    # Birth date & nationality
    type_calendar_ddmmyyyy(driver, path.bd, "06101999")
    wait_click(driver, path.nation)
    wait_click(driver, path.liban)
    wait_click(driver, path.accept, scroll=True)

    wait_click(driver, path.save_cont_path)

def apply_website(driver):
    # Apply
    wait_click(driver, path.apply_button_path)

    # Use last application if offered
    try:
        wait_click(driver, path.use_last_button_path, timeout=6)
    except TimeoutException:
        pass

    # Some pages require pressing Sign In again
    try:
        WebDriverWait(driver, 6).until(EC.element_to_be_clickable((By.XPATH, path.signin2_xpath))).click()
    except TimeoutException:
        pass

    # “How did you hear about us?”
    wait_click(driver, path.how_hear_path)
    wait_click(driver, path.career_website_button_path)
    wait_click(driver, path.save_cont_path)

    # Sometimes there's an extra intermediate page
    try:
        wait_click(driver, path.save_cont_path, timeout=6)
    except TimeoutException:
        pass

    # Main sections
    apply_stage(driver)
    wait_click(driver, path.save_cont_path)

    # Final
    final_page(driver)

    # Submit
    wait_click(driver, path.submit)

# -------------------------
# Orchestration
# -------------------------
def iter_links() -> list[str]:
    # Use your link_getter if available; otherwise known list
    try:
        links = link_getter.get_links()  # keep your existing call signature
    except TypeError:
        links = None
    if not links:
        links = [
            "https://ag.wd3.myworkdayjobs.com/en-US/Airbus/job/Blagnac---Wings-Campus/Stage-en-gestion-de-projet--f-h-_JR10149650"
        ]
    return links

def main():
    success_fp = Path("succ_links.txt").open("a", encoding="utf-8")
    missed_fp  = Path("missed_links.txt").open("a", encoding="utf-8")
    driver = build_driver()

    try:
        links = iter_links()
        # Prime sign-in on first link (since you now persist the session, this is usually quick)
        driver.get("https://ag.wd3.myworkdayjobs.com/fr-FR/Airbus")
        time.sleep(2)
        sign_in(driver)

        for link in links:
            try:
                driver.get(link)
                WebDriverWait(driver, TIMEOUT).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                time.sleep(1.0)

                apply_website(driver)
                success_fp.write(link + "\n")
                success_fp.flush()
                print(f"✅ Applied: {link}")
            except Exception:
                missed_fp.write(link + "\n")
                missed_fp.flush()
                traceback.print_exc()
                print(f"❌ Missed: {link}")
    finally:
        try:
            success_fp.close(); missed_fp.close()
        except: pass
        driver.quit()

if __name__ == "__main__":
    main()
