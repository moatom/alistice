'''
MIT License

Copyright (c) 2020 Andriy Orehov

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

from bs4 import BeautifulSoup


def get_node_data(node):
    data = {}
    for child in node:
        if child.name == 'a':
            data['type'] = 'bookmark'
            data['url'] = child.get('href')
            data['title'] = child.text
            data['add_date'] = child.get('add_date')
            data['icon'] = child.get('icon')
            # only in FF
            # icon_uri = child.get('icon_uri')
            # if icon_uri:
            #     data['icon_uri'] = icon_uri
            # tags = child.get('tags')
            # if tags:
            #     data['tags'] = tags.split(',')
        elif child.name == 'h3':
            data['type'] = 'folder'
            data['title'] = child.text
            data['add_date'] = child.get('add_date')
            data['last_modified'] = child.get('last_modified')

            data['ns_root'] = None
            # for Bookmarks Toolbar in FF and Bookmarks bar in Chrome
            if child.get('personal_toolbar_folder'):
                data['ns_root'] = 'toolbar'
            # FF Other Bookmarks
            if child.get('unfiled_bookmarks_folder'):
                data['ns_root'] = 'other_bookmarks'
        elif child.name == 'dl':
            # store DL element reference for further processing the child nodes
            data['__dir_dl'] = child

    if data['type'] == 'folder' and not data.get('__dir_dl'):
        if node.next_sibling and node.next_sibling.name == "dd":
            dls = node.next_sibling.find_all('dl')
            if dls:
                data['__dir_dl'] = dls[0]
    return data


def process_dir(bookmark_dir, level):
    items = []
    menu_root = None
    for child in bookmark_dir:
        if child.name != 'dt':
            continue
        item_data = get_node_data(child)
        if level == 0 and (not item_data.get('ns_root')):
            if menu_root is None:
                # For chrome
                if child.previous_sibling.name == "dt":
                    menu_root = {'type': 'folder', 'title': "Other bookmarks", 'children': [], 'ns_root': 'menu'}
                # for FF
                else:
                    menu_root = {'type': 'folder', 'title': "Bookmarks Menu", 'children': [], 'ns_root': 'menu'}
            if item_data.get('__dir_dl'):
                item_data['children'] = process_dir(item_data['__dir_dl'], level + 1)
                del item_data['__dir_dl']
            menu_root['children'].append(item_data)
        else:
            if item_data.get('__dir_dl'):
                item_data['children'] = process_dir(item_data['__dir_dl'], level + 1)
                del item_data['__dir_dl']
            items.append(item_data)
    if menu_root:
        items.append(menu_root)
    return items


def parse(file_path):
    with open(file_path, 'rb') as f:
        # soup = BeautifulSoup(f, "html.parser")
        soup = BeautifulSoup(f, "html5lib")
    dls = soup.find_all('dl')
    bookmarks = process_dir(dls[0], 0)
    return bookmarks
