from selenium import webdriver
from pathlib import Path

USER_DATA_DIR = Path(r"C:\SeleniumProfiles\SeleniumAirbus")  # fixed location
PROFILE_NAME  = "Default"                                     # always "Default" here

def _clean_stale_locks():
    prof = USER_DATA_DIR / PROFILE_NAME
    prof.mkdir(parents=True, exist_ok=True)
    for p in prof.glob("Singleton*"):
        try:
            p.unlink()
        except Exception:
            pass

def build_driver():
    _clean_stale_locks()

    opts = webdriver.ChromeOptions()
    # persistent, dedicated profile (do not open it manually while Selenium runs)
    opts.add_argument(f"--user-data-dir={USER_DATA_DIR}")
    opts.add_argument(f"--profile-directory={PROFILE_NAME}")

    # stability flags (help avoid DevToolsActivePort issues)
    opts.add_argument("--remote-debugging-port=0")
    opts.add_argument("--disable-backgrounding-occluded-windows")
    opts.add_argument("--no-first-run")
    opts.add_argument("--no-default-browser-check")
    # IMPORTANT: while stabilizing, avoid headless. Later you can use: opts.add_argument("--headless=new")

    # Let Selenium Manager pick the right driver automatically (Selenium ≥ 4.6)
    driver = webdriver.Chrome(options=opts)
    driver.implicitly_wait(0.5)
    return driver

if __name__ == "__main__":
    d = build_driver()
    d.get("https://ag.wd3.myworkdayjobs.com/fr-FR/Airbus")
    import time;
    time.sleep(10)
    # ... your flow ...
    d.quit()
