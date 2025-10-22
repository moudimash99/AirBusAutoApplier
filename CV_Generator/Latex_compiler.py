import subprocess
import shutil
from pathlib import Path
from datetime import datetime
import PyPDF2
def build_pdf(
    tex_path: Path,
    tex_source: str | None = None,     # pass new LaTeX content if you want to overwrite the file
    engine: str = "xelatex",           # "xelatex" | "lualatex" | "pdflatex"
    jobname: str | None = None,        # output PDF name without .pdf; defaults to tex filename
    workdir: Path | None = None,       # directory to run in; defaults to tex_path.parent
    force_rebuild: bool = True,       # use -g to force rebuild when you know the file changed
    clean_aux_first: bool = True,     # remove aux files before compiling
    keep_aux: bool = False             # keep aux after success
) -> Path:
    tex_path = Path(tex_path).resolve()
    if workdir is None:
        workdir = tex_path.parent
    if jobname is None:
        jobname = tex_path.stem

    # 0) Write/overwrite the .tex file if content provided
    if tex_source is not None:
        tex_path.write_text(tex_source, encoding="utf-8")

    # 1) Quick sanity checks
    if shutil.which("latexmk") is None:
        raise RuntimeError("latexmk not found on PATH. Install MiKTeX/TeX Live and ensure latexmk is available.")
    if shutil.which(engine) is None:
        raise RuntimeError(f"{engine} not found on PATH. Install it or switch engine.")

    # 2) Optional clean
    if clean_aux_first:
        subprocess.run(["latexmk", "-C", tex_path.name], cwd=workdir, check=False)

    # 3) Compile
    cmd = [
        "latexmk",
        f"-{engine}",
        "-halt-on-error",
        "-interaction=nonstopmode",
        f"-jobname={jobname}",
    ]
    if force_rebuild:
        cmd.append("-g")

    cmd.append(tex_path.name)
    print(">>", " ".join(cmd))
    p = subprocess.run(cmd, cwd=workdir)

    # 4) On failure, surface the tail of the log
    if p.returncode != 0:
        log = workdir / f"{jobname}.log"
        tail = ""
        if log.exists():
            lines = log.read_text(errors="ignore").splitlines()
            tail = "\n".join(lines[-80:])
        raise RuntimeError(f"LaTeX build failed.\nCommand: {' '.join(cmd)}\n\n--- LOG TAIL ---\n{tail}")

    # 5) Success: optionally clean aux
    if not keep_aux:
        subprocess.run(["latexmk", "-c", tex_path.name], cwd=workdir, check=False)

    pdf_path = workdir / f"{jobname}.pdf"
    if not pdf_path.exists():
        raise RuntimeError("Build reported success but PDF not found.")
    # copy the done pdf to a timestamped file in the output folder
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    CV_Output_Dir = workdir / "output"
    stamped_pdf_path = CV_Output_Dir / f"{jobname}_{timestamp}.pdf"
    CV_Output_Dir.mkdir(parents=True, exist_ok=True)
    shutil.move(str(pdf_path), str(stamped_pdf_path))
    return stamped_pdf_path
def pdf_is_1_page(pdf_path: Path) -> bool:
    """Check if the given PDF has only 1 page."""

    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        return len(reader.pages) == 1

# ------------------- Example usage -------------------
if __name__ == "__main__":
    TEX_FILE = Path(r"C:\Users\moudi\Downloads\Mohammad_CV_2_Parts\mohammad_main_CV.tex")

    # Example: dynamically update a field, then compile to a timestamped PDF
    original = TEX_FILE.read_text(encoding="utf-8")
    stamped = original.replace("%%DATE_PLACEHOLDER%%", datetime.now().strftime("%Y-%m-%d"))

    out_pdf = build_pdf(
        tex_path=TEX_FILE,
        tex_source=stamped,        # omit or pass None if the .tex is already modified elsewhere
        engine="xelatex",          # match Overleaf’s engine
        jobname="mohammad_main_CV_build",  # control output filename
        force_rebuild=True,        # useful when you know content changed
        clean_aux_first=False,     # set True if latexmk thinks things are up-to-date after a failure
        keep_aux=False
    )
    print("PDF ready at:", out_pdf)
