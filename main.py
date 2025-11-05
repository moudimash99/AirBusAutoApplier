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
from CV_Generator.Cover_Letter.Cover_letter_Generator import create_latex_cover_letter
from utils import pause_for_human_resume
from datetime import datetime

CFG = SeleniumConfig()
ME  = CandidateData()

def sign_in_if_present(ux: UX):
    import app.path as loc
    ux.d.get("https://ag.wd3.myworkdayjobs.com/en-US/Airbus")
    for xp in (loc.signin_xpath, loc.signin_xpath, loc.signin2_xpath):
        try: ux.click(xp)
        except: pass  # already signed in / not visible

def build_cv_pdf(job_description_text: Path, job_name: str, link: str) -> Path:
    # latex_file_path = create_latex_CV(job_description_text)

    
    
    


    latex_file_path = r"C:\Users\moudi\OneDrive\Documentos\Coding\mission-control-ultra\AirBusAutoApplier\CV_Generator\Mohammad_CV_2_Parts\CV.tex"
    failed_build = False
    try:
        cv_path = build_pdf(Path(latex_file_path),jobname=job_name)
    except Exception as e:
        print(f"Error building PDF for job {job_name} at {link}: {e}")
        traceback.print_exc()
        failed_build = True
        cv_path = r"C:\Users\moudi\OneDrive\Documentos\Coding\mission-control-ultra\AirBusAutoApplier\CV_Generator\Mohammad_CV_2_Parts\CV.pdf"

        
    # make sure that the CV is no more than 1 page, if it is , then paut a pause for 5 minutes that can be resumed by a human

    
    return failed_build, cv_path

def build_cover_letter(job_description_text: Path, job_name: str, link: str) -> Path:
    
    latex_file_path = create_latex_cover_letter(job_description_text)
    
    failed_build = False
    try:
        cover_letter_path = build_pdf(Path(latex_file_path),jobname="cover_letter_"+job_name)
    except Exception as e:
        print(f"Error building PDF for cover letter {job_name} at {link}: {e}")
        traceback.print_exc()
        failed_build = True
        cover_letter_path = None

        
    # make sure that the cover letter is no more than 1 page, if it is , then paut a pause for 5 minutes that can be resumed by a human
    return failed_build, cover_letter_path
def check_pdf_health(failed_cv, cv_path, failed_cl, cover_letter_path):
    # create a string that shows which one failed
    cv_failed = bool(failed_cv)
    cl_failed = bool(failed_cl)
    cv_one = pdf_is_1_page(cv_path)
    cl_one = pdf_is_1_page(cover_letter_path)

    failed_any = cv_failed or cl_failed or (not cv_one) or (not cl_one)

    reasons = []
    if cv_failed:
        reasons.append("CV build failed")
    if cl_failed:
        reasons.append("Cover letter build failed")
    if not cv_one:
        reasons.append("CV is >1 page")
    if not cl_one:
        reasons.append("Cover letter is >1 page")

    str_failed = ", ".join(reasons) if reasons else "None"
    if failed_any:
        print(f"One or more generated documents failed or are >1 page (Reasons: {str_failed}). Pausing for manual review.")
        # pause_for_human_resume(300, raise_on_timeout=True)
    else:
        print(f"Generated documents are OK (1 page each). Pausing briefly for review.")
        # pause_for_human_resume(60, raise_on_timeout=False)



def apply_one(driver, link: str) -> bool:
    ux = UX(driver, CFG.timeout_s, CFG.micro_wait_s)
    driver.get(link)
    start_ex = datetime.now()
    print(f"[{start_ex.isoformat()}] START: extracting job description for link: {link}")
    job_name, job_description_text = extract_job_description(driver, link, timeout=10, expand_show_more=True)
    done_ex = datetime.now()
    print(
        f"[{done_ex.isoformat()}] DONE: extracted job '{job_name}' (duration {(done_ex - start_ex).total_seconds():.1f}s)"
    )

    print(f"[{datetime.now().isoformat()}] START: building cover letter for job '{job_name}'")
    start_cl = datetime.now()
    failed_cl, cover_letter_path = build_cover_letter(job_description_text, job_name=job_name, link=link)
    done_cl = datetime.now()
    print(
        f"[{done_cl.isoformat()}] DONE: cover letter build for '{job_name}' "
        f"(failed={failed_cl}, path={cover_letter_path}) duration {(done_cl - start_cl).total_seconds():.1f}s"
    )

    print(f"[{datetime.now().isoformat()}] START: building CV for job '{job_name}'")
    start_cv = datetime.now()
    failed_cv, cv_path = build_cv_pdf(job_description_text, job_name=job_name, link=link)
    done_cv = datetime.now()
    print(
        f"[{done_cv.isoformat()}] DONE: CV build for '{job_name}' "
        f"(failed={failed_cv}, path={cv_path}) duration {(done_cv - start_cv).total_seconds():.1f}s"
    )
    check_pdf_health(failed_cv , cv_path, failed_cl , cover_letter_path)
    files = [cv_path]
    if cover_letter_path is not None:
        files.append(cover_letter_path)
    
    job = JobPage(ux)
    job.start_application()
    job.select_source()
    job.experience_page(files=files)
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
                # wait 2 minutes before next application , to attempt human finish 
                pause_for_human_resume(120, raise_on_timeout=False)
    finally:
        succ.close(); miss.close()
        d.quit()

if __name__ == "__main__":
    main()
