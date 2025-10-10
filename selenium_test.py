from selenium import webdriver
from pathlib import Path
import time
USER = "Theotime"# "Mohammad"
PROFILE_ROOT = fr"C:\Users\{USER}\AppData\Local\Google\Chrome\User Data"
PROFILE_NAME = "Profile 3"  # or "Default"

def _ensure_profile_is_clean():
    prof_dir = Path(PROFILE_ROOT) / PROFILE_NAME
    prof_dir.mkdir(parents=True, exist_ok=True)
    # remove stale lock files if Chrome crashed previously
    for p in prof_dir.glob("Singleton*"):
        try:
            p.unlink()
        except Exception:
            pass

def build_driver():
    print("Ens.couring profile is clean...")
    _ensure_profile_is_clean()

    opts = webdriver.ChromeOptions()
    # persistent profile
    opts.add_argument(f"--user-data-dir={PROFILE_ROOT}")
    opts.add_argument(f"--profile-directory={PROFILE_NAME}")

    # stability + avoid the DevToolsActivePort race
    opts.add_argument("--remote-debugging-port=0")  # let Chrome choose a free port
    opts.add_argument("--disable-backgrounding-occluded-windows")
    opts.add_argument("--no-first-run")
    opts.add_argument("--no-default-browser-check")
    # (do NOT set headless while testing persistent profiles)

    # optional: look less automated
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)

    # Selenium Manager will fetch the right driver automatically (Selenium ≥ 4.6)
    print("Creating Chrome WebDriver...")
    driver = webdriver.Chrome(options=opts)
    driver.implicitly_wait(0.5)
    print("WebDriver created successfully.")
    return driver

try:
    driver = build_driver()
    print("Navigating to Google...")
    driver.get("https://www.google.com")
    print("Navigation successful. Sleeping for 10 seconds...")
    time.sleep(10)
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    print("Quitting driver...")
    try:
        driver.quit()
    except Exception as e:
        print(f"Error quitting driver: {e}")
