import codecs
import regex as re
def get_links():
    l = []
    f=codecs.open("bookmarks_9_23_22.html", 'r')
    lines = f.readlines()
    for line in lines:
        x2 = re.search('            <DT><A HREF="(.*)" ADD_DATE',line)

        if (x2 != None):

            l.append(x2.group(1))
    return l
