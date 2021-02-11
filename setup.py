from setuptools import setup
from os.path import abspath, join as pjoin, relpath, split

DISTNAME = 'dbcrawlers'
DESCRIPTION = 'DB Crawlers'
AUTHOR = 'lee3jjang'
AUTHOR_EMAIL = 'lee3jjang@gmail.com'
URL = 'https://github.com/lee3jjang/stockpricecrawler'
SETUP_DIR = split(abspath(__file__))[0]
with open(pjoin(SETUP_DIR, 'README.rst'), encoding='utf8') as readme:
    README = readme.read()
LONG_DESCRIPTION = README

setup(
    name=DISTNAME,
    version='0.0.1',
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    url=URL,
    packages=['dbcrawlers'],
    python_requires=">=3.6",
    zip_safe=False,
)