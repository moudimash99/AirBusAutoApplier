# main.py
import traceback
from pathlib import Path
from app.config import SeleniumConfig, CandidateData
from app.driver import build_driver
from app.ux import UX
from app.pages import JobPage, ApplicationWizard
import app.link_getter
from job_scrapper.description_getter import extract_job_description
from CV_Generator.Latex_compiler import build_pdf,pdf_is_1_page
from CV_Generator.CV_Generator import create_latex_CV
from utils import pause_for_human_resume
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
    job_name,job_description_text = extract_job_description(driver,link, timeout=10, expand_show_more=True)
    latex_file_path = create_latex_CV(job_description_text)
    cv_path = build_pdf(Path(latex_file_path),jobname=job_name)
    # make sure that the CV is no more than 1 page, if it is , then paut a pause for 5 minutes that can be resumed by a human

    if not pdf_is_1_page(cv_path):
        print(f"CV {cv_path} has more than 1 page. Pausing for manual review.")
        pause_for_human_resume(300,raise_on_timeout=True)
    else:
        print(f"CV {cv_path} is 1 page. Pausing for review.")
        pause_for_human_resume(180, raise_on_timeout=False)


    job = JobPage(ux)
    job.start_application()
    job.select_source()
    job.experience_page(cv_path)
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
        
        links = app.link_getter.get_links()
        
        if not links:
            raise RuntimeError("No links obtained from link getter.")
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
