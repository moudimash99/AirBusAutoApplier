# main.py
import traceback
from pathlib import Path
from app.config import SeleniumConfig, CandidateData
from app.driver import build_driver
from app.ux import UX
from app.pages import JobPage, ApplicationWizard
import link_getter

CFG = SeleniumConfig()
ME  = CandidateData()

def sign_in_if_present(ux: UX):
    import path as loc
    for xp in (loc.signin_xpath, loc.signin_xpath, loc.signin2_xpath):
        try: ux.click(xp)
        except: pass  # already signed in / not visible

def apply_one(driver, link: str) -> bool:
    ux = UX(driver, CFG.timeout_s, CFG.micro_wait_s)
    driver.get(link)
    sign_in_if_present(ux)

    job = JobPage(ux)
    job.start_application()
    job.select_source()

    wiz = ApplicationWizard(driver, ux, ME)
    wiz.fill_education()
    wiz.set_contract()
    wiz.set_languages()
    ux.click("//*[normalize-space()='Save and Continue']")  # reuse locator if needed
    wiz.final_page()
    wiz.submit()
    return True

def main():
    succ = Path("succ_links.txt").open("a", encoding="utf-8")
    miss = Path("missed_links.txt").open("a", encoding="utf-8")
    d = build_driver(CFG.user_data_dir, CFG.profile_name)
    try:
        links = None
        try: links = link_getter.get_links()
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
