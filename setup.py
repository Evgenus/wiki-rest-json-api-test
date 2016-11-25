from pathlib import Path
import re
import codecs

from setuptools import setup, find_packages

NAME = "wikiapi"
DESCRIPTION = "Wiki REST JSON Api Test"

CLASSIFIERS = """
Programming Language :: Python
""".strip().split("\n")

AUTHOR = "Eugene Chernyshov"
EMAIL = "chernyshov.eugene@gmail.com"
URL = ""
KEYWORDS = ""

here = Path(__file__).parent.resolve()

with here.joinpath(NAME, '__init__.py').open('r', encoding="utf-8") as stream:
    try:
        VERSION = re.findall(r"""^__version__ = '([^']+)'$""", stream.read(), re.M)[0]
    except IndexError:
        raise RuntimeError('Unable to determine version.')

README = here.joinpath('README.md').open("r").read()
LICENSE = here.joinpath('LICENSE.txt').open("r").read()
requires = here.joinpath('requirements.txt').open("r").readlines()

setup(name=NAME,
      version=VERSION,
      description=DESCRIPTION,
      long_description=README,
      classifiers=CLASSIFIERS,
      author=AUTHOR,
      author_email=EMAIL,
      url=URL,
      license=LICENSE,
      keywords=KEYWORDS,
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite=NAME+".tests",
      entry_points={
          'console_scripts': [
          ]
      }
      )  
