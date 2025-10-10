# app/driver.py
from pathlib import Path
from selenium import webdriver

def clean_stale_locks(user_data_dir: Path, profile_name: str):
    prof = user_data_dir / profile_name
    prof.mkdir(parents=True, exist_ok=True)
    for p in prof.glob("Singleton*"):
        try: p.unlink()
        except: pass

def build_driver(user_data_dir: Path, profile_name: str) -> webdriver.Chrome:
    clean_stale_locks(user_data_dir, profile_name)
    opts = webdriver.ChromeOptions()
    opts.add_argument(f"--user-data-dir={user_data_dir}")
    opts.add_argument(f"--profile-directory={profile_name}")
    opts.add_argument("--remote-debugging-port=0")
    opts.add_argument("--disable-backgrounding-occluded-windows")
    opts.add_argument("--no-first-run")
    opts.add_argument("--no-default-browser-check")
    drv = webdriver.Chrome(options=opts)
    drv.implicitly_wait(0.5)
    return drv
