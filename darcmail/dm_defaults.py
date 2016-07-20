#!/usr/bin/env python
######################################################################
## $Revision: 1.3 $
## $Date: 2016/02/11 23:38:42 $
## Author: Carl Schaefer, Smithsonian Institution Archives 
######################################################################

## for Login page (logon_panel.py)
DEFAULT_USER     = ''
DEFAULT_HOST     = 'localhost'
DEFAULT_PASSWORD = ''
DEFAULT_DATABASE = 'DArcMail'

## for partial path to account directories (load_panel.py)
DEFAULT_ACCOUNT_DIRECTORY_PREFIX = '.'

## for partial path to export directories (export_panel.py)
DEFAULT_EXPORT_DIRECTORY_PREFIX = '.'

## permissions for creating external content
## 0775 owner&group: read,write,execute/navigate; world:read,execute/navigate
## 0664 owner&group: read,write; world: read 
EXTERNAL_CONTENT_DIRECTORY_PERMISSIONS = 0775
EXTERNAL_CONTENT_FILE_PERMISSIONS      = 0664

## permissions for XML export files created in the account_directory (dm2xml.py)
XML_FILE_PERMISSIONS = 0664

VERSION='v1.0'

DEFAULT_HIGHLITE_COLOR = '#FF00FF'  # magenta
#DEFAULT_HIGHLITE_COLOR = '#88FF00'  # lime green
#DEFAULT_HIGHLITE_COLOR = '#FF6666'  # light red
