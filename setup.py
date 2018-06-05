import tomes_tagger.tagger as tagger
from setuptools import setup, setuptools

def doc():
    with open("docs/documentation.md") as d:
        return d.read()
		
setup(
    author = tagger.__author__,
    author_email = tagger.__author_email__,
    description = tagger.__description__,
    name = tagger.__name__,
    url = tagger.__url__,
    version = tagger.__version__,
    packages = setuptools.find_packages(),
    package_data = {"tomes_tagger.lib": ["nlp_to_xml.xsd"]},
    include_package_data = True,
    python_requires = ">=3",
    license = "LICENSE.txt",
    long_description = doc(),
)

