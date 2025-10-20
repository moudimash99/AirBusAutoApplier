import codecs
import regex as re
from pathlib import Path
def get_links():
    l = []
    input_dir = Path("input")
    files = list(input_dir.glob("bookmarks*"))
    if not files:
        raise FileNotFoundError("No bookmarks files starting with 'bookmarks' found in 'input/'")
    latest_file = max(files, key=lambda p: p.stat().st_mtime)
    f = latest_file.open("r", encoding="utf-8")
    lines = f.readlines()
    for line in lines:
        x2 = re.search('            <DT><A HREF="(.*)" ADD_DATE',line)

        if (x2 != None):

            l.append(x2.group(1))
    return l
