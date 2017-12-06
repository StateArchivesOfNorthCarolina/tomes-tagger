from distutils.core import setup

setup(
    name='docker_tmstl',
    version='0.0.1',
    package_dir={'docker_tomes': 'lib'},
    packages=['lib', 'lib.stanford_edu', '_other', '_other.mets', '_other.mets_templates', '_other.old',
              '_other.signatures'],
    url='',
    license='LICENSE.txt',
    author='Nitin Arora',
    author_email='nitin.arora@ncdcr.gov',
    description='The eaxs to tagged portion of the TOMES process',
    install_requires=[
        "beautifulsoup4">="4.5.3",
        "lxml" >= "3.7.2",
        "openpyxl" >= "2.4.8",
        "plac" >= " 0.9.6",
        "pycorenlp" >= "0.3.0",
        "PyYAML" >= "3.12"
    ]
)
