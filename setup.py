from setuptools import setup, setuptools

def doc():
    with open("docs/documentation.md") as d:
        return d.read()
		
setup(
    name="tomes_tagger",
    version="0.0.1",
    packages=setuptools.find_packages(),
    package_data={"tomes_tagger.lib": ["nlp_to_xml.xsd"]},
    include_package_data=True,
    python_requires=">=3",
    url="https://github.com/StateArchivesOfNorthCarolina/tomes-tagger",
    license="LICENSE.txt",
    author="Nitin Arora",
    author_email="nitin.a.arora@ncdcr.gov",
    description="Part of the TOMES project: creates a 'tagged' version of an EAXS file.",
    long_description=doc(),
)

