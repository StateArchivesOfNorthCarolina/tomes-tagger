import tomes_tagger.tagger as tagger
from setuptools import setup, setuptools

def doc():
    with open("docs/documentation.md") as d:
        return d.read()
		
setup(
    name = tagger.__NAME__,
    description = tagger.__DESCRIPTION__,
    url = tagger.__URL__,
    version = tagger.__VERSION__,
    author = tagger.__AUTHOR__,
    author_email = tagger.__AUTHOR_EMAIL__,
    packages = setuptools.find_packages(),
    package_data = {"tomes_tagger.lib": ["nlp_to_xml.xsd"]},
    include_package_data = True,
    python_requires = ">=3",
    license = "LICENSE.txt",
    long_description = doc(),
)

