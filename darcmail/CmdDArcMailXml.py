#!/usr/bin/env python
######################################################################
## $Revision: 1.1 $
## $Date: 2015/07/15 12:24:41 $
## Author: Carl Schaefer, Smithsonian Institution Archives 
######################################################################

import sys
import os
import re
import argparse
from lib2.dm_common import EOL
import lib2.mbox2xml as mbox2xml

XML_WRAP = True
NO_CHUNK = 0
NO_LIMIT = 0
NO_LEVELS = 0
LEVELS = 1
LOG_NAME = 'dm_xml.log.txt'


class DarcMail:

    def __init__(self,
                 account_directory=None,
                 account_name=None,
                 folder_name=None,
                 folder_path=None,
                 chunk_size=NO_CHUNK,
                 levels=LEVELS,
                 max_internal=NO_LIMIT,
                 xml_wrap=XML_WRAP
                 ):
        self.account_directory = account_directory
        self.account_name = account_name
        self.folder_name = folder_name
        self.folder_path = folder_path
        self.chunksize = chunk_size
        self.levels = levels
        self.max_internal = max_internal
        self.xml_wrap = xml_wrap

    @staticmethod
    def log_variables(self, logf):
        logf.write('########## SETTINGS ##########' + EOL)
        logf.write('account: ' + self.account_name + EOL)
        logf.write('account directory: ' + self.account_directory + EOL)
        #  if max_internal == dmc.ALLOCATE_BY_DISPOSITION:
        if self.max_internal == NO_LIMIT:
            logf.write('external content: all attachments' + EOL)
        else:
            logf.write('external content: all attachments > ' + \
                       str(self.max_internal) + ' bytes' +EOL)
        if self.chunksize:
            logf.write('chunk size: ' + str(self.chunksize) + EOL)
        if self.folder_name:
            logf.write('folder: ' + self.folder_name + EOL)
        logf.write('external storage subdirectory levels: ' + \
                   str(self.levels) + EOL)
        logf.write('xml-wrap externally stored content: ' + \
                   str(self.xml_wrap) + EOL)

    def find_mbox_files(self, folder_data, parent):
        for f in os.listdir(parent):
            child = os.path.join(parent, f)
            if os.path.isdir(child):
                self.find_mbox_files(folder_data, child)
            else:
                m = re.match('.*\.mbox$', f)
                if re.match('mbox', f):
                    # This is a readpst mbox structure test to see if it's a placeholder
                    if f.__sizeof__() == 0:
                        self.find_mbox_files(folder_data, child)
                    else:
                        ##  Jeremy M. Gibson (State Archives of North Carolina)
                        ##  2016-16-06 added this section for readpst compatibility
                        head, tail = os.path.split(parent)
                        folder_name = tail
                        folder_mbox = os.path.basename(child)
                        folder_dir = os.path.dirname(child)
                        folder_data.append((folder_name, folder_mbox, folder_dir))

                if m:
                    folder_name = re.sub('\.mbox$', '', f)
                    folder_mbox = os.path.basename(child)
                    folder_dir  = os.path.dirname(child)
                    folder_data.append((folder_name, folder_mbox, folder_dir))

    def check_account_directory(self, dir, mbox_inventory):
        if not os.path.exists(dir):
            print 'account directory ' + dir + ' does not exist'
            return False
        if not os.path.isdir(dir):
            print dir +  ' is not a directory'
            return False
        self.find_mbox_files(mbox_inventory, dir)
        return True

    @staticmethod
    def check_folder(self, mbox_inventory, folder):
        if len(mbox_inventory) == 0:
            print 'There are no .mbox files located under the account directory'
            return False
        folder_count = {}
        for (folder_name, mbox_name, path) in mbox_inventory:
            if folder_name in folder_count.keys():
                folder_count[folder_name] = folder_count[folder_name] + 1
            else:
                folder_count[folder_name] = 1
        multiple = 0
        duplicate_folders = []
        for folder_name in folder_count.keys():
            if folder_count[folder_name] > 1:
                multiple = multiple + 1
                # Jeremy M. Gibson (State Archives of North Carolina)
                # 2016-07-12 find the index of the duplicate folders and store as a list of lists
                duplicate_folders.append([i for i, v in enumerate(mbox_inventory) if v[0] == folder_name])
                print 'There are ' + str(folder_count[folder_name]) + \
                      ' folders named ' + folder_name + ' under the account directory'
        if multiple:
            # Jeremy M. Gibson (State Archives of North Carolina)
            # 2016-07-12 Rename the duplicate .mbox's to make them unique
            # Pattern is [<filename>.mbox, <filename>_001.mbox, <filename>_002.mbox]
            self.rename_dups(duplicate_folders, mbox_inventory)
            return True
        elif folder and folder not in folder_count.keys():
            print 'File ' + folder + '.mbox cannot be found under the account directory'
            return False
        return True

    def rename_dups(self, duplicate_list, inventory):
        """ Automatically rename duplicate folders
        # Jeremy M. Gibson (State Archives of North Carolina)
        # 2016-07-12 Rename the duplicate .mbox's to make them unique

        @type list duplicate_list
        @type list inventory:
        """
        for l in duplicate_list:
            # remove first item from the list
            i = l.pop(0)
            ind = 1
            for fldr in l:
                tup = inventory[fldr]
                original = os.path.join(tup[2], tup[1])
                renamed = os.path.join(tup[2], "{}_{:03d}{}".format(tup[0], ind,'.mbox'))
                renamed_mbox = "{}_{:03d}{}".format(tup[0], ind,'.mbox')
                renamed_fldr = "{}_{:03d}".format(tup[0], ind)
                inventory[fldr] = (renamed_fldr, renamed_mbox, tup[2])
                os.rename(original, renamed)
                ind += 1

    def get_args(self):
        parser = argparse.ArgumentParser(description='convert mbox into XML.')
        parser.add_argument('--account', '-a', dest='account_name', required=True,
                            help='email account name')
        parser.add_argument('--directory', '-d', dest='account_directory', required=True,
                            help='directory to hold all files for this account')
        parser.add_argument('--folder', '-f', dest='folder_name',
                            help='folder name (generate XML only for this one folder)')
        parser.add_argument('--max_internal', '-m', dest='max_internal',
                            type=int, default=NO_LIMIT,
                            help='maximum size in bytes for an internally-stored attachment, default = no limit')
        parser.add_argument('--chunk', '-c', dest='chunk', type=int,
                            default=NO_CHUNK,
                            help='number of messages to put in one output XML file, '+ \
                                 'default = no limit')
        parser.add_argument('--no_subdirectories', '-n', dest='no_subdirectories', action='store_true',
                            help='do NOT make subdirectories to hold external content' + \
                                 '(default = make subdirectories)')

        args = parser.parse_args()
        argdict = vars(args)
        if 'max_internal' in argdict.keys():
            self.max_internal = int(argdict['max_internal'])
        if argdict['no_subdirectories']:
            self.levels = NO_LEVELS
        self.account_name = argdict['account_name'].strip()
        account_directory = os.path.abspath(argdict['account_directory'].strip())
        folder_name = argdict['folder_name']
        if folder_name:
            folder_name = folder_name.strip()
        if 'chunk' in argdict.keys():
            self.chunksize = argdict['chunk']

        mbox_inventory = []
        if not self.check_account_directory(account_directory, mbox_inventory):
            sys.exit(0)
        if not self.check_folder(mbox_inventory, folder_name):
            sys.exit(0)
        if folder_name:
            hit = False
            for (fname, mname, dir) in mbox_inventory:
                if folder_name == fname:
                    hit = True
                    folder_path = os.path.join(dir, mname)
            if not hit:
                # should never get here; was already checked
                print 'no mbox file ' + folder_name + '.mbox under account_directory'

    def convert(self):
        logf = open(os.path.join(self.account_directory, LOG_NAME), 'w')
        self.log_variables(logf)
        mx = mbox2xml.Mbox2Xml(logf,
                               self.account_name,
                               self.account_directory,
                               self.folder_name,
                               self.folder_path,
                               self.max_internal,
                               self.levels,
                               self.chunksize,
                               self.xml_wrap)
        mx.new_output_file()
        mx.xc.xml_header()
        mx.xc.account_head(self.account_name)
        if self.folder_name:
            mx.walk_folder(self.folder_path)
        else:
            mx.walk_account_tree('.', self.account_directory)
        mx.xc.finish_account()
        mx.finish_output_file()
        mx.write_log()
        del mx
        logf.close()

