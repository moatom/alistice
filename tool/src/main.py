import os
import json
import tempfile
import sys
import subprocess
import safariOnMac
from utils import getFiletime, get_firefox_default_profile_paths, normalizeChromeBookmarks, send
from bookmarks_parser  import parse
from configparser import ConfigParser, NoOptionError


settings_path = 'settings.ini'

# Referred to https://github.com/jarun/buku
if sys.platform.startswith(('linux', 'freebsd', 'openbsd')):
    chrome_path   = '~/.config/google-chrome/Default/Bookmarks'
    chromium_path = '~/.config/chromium/Default/Bookmarks'

    firefox_base_path     = os.path.expanduser('~/.mozilla/firefox')
    firefox_profile_paths = get_firefox_default_profile_paths(firefox_base_path)
elif sys.platform == 'darwin':
    chrome_path   = '~/Library/Application Support/Google/Chrome/Default/Bookmarks'
    chromium_path = '~/Library/Application Support/Chromium/Default/Bookmarks'

    firefox_base_path     = os.path.expanduser('~/Library/Application Support/Firefox')
    firefox_profile_paths = get_firefox_default_profile_paths(firefox_base_path)
elif sys.platform == 'win32':
    username = os.getlogin()
    chrome_path   = 'C:/Users/{}/AppData/Local/Google/Chrome/User Data/Default/Bookmarks'.format(username)
    chromium_path = 'C:/Users/{}/AppData/Local/Chromium/User Data/Default/Bookmarks'.format(username)

    firefox_base_path     = 'C:/Users/{}/AppData/Roaming/Mozilla/Firefox/'.format(username)
    firefox_profile_paths = get_firefox_default_profile_paths(firefox_base_path)
else:
    print("We don't support {}.".format(sys.platform), file=sys.stderr)
    raise Exception("")

chrome_path   = os.path.expanduser(chrome_path)
chromium_path = os.path.expanduser(chromium_path)



def first_use():
    if not os.path.exists(settings_path):
        with open(settings_path, mode='x') as f:
            f.write('')
        config = ConfigParser()
        config.read(settings_path)

        email    = input('Input your email address to sign in Alistice: ')
        password = input('Input your      password to sign in Alistice: ')
        config['account'] = {'email': email, 'password': password}

        try:
            resp = input('Import bookmarks from google chrome? (y/n): ')
            if resp == 'y':
                if not os.path.exists(chrome_path):
                    raise FileNotFoundError
                config['chrome'] = {'import': 'y'}
            else:
                config['chrome'] = {'import': 'n'}
        except Exception as e:
            print('Chrome seems to be not installed.', file=sys.stderr)

        try:
            resp = input('Import bookmarks from chromium? (y/n): ')
            if resp == 'y':
                if not os.path.exists(chromium_path):
                    raise FileNotFoundError
                config['chromium'] = {'import': 'y'}
            else:
                config['chromium'] = {'import': 'n'}
        except Exception as e:
            print('Chromium seems to be not installed.', file=sys.stderr)

        try:
            print('Caution: importation function from firefox is especially experimental and may be dangerous.')
            resp = input('Import bookmarks from Firefox? (y/n): ')
            if resp == 'y':
                config['firefox'] = {'import': 'y'}
                output_db = os.path.join(tempfile.gettempdir(), 'ff_bookmarks.html') 
                for profile in firefox_profile_paths:
                    with open(os.path.join(profile, 'user.js'), mode='a') as f:
                        f.writelines(['user_pref("browser.bookmarks.autoExportHTML", true);\n',\
                            'user_pref("browser.bookmarks.file", "{}");\n'.format(output_db)])
            else:
                config['firefox'] = {'import': 'n'}
        except Exception as e:
            print('Firefox seems to be not installed.', file=sys.stderr)

        if sys.platform == 'darwin':
            resp = input('Import bookmarks from Safari? (y/n): ')
            if resp == 'y':
                config['safari'] = {'import': 'y'}
            else:
                config['safari'] = {'import': 'n'}

        with open(settings_path, 'w') as f:
            config.write(f)


def main():
    first_use()

    config = ConfigParser()
    config.read(settings_path)
    email = config['account']['email']
    password = config['account']['password']

    if config['chrome']['import'] == 'y':
        with open(chrome_path) as f:
            roots = json.load(f).get('roots')
            root = {'children': []}
            for node in [roots.get('bookmark_bar'), roots.get('other')]:
                normalizeChromeBookmarks(node, root)
            print("importing chrome's bookmarks...")
            send(root, email, password)
            print("")

    if config['chromium']['import'] == 'y':
        with open(chromium_path) as f:
            roots = json.load(f).get('roots')
            root = {'children': []}
            for node in [roots.get('bookmark_bar'), roots.get('other')]:
                normalizeChromeBookmarks(node, root)
            print("importing chromium's bookmarks...")
            send(root, email, password)
            print("")

    if config['firefox']['import'] == 'y':
        output_db = os.path.join(tempfile.gettempdir(), 'ff_bookmarks.html') 
        root = {'children': parse(output_db)}
        print("importing firefox's bookmarks...")
        send(root, email, password)
        print("")

    if config['safari']['import'] == 'y':
        output_db = os.path.join(tempfile.gettempdir(), 'sa_bookmarks.html') 

        with open(output_db, mode='w') as f:
            subprocess.run(['python3', 'safariOnMac.py'], stdout=f)
        root = {'children': parse(output_db)}
        print("importing safari's bookmarks...")
        send(root, email, password)
        print("")


if __name__ == "__main__":
    main()
