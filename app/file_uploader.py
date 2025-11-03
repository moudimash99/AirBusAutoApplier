from pathlib import Path
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException

def _abs(p): return str(Path(p).expanduser().resolve())

def upload_files_example(driver, files, timeout=10):
    wait = WebDriverWait(driver, timeout)

    # 1) Scope to the Application attachments group
    group = wait.until(EC.presence_of_element_located((
        By.CSS_SELECTOR, 'div[role="group"][aria-labelledby="Application-attachments-section"]'
    )))

    # 2) Grab the real file input (don’t click the button)
    file_input = group.find_element(By.CSS_SELECTOR, 'input[data-automation-id="file-upload-input-ref"]')

    # 3) Force-show it in case it’s CSS-hidden (so send_keys works)
    try:
        driver.execute_script("""
            arguments[0].style.display='block';
            arguments[0].style.visibility='visible';
            arguments[0].style.opacity=1;
            arguments[0].removeAttribute('hidden');
        """, file_input)
    except Exception:
        pass

    # 4) Send absolute paths (newline-separated if multiple is allowed)
    paths = "\n".join(_abs(p) for p in files)
    try:
        file_input.send_keys(paths)
    except StaleElementReferenceException:
        # React re-rendered; re-find and try once more
        sleep(0.2)
        file_input = group.find_element(By.CSS_SELECTOR, 'input[data-automation-id="file-upload-input-ref"]')
        file_input.send_keys(paths)

    # 5) (Optional) wait for an uploaded item to appear / progress complete
    try:
        wait.until(EC.presence_of_element_located((
            By.CSS_SELECTOR, '[data-automation-id="attachments-FileUpload"] [role="listitem"], .css-10klw3m'
        )))
    except Exception:
        pass
