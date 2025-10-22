import os
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import JavascriptException


# If the form is in an iframe, switch first:
# driver.switch_to.frame(wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe"))))

def resolve(p):
    return str(Path(p).expanduser().resolve())

def find_file_input(container):
    """
    Find the <input type='file'> inside the given upload widget.
    Handles cases where Workday keeps it hidden or inserts it dynamically.
    """
    # Common patterns inside Workday widgets
    candidates = container.find_elements(By.XPATH, ".//input[@type='file']")
    if not candidates:
        # Sometimes created after clicking "Select files"
        try:
            select_btn = container.find_element(By.CSS_SELECTOR, "button[data-automation-id='select-files']")
            select_btn.click()  # this won't be used to pick files, but often makes the input appear
        except Exception:
            pass
        candidates = container.find_elements(By.XPATH, ".//input[@type='file']")

    # Prefer a displayed/enabled one; otherwise we’ll force-show it
    for el in candidates:
        if el.is_enabled():
            return el
    # Fallback: return first and we’ll unhide via JS
    return candidates[0] if candidates else None

def ensure_visible(el):
    """Make hidden file input interactable."""
    try:
        driver.execute_script("""
            arguments[0].style.display='block';
            arguments[0].style.visibility='visible';
            arguments[0].style.opacity=1;
            arguments[0].removeAttribute('hidden');
        """, el)
    except JavascriptException:
        pass

def upload_files_to_widget(widget, file_paths):
    file_input = find_file_input(widget)
    if not file_input:
        raise RuntimeError("Could not find <input type='file'> in the upload widget.")

    ensure_visible(file_input)

    # Workday accepts multiple files if the input has the 'multiple' attribute.
    # If not, loop and send one by one.
    paths = [resolve(p) for p in file_paths]

    if file_input.get_attribute("multiple"):
        # On Selenium, multiple files are separated by newline
        file_input.send_keys("\n".join(paths))
    else:
        for p in paths:
            file_input.send_keys(p)

def upload_files_example(driver, file_paths: list[str]):
    wait = WebDriverWait(driver, 15)

    # ------- USE IT -------
    # Narrow to the specific upload drop-zone you showed:
    widget = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "div[data-automation-id='file-upload-drop-zone']"))
    )

    # Example: upload specific files by absolute path
    upload_files_to_widget(widget, file_paths)
