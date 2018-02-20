from distutils.core import setup

setup(
    name="tomes_tool",
    version="0.0.1",
    packages=["tomes_tool", "tomes_tool.lib"], 
    url="https://github.com/StateArchivesOfNorthCarolina/tomes_tool",
    license="LICENSE.txt",
    author="Nitin Arora",
    author_email="nitin.a.arora@ncdcr.gov",
    description="Part of the TOMES project: creates a 'tagged' version of an EAXS file.",
    python_requires=">=3",
    install_requires=["beautifulsoup4>=4.5.3",
        "html5lib>=0.9",
        "lxml>=3.7.2",
        "openpyxl>=2.4.8",
        "plac>=0.9.6",
        "pycorenlp>=0.3.0",
        "PyYAML>=3.12",
        ],
)
