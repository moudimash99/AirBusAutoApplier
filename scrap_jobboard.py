from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, Iterable
from datetime import datetime

from job_scrapper import scrap_job_board
from job_scrapper.description_getter import extract_job_description
from app.config import SeleniumConfig, CandidateData
from app.driver import build_driver


MAX_ITEMS_PER_FILE = 10


def _ensure_dirs(base: Path) -> tuple[Path, Path]:
    suc = base / "successes"
    mis = base / "misses"
    suc.mkdir(parents=True, exist_ok=True)
    mis.mkdir(parents=True, exist_ok=True)
    return suc, mis


def _today_str() -> str:
    # e.g., 20251018
    return datetime.now().strftime("%Y%m%d")


def _next_index_for_day(dir_: Path, day: str) -> int:
    """
    Scan existing files like 'YYYYMMDD_001.json' and return the next available index (1-based).
    """
    max_idx = 0
    for p in dir_.glob(f"{day}_*.json"):
        try:
            # filename = YYYYMMDD_###.json
            stem = p.stem  # 'YYYYMMDD_###'
            idx_part = stem.split("_", 1)[1]
            idx = int(idx_part)
            if idx > max_idx:
                max_idx = idx
        except Exception:
            continue
    return max_idx + 1


def _chunk(iterable: list[dict], size: int) -> Iterable[list[dict]]:
    for i in range(0, len(iterable), size):
        yield iterable[i : i + size]


def _write_chunks(items: list[dict], out_dir: Path, day: str, start_index: int) -> list[Path]:
    """
    Write items in chunks of MAX_ITEMS_PER_FILE to files:
    <out_dir>/<YYYYMMDD>_<index:03d>.json
    Returns list of written paths.
    """
    written = []
    idx = start_index
    for chunk in _chunk(items, MAX_ITEMS_PER_FILE):
        path = out_dir / f"{day}_{idx:03d}.json"
        path.write_text(json.dumps(chunk, ensure_ascii=False, indent=2), encoding="utf-8")
        written.append(path)
        idx += 1
    return written


def _extract_desc(driver, link: str) -> str:
    """
    Handle both extractor signatures and normalize to a string.
    """
    # Navigate first to stabilize page state
    driver.get(link)
    try:
        res = extract_job_description(driver, timeout=10, expand_show_more=True)
    except TypeError:
        res = extract_job_description(driver, link, timeout=10, expand_show_more=True)

    if isinstance(res, (list, tuple)):
        desc = (res[0] or "").strip() if res else ""
    else:
        desc = (res or "").strip()
    return desc

def write_to_json( suc_dir: Path,
                   mis_dir: Path,
                   day: str,
                   successes: list[dict],
                   misses: list[dict]) -> None:
    """
    Write successes and misses to JSON files in their respective directories.
    """

    # Write in ≤10-item files with date+index naming
    suc_start = _next_index_for_day(suc_dir, day)
    mis_start = _next_index_for_day(mis_dir, day)

    suc_files = _write_chunks(successes, suc_dir, day, suc_start) if successes else []
    mis_files = _write_chunks(misses,   mis_dir, day, mis_start) if misses else []

    if suc_files:
        print("Success files:")
        for p in suc_files:
            print(f"  → {p}")
    if mis_files:
        print("Miss files:")
        for p in mis_files:
            print(f"  → {p}")

    print(f"Saved {len(successes)} successes, {len(misses)} misses.")


def main_get_links(output_dir: Optional[str | Path] = None, max_pages: int = 3, redo_misses: bool = False):
    """
    Scrape job links, extract descriptions, and write JSON files with:
      - successes → <output>/successes/YYYYMMDD_###.json  (≤10 items per file)
      - misses    → <output>/misses/YYYYMMDD_###.json     (≤10 items per file)
    Filenames auto-increment per date, so multiple runs per day append new files.

    If redo_misses is True, the function will re-attempt all previously recorded missed links
    found in the misses directory (all JSON files), instead of collecting new links from the board.
    """
    cfg = SeleniumConfig()
    _me = CandidateData()  # reserved for future use

    driver = build_driver(cfg.user_data_dir, cfg.profile_name)

    repo_root = Path(__file__).resolve().parent
    base_out = Path(output_dir) if output_dir else repo_root / "job_scrapper" / "output"
    suc_dir, mis_dir = _ensure_dirs(base_out)

    day = _today_str()

    successes, misses = [], []
    seen = scrap_job_board._load_seen_from_successes(suc_dir)
    try:
        if not redo_misses:
            links = scrap_job_board.collect_all_job_links(driver, max_pages=max_pages, seen=seen)
        else:
            links = scrap_job_board._load_links_from_misses(mis_dir)
        print(f"Collected {len(links)} links")

        for i, link in enumerate(links, 1):
            try:
                desc = _extract_desc(driver, link)
                if desc:
                    successes.append({"url": link, "description": desc})
                    print(f"[{i}/{len(links)}] OK   {link}")
                else:
                    misses.append({"url": link, "error": "no description found"})
                    print(f"[{i}/{len(links)}] MISS {link} (empty)")
            except Exception as e:
                misses.append({"url": link, "error": str(e)})
                print(f"[{i}/{len(links)}] ERR  {link}: {e}")
        write_to_json(suc_dir, mis_dir, day, successes, misses)
    finally:
        try:
            driver.quit()
        except Exception:
            pass


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Scrape job links and extract descriptions.")
    parser.add_argument("--output-dir", type=str, default=None, help="Custom output directory")
    parser.add_argument("--max-pages", type=int, default=30, help="Max pages to traverse")
    args = parser.parse_args()

    main_get_links(output_dir=args.output_dir, max_pages=args.max_pages, redo_misses=False)
