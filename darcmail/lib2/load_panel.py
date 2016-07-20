#!/usr/bin/env python
######################################################################
## $Revision: 1.3 $
## $Date: 2016/02/11 23:38:42 $
## Author: Carl Schaefer, Smithsonian Institution Archives 
######################################################################

import threading
import time
import sys
import os
import re
import wx
import  wx.lib.scrolledpanel as scrolled
import db_access as dba
import dm_common as dmc
from dm_common import EOL
import dm_wx
from dm_wx import FRAME_WIDTH, FRAME_HEIGHT
import dm_defaults as dmd
import mbox2db
import info_window

ESTIMATED_BYTES_PER_MESSAGE = 75000

####################################################################
## LoadPanel
####################################################################
class LoadPanel (scrolled.ScrolledPanel):

  variable_names = [
    'account',
    'account_dir',
    'folder',
    'folder_cb',
    'max_internal',
    'levels_cb'
#    'wrap_cb',
#    'disposition_radio',
#    'size_radio'
  ]

  name2default   = {
    'account'         : '',
    'account_dir'     : dmd.DEFAULT_ACCOUNT_DIRECTORY_PREFIX,
    'folder'          : '',
    'folder_cb'       : False,
    'max_internal'       : 3,
    'levels_cb'          : True
#    'wrap_cb'            : False,
#    'disposition_radio'  : False,
#    'size_radio'         : True
  }

  name2component = {}

  account         = None
  account_dir     = None
  folder          = None
  folder_cb       = None
  cnx             = None
  username        = None
  database        = None
  host            = None
  external_size   = None

  account_id      = None
  folder_dir      = None

  folder_data     = None
  log_name               = 'dm_load.log.txt'
  external_subdir_levels = 0
  logf                   = None
  xml_wrap               = False
    
  ####################################################################
  def __init__ (self, parent, name):

    wx.ScrolledWindow.__init__ (self, parent=parent, id=-1, name=name)

    normal_font_size = self.GetFont().GetPointSize()  # get the current size
    bigger_font_size = normal_font_size + 3

    sz = wx.BoxSizer(orient=wx.VERTICAL)
    sz.Add((FRAME_WIDTH, 10))

    t1 = wx.StaticText(self, id=-1, label=
        'Load DArcMail Data')
    t1.SetFont(wx.Font(bigger_font_size, wx.SWISS, wx.NORMAL, wx.BOLD))
    sz.Add(t1, 0, wx.ALIGN_CENTER, 5)

    sz.Add((FRAME_WIDTH, 15))

    sz.Add(dm_wx.Paths(self, 'Load'), 0, wx.ALIGN_LEFT, 5)
    sz.Add((FRAME_WIDTH, 10))

    sz.Add(dm_wx.Limits(self, 'Load'), 0, wx.ALIGN_LEFT, 5)
    sz.Add((FRAME_WIDTH, 10))

    sz.Add(dm_wx.ExternalStorage(self, 'DArcMail'), 0, wx.ALIGN_LEFT, 5)
    sz.Add((FRAME_WIDTH, 10))

    sz.Add(dm_wx.ActionButtons(self, 'Load Data'), 0, wx.ALIGN_CENTER, 5)
    sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
    sizer.Add((20,FRAME_HEIGHT))
    sizer.Add(sz, 1, wx.EXPAND)
    self.SetSizer(sizer)
    self.SetupScrolling()

    for v in self.variable_names:
      self.name2component[v] = self.FindWindowByName(v)
    self.name2component['max_internal_label'] = self.FindWindowByName('max_internal_label')

    self.ResetVariables()

    for b in dm_wx.button_names:
      self.name2component[b] = self.FindWindowByName(b)

    self.name2component['reset_button'].Bind(wx.EVT_LEFT_UP, self.ExecuteReset)
    self.name2component['go_button'].Bind(wx.EVT_LEFT_UP, self.ValidateVariablesAndGo)

    wx.EVT_CHECKBOX(self, self.name2component['folder_cb'].GetId(),
        self.FolderSpec)

    if dmc.ALLOW_ALLOCATION_CHOICE:
      self.Bind(wx.EVT_RADIOBUTTON, self.ExternalStorageRadio)

  ####################################################################
  def ResetVariables (self):
    for v in self.variable_names:
      if v == 'account_dir':
        self.name2component[v].SetPath(self.name2default[v])
      elif v == 'max_internal':
        self.name2component[v].SetSelection(self.name2default[v])
      else:
        self.name2component[v].SetValue(self.name2default[v])
    cb = self.name2component['folder_cb']
    fl = self.name2component['folder']
    if cb.GetValue():
      fl.Enable(True)
    else:
      fl.SetValue('')
      fl.Enable(False)
      fl.Refresh()
    if dmc.ALLOW_ALLOCATION_CHOICE:
      dr = self.name2component['disposition_radio']
      if dr.GetValue():
        self.name2component['max_internal_label'].Hide()
        self.name2component['max_internal'].Hide()
      else:
        self.name2component['max_internal_label'].Show()
        self.name2component['max_internal'].Refresh()
        self.name2component['max_internal'].Show()
      self.Layout()

  ####################################################################
  def FolderSpec (self, event):
    cb = self.name2component['folder_cb']
    fl = self.name2component['folder']
    if cb.GetValue():
      fl.Enable(True)
      fl.Refresh()
    else:
      fl.SetValue('')
      fl.Enable(False)
      fl.Refresh()

  ####################################################################
  def ExternalStorageRadio (self, event):
    dr = self.name2component['disposition_radio']
    if dr.GetValue():
      self.name2component['max_internal_label'].Hide()
      self.name2component['max_internal'].Hide()
    else:
      self.name2component['max_internal_label'].Show()
      self.name2component['max_internal'].Show()
    self.Layout()

  ####################################################################
  def ExecuteReset (self, event):
    self.ResetVariables()
    self.GetParent().SetFocus()

  ####################################################################
  def ExecuteExit (self, event):
    # self is a
    #   wx.Panel within a
    #       wx.Notebook within a
    #             wx.Frame
    self.GetParent().GetParent().Close()

  ####################################################################
  def LogVariables (self):
    self.logf.write('########## SETTINGS ##########' + EOL)
    self.logf.write('account: ' + self.account + EOL)
    self.logf.write('account directory: ' + self.account_dir + EOL)
    if self.max_internal == -1:
      self.logf.write('external content: all attachments' + EOL)
    else:
      self.logf.write('max size for internal content: ' + \
        str(self.max_internal) + EOL)
    self.logf.write('external storage subdirectory levels: ' + \
        str(self.external_subdir_levels) + EOL)
    self.logf.write('xml-wrap externally stored content: ' + \
        str(self.xml_wrap) + EOL)

    if self.folder_cb:
      self.logf.write('do only one mbox: ' + self.folder + '.mbox' + EOL)
    self.logf.write(EOL)

  ####################################################################
  def ValidateVariablesAndGo (self, event):
    ready = True

    msg = dm_wx.ValidateDirectory(self, self.name2component['account_dir'].GetPath())
    if msg != '':
      md = wx.MessageDialog(parent=self, message=msg, caption='Error',
          style=wx.OK|wx.ICON_EXCLAMATION)
      retcode = md.ShowModal()
      ready = False
      # no point in continuing
      return
    msg = dm_wx.ValidateAccount(self, self.name2component['account'].GetValue())
    if msg != '':
      md = wx.MessageDialog(parent=self, message=msg, caption='Error',
          style=wx.OK|wx.ICON_EXCLAMATION)
      retcode = md.ShowModal()
      ready = False
      # no point in continuing
      return

    # an account name was specified; it may or may not exist
    # an account directory was specified and is externally valid; it may or may not be
    #  recorded in the db
    # Now check to see that either (a) neither the account name nor the account directory
    #  appears in the database; or (b) they both appear in the database and are associated
    #  with each other

    self.account_id = dba.get_account_id(self.cnx, self.account, make=False)
    acc_info = dba.lookup_account_directory (self.cnx, self.account_dir)
    acc_names = []
    for (id, name, dir) in acc_info:
      acc_names.append(name)
    if self.account_id == None and len(acc_names) > 0:
      if len(acc_names) > 1:
        msg = self.account_dir + ' is associated with different accounts: ' + \
          ', '.join(acc_names)
      else:
        msg = self.account_dir + ' is associated with a different account: ' + \
          ', '.join(acc_names)
      md = wx.MessageDialog(parent=self, message=msg, caption='Error',
          style=wx.OK|wx.ICON_EXCLAMATION)
      retcode = md.ShowModal()
      ready = False
    elif self.account_id and (self.account not in acc_names):
      msg = 'Account ' + self.account + ' has already been ' + \
          'assigned a different directory. ' + \
          'If you want to assign directory ' + self.account_dir + ' ' + \
          'You must first ' + \
          'delete the existing account and all its data'
      md = wx.MessageDialog(parent=self, message=msg, caption='Error',
          style=wx.OK|wx.ICON_EXCLAMATION)
      retcode = md.ShowModal()
      ready = False

    if ready and self.account_id == None:
      msg = 'No account ' + self.account + '; do you want to create it?'
      md = wx.MessageDialog(parent=self, message=msg, caption='Info',
          style=wx.CANCEL|wx.OK|wx.ICON_EXCLAMATION)
      md.SetOKLabel('Create Account?')
      retcode = md.ShowModal()
      if retcode == wx.ID_OK:
        self.account_id = dba.get_account_id(self.cnx, self.account, make=True)
        ## We won't commit here; it will happen after the first message is committed
        ## or else, not at all. This will prevent having committed an account
        ## name that has no associated directory
        #self.cnx.commit()
        if self.account_id == None:
          msg = 'Cannot create account ' + self.account
          md = wx.MessageDialog(parent=self, message=msg, caption='Error',
              style=wx.OK|wx.ICON_EXCLAMATION)
          retcode = md.ShowModal()
          ready = False
          return
        else:
          dba.update_account_directory(self.cnx, self.account_id, self.account_dir)
      else:
        ready = False
        # no sense proceeding if missing account will not be created
        return

    # at this point, self.account_id is valid
    folder_names_in_db = dba.get_folder_names_for_account(self.cnx, self.account_id)
    self.folder_data = []
    dm_wx.FindMboxFiles(self, self.folder_data, self.account_dir)
    if len(self.folder_data) == 0:
      msg = 'There are no mbox files among the descendants of ' + \
        'account directory ' + self.account_dir
      md = wx.MessageDialog(parent=self, message=msg, caption='Error',
          style=wx.OK|wx.ICON_EXCLAMATION)
      retcode = md.ShowModal()
      ready = False
    else:
      dups = self.check_for_dup_folder_names(self.folder_data)
      if len(dups) > 0:
        msg = 'Folder names must be unique in an account. ' + \
            'These folder names are used more than one time in ' + \
            'the account directory:' + EOL + EOL.join(dups)
        md = wx.MessageDialog(parent=self, message=msg, caption='Error',
            style=wx.OK|wx.ICON_EXCLAMATION)
        retcode = md.ShowModal()
        ready = False
      else:
        pass

    msg = dm_wx.ValidateLimits(self, self.name2component['folder_cb'].GetValue(),
        self.name2component['folder'].GetValue())
    if msg != '':
      md = wx.MessageDialog(parent=self, message=msg, caption='Error',
          style=wx.OK|wx.ICON_EXCLAMATION)
      retcode = md.ShowModal()
      ready = False
    else:
      if self.folder:
        (fname, mbox, fdir, fsz, fid) = dm_wx.FindFolderName(self.folder_data, self.folder)
        if fname == None:
          msg = 'Cannot find folder mbox ' + self.folder + \
              '.mbox under directory ' + self.account_dir
          md = wx.MessageDialog(parent=self, message=msg, caption='Error',
              style=wx.OK|wx.ICON_EXCLAMATION)
          retcode = md.ShowModal()
          ready = False
        elif fid != None:
          msg = 'Folder ' + self.folder + \
              ' is already in the database; you must delete it before it can be reloaded.'
          md = wx.MessageDialog(parent=self, message=msg, caption='Error',
             style=wx.OK|wx.ICON_EXCLAMATION)
          retcode = md.ShowModal()
          ready = False
        else:
          self.folder_dir = fdir
      elif len(folder_names_in_db) > 0:
        msg = 'This account already has at least one folder loaded.' + EOL + \
          'You cannot load ALL folders in the account directory ' + EOL + \
          'unless you first delete all folders from the database.'
        md = wx.MessageDialog(parent=self, message=msg, caption='Error',
            style=wx.OK|wx.ICON_EXCLAMATION)
        retcode = md.ShowModal()
        ready = False

    if dmc.ALLOW_ALLOCATION_CHOICE:
      if self.name2component['disposition_radio'].GetValue():
        # -1 for max_internal will signal external storage by
        # disposition==attachment rather than by size
        self.max_internal = dmc.ALLOCATE_BY_DISPOSITION
      elif self.name2component['size_radio'].GetValue():
        mi = self.name2component['max_internal']
        self.max_internal = int(mi.GetString(mi.GetCurrentSelection()))
    else:
       mi = self.name2component['max_internal']
       self.max_internal = int(mi.GetString(mi.GetCurrentSelection()))

    if ready:
      if self.name2component['levels_cb'].GetValue():
        self.external_subdir_levels = 1
