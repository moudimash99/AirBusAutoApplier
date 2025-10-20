# main.py
import traceback
from pathlib import Path
from app.config import SeleniumConfig, CandidateData
from app.driver import build_driver
from app.ux import UX
from app.pages import JobPage, ApplicationWizard
import app.link_getter
from job_scrapper.description_getter import extract_job_description
CFG = SeleniumConfig()
ME  = CandidateData()

def sign_in_if_present(ux: UX):
    import app.path as loc
    ux.d.get("https://ag.wd3.myworkdayjobs.com/en-US/Airbus")
    for xp in (loc.signin_xpath, loc.signin_xpath, loc.signin2_xpath):
        try: ux.click(xp)
        except: pass  # already signed in / not visible

def apply_one(driver, link: str) -> bool:
    ux = UX(driver, CFG.timeout_s, CFG.micro_wait_s)
    driver.get(link)
    job_description_text, job_description_html = extract_job_description(driver, timeout=10, expand_show_more=True)
    job = JobPage(ux)
    job.start_application()
    job.select_source()

    wiz = ApplicationWizard(driver, ux, ME)
    # wiz.fill_education()
    wiz.set_contract()
    # wiz.set_languages()
    ux.click("//*[normalize-space()='Save and Continue']")  # reuse locator if needed
    wiz.final_page()
    wiz.submit()
    return True
def get_output_files():
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    succ_path = output_dir / "succ_links.txt"
    miss_path = output_dir / "missed_links.txt"
    print(f"Success links will be written to: {succ_path}")
    print(f"Missed links will be written to: {miss_path}")
    succ = succ_path.open("a", encoding="utf-8")
    miss = miss_path.open("a", encoding="utf-8")
    return succ, miss

def main():
    succ, miss = get_output_files()
    d = build_driver(CFG.user_data_dir, CFG.profile_name)
    sign_in_if_present(UX(d, CFG.timeout_s, CFG.micro_wait_s))
    try:
        links = None
        try: links = app.link_getter.get_links()
        except: pass
        if not links:
            links = ["https://ag.wd3.myworkdayjobs.com/en-US/Airbus/job/Blagnac---Wings-Campus/Stage-en-gestion-de-projet--f-h-_JR10149650"]

        for link in links:
            try:
                ok = apply_one(d, link)
                (succ if ok else miss).write(link + "\n")
            except Exception:
                miss.write(link + "\n")
                traceback.print_exc()
    finally:
        succ.close(); miss.close()
        d.quit()

if __name__ == "__main__":
    main()
