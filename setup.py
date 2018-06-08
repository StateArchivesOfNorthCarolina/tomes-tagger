from setuptools import setup, setuptools
from tomes_tagger.tagger import __NAME__, __DESCRIPTION__, __URL__, __VERSION__, __AUTHOR__, __AUTHOR_EMAIL__

def doc():
    with open("docs/documentation.md") as d:
        return d.read()
		
setup(
    name = __NAME__,
    description = __DESCRIPTION__,
    url = __URL__,
    version = __VERSION__,
    author = __AUTHOR__,
    author_email = __AUTHOR_EMAIL__,
    packages = setuptools.find_packages(),
    data_files = [("tomes_tagger/lib", ["tomes_tagger/lib/nlp_to_xml.xsd"])],
    python_requires = ">=3",
    license = "LICENSE.txt",
    long_description = doc(),
)