# No choice for XML wrap
#      self.xml_wrap = self.name2component['wrap_cb'].GetValue()
      self.logf = open(os.path.join(self.account_dir, self.log_name) , 'w')
      self.LogVariables()

#      load_thread = threading.Thread(target=self.load_data, args=() )
#      load_thread.start()

      self.load_data()

      self.ResetVariables()
      self.SetFocus()
      ## not sure why this return statement is needed, but the call to load_data is sometimes
      ## repeated ...
      return

  ######################################################################
  def check_for_dup_folder_names(self, folder_data):
    fld_names = {}
    for (folder_name, folder_mbox, folder_dir, folder_size, folder_id) \
        in folder_data:
      if folder_name not in fld_names.keys():
        fld_names[folder_name] = 1
      else:
        fld_names[folder_name] = fld_names[folder_name] + 1
    dups = []
    for folder_name in fld_names.keys():
      if fld_names[folder_name] > 1:
        dups.append(folder_name)
    return dups

  ######################################################################
  def load_data (self):

    self.FindWindowByName('go_button').Disable()

    mbdb = mbox2db.Mbox2Db(
        self.cnx,
        self.logf,
        self.account,
        self.account_dir,
        self.account_id,
        self.folder,
        self.folder_dir,
        self.max_internal,
        self.external_subdir_levels,
        self.xml_wrap)


    fsz = 0
    for (folder_name, folder_mbox, folder_dir, folder_size,
        folder_id) in self.folder_data:
      if self.folder:
        if self.folder == folder_name:
          fsz = folder_size
      else:
        fsz = fsz + folder_size
    estimated_total_messages = int(fsz/ESTIMATED_BYTES_PER_MESSAGE)
    self.pd = wx.ProgressDialog('Loading mbox data into DArcMail',
      'Loading mbox into DArcMail',
      maximum=estimated_total_messages, parent=self, style=wx.PD_APP_MODAL) 
    mbdb.set_progress_dialog(self.pd, estimated_total_messages)

    wait = wx.BusyCursor()

    if self.folder:
      folder_relative_path = os.path.join('.',
          self.folder_dir[len(self.account_dir)+1:])
      mbox_file_name = os.path.join(self.folder_dir, self.folder + '.mbox')
      self.folder_id  = dba.get_folder_id(self.cnx, self.account_id,
          self.folder, folder_relative_path, make=True)
      mbdb.do_mbox_folder(self.folder_id,
          os.path.join(self.folder_dir, mbox_file_name))
    else:
      mbdb.walk_account_tree('.', self.account_dir)
    mbdb.write_log()

    self.pd.Destroy()
    del wait
    del mbdb

    self.logf.close()
    self.logf = open(os.path.join(self.account_dir, self.log_name))
    message = self.logf.read()
    self.logf.close()
    summary_info = info_window.InfoWindow(self, 'Load Summary', message)
    summary_info.Show(True)
    summary_info.SetFocus()

    self.account         = None
    self.account_dir     = None
    self.folder          = None
    self.folder_cb       = None
    self.max_internal    = None
    self.account_id      = None
    self.folder_dir      = None
    self.folder_data     = None
    self.external_subdir_levels = 0
    self.xml_wrap        = None

    self.FindWindowByName('go_button').Enable()
