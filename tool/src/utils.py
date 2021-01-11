import datetime
import os
import requests
import json
from configparser import ConfigParser, NoOptionError

def getFiletime(dtms):
  seconds, micros = divmod(dtms, 1000000)
  days, seconds = divmod(seconds, 86400)
  return (datetime.datetime(1601, 1, 1) + datetime.timedelta(days, seconds, micros)).timestamp()


def get_firefox_default_profile_paths(path):
    installs_path = os.path.join(path, 'installs.ini')
    if os.path.exists(installs_path):
        config = ConfigParser()
        config.read(installs_path)

        profile_paths = []
        for name in config.sections():
            try:
                profile_paths.append(os.path.join(path, config.get(name, 'default')))
            except NoOptionError:
                continue
        return profile_paths

    # There is no default profile
    print('{} does not exist'.format(path), file=sys.stderr)
    return None


def normalizeChromeBookmarks(node, parent):
    node_a = {'children': []}
    parent['children'].append(node_a)

    node_a['title'] = node.get('name')
    node_a['add_date'] = str(getFiletime(int(node.get('date_added'))))

    if node.get('type') == 'url':
        node_a['type'] = 'bookmark'
        node_a['url'] = node.get('url')

    elif node.get('type') == 'folder':
        node_a['type'] = 'folder'
        for child in node.get('children'):
            normalizeChromeBookmarks(child, node_a)


# curl http://localhost:5000/api/auth/signin -c cookie.txt -X POST -H "Content-Type: application/json" -d '{"email": "test@test.com", "password": "testtest"}'
# curl http://localhost:5000/api/bookmarks/autoadd -b cookie.txt -X POST -H "Content-Type: application/json" -d '{"email": "test@test.com", "password": "testtest"}'
def send(root, email, password):
    signin_url = 'http://localhost:5000/api/auth/signin'
    import_url = 'http://localhost:5000/api/bookmarks/uniqueadd'
    auth = {
        'email': email,
        'password': password
    }
    header = {
        'Content-Type': 'application/json'
    }

    r = requests.post(signin_url, data=json.dumps(auth), headers=header)
    cookies = r.cookies
    # should backup json.dumps(root) to some file
    r = requests.post(import_url, data=json.dumps(root), cookies=cookies, headers=header)
    if json.loads(r.text).get('message') == 'Success':
        print("imported")
