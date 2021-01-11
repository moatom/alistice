#!/usr/bin/python3
# origins: http://www.macosxhints.com/dlfiles/export_bookmarks.txt,
#          http://hints.macworld.com/article.php?story=20061227073124530
# allow full disk access to your shell: https://support.avast.com/en-ca/article/Mac-full-disk-access
#                                       (system preferences / security & privacy / privacy / full disk access)

import sys, os, codecs, plistlib


def parsePlist(bookmarks_file):
    try:
        with open(bookmarks_file, 'rb') as f: 
            t = plistlib.load(f)
        return t
    except:
        os.system("/usr/bin/plutil -convert xml1 %s" % bookmarks_file )
        with open(bookmarks_file, 'rb') as f: 
            xmlContent = plistlib.load(f)
        os.system("/usr/bin/plutil -convert binary1 %s" % bookmarks_file )
        return xmlContent


def read_bookmarks():
    bookmarks_file = os.path.join(
        os.getenv("HOME"),
        "Library/Safari/Bookmarks.plist"
    )
    return parsePlist(bookmarks_file)



# Main
def header():
    print("""<!DOCTYPE NETSCAPE-Bookmark-file-1>
    <HTML>
    <META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
    <Title>Bookmarks</Title>
    <H1>Bookmarks</H1>""")


def filter_bookmarks(node, wanted, found = 0, depth = 0):
    node_type  = node.get("WebBookmarkType")
    node_title = node.get("Title")
    if node_title == "BookmarksBar": node_title ="Bookmarks Bar"
    indent = "\t" * depth
    if node_type == "WebBookmarkTypeList":
        found = found or (node_title in wanted)
        if found and node_title:
            print("%s<DT><H3 FOLDED>%s</H3>" % (indent, node_title))
            print("%s<DL><p>" % indent)
        for child in node.get("Children", []):
            filter_bookmarks(child, wanted, found, found*(depth+1)) 
        if found and node_title:
            print("%s</DL><p>" % indent)
    elif node_type == "WebBookmarkTypeLeaf":
        if found:
            print('%s<DT><A HREF="%s">%s</A>' % (
                indent,
                node["URLString"],
                node["URIDictionary"]["title"]
            ))


def footer():
    print("""</HTML>""")


def main(args):
    header()
    if args: filter_bookmarks(read_bookmarks(), args)
    else: filter_bookmarks(read_bookmarks(), [], found=1)
    footer()


if __name__ == "__main__": main(sys.argv[1:]) 
