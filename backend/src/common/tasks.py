from src.extentions import celery

import os
from urllib.parse import urlparse, urlunparse, urljoin

import requests
from bs4 import BeautifulSoup
from PIL import Image


@celery.task()
def saveFavicon(URL, filename):
  try:
    if not os.path.isfile(filename):
        page = requests.get(URL, timeout=1)
        soup = BeautifulSoup(page.content, 'html.parser')

        b = soup.find(rel="icon")
        b = getImagePlace(b, 'href')
        if not b:
            b = soup.find('meta', itemprop="image")
            b = getImagePlace(b, 'content')

        if b:
            a = requests.get(urljoin(URL, b), timeout=1)
            with open(filename, 'w+b') as fp:
                fp.write(a.content)
                if b.lower().endswith('.ico') or b.lower().endswith('.jpg'):
                    im = Image.open(fp)
                    im.save(fp, 'png')
  except Exception as err:
    # @fix should write it to a file
    print(err)


def getImagePlace(found, attr):
    if found:
        return found.get(attr)
