#!/usr/bin/env python
######################################################################
## $Revision: 1.1 $
## $Date: 2015/07/15 12:24:41 $
## Author: Carl Schaefer, Smithsonian Institution Archives 
######################################################################

import time
import sys
import os
import re
import wx
import  wx.lib.scrolledpanel as scrolled
import dm_common as dmc
from dm_common import EOL
import dm_wx
from dm_wx import FRAME_WIDTH, FRAME_HEIGHT
import dm_defaults as dmd
import mbox2xml
import info_window

####################################################################
## DMXmlPanel
####################################################################
class DMXmlPanel (scrolled.ScrolledPanel):

  variable_names = [
    'account',
    'account_dir',
    'folder',
    'folder_cb',
    'chunksize',
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
    'chunksize'       : 0,
    'folder'          : '',
    'folder_cb'       : False,
    'max_internal'    : 3,
    'levels_cb'       : True
#    'wrap_cb'         : True,
#    'disposition_radio' : True,
#    'size_radio'        : False
  }

  log_name               = 'dm_xml.log.txt'
  xml_wrap               = True
 
  ####################################################################
  def __init__ (self, parent, name):

    wx.ScrolledWindow.__init__ (self, parent=parent, id=-1, name=name)

    self.name2component = {}
    self.account          = None
    self.account_dir      = None
    self.folder           = None
    self.folder_dir       = None
    self.folder_cb        = None
    self.logf             = None
    self.chunksize        = None
    self.folder_data      = []
    self.levels_cb        = None
    self.max_internal     = None
#    self.max_internal_label = None
#    self.disposition_radio  = None
#    self.size_radio         = None
    self.external_subdir_levels = 0

    normal_font_size = self.GetFont().GetPointSize()  # get the current size
    bigger_font_size = normal_font_size + 3

    sz = wx.BoxSizer(orient=wx.VERTICAL)
    sz.Add((FRAME_WIDTH, 10))

    t1 = wx.StaticText(self, id=-1, label=
        'convert .mbox Files to XML')
    t1.SetFont(wx.Font(bigger_font_size, wx.SWISS, wx.NORMAL, wx.BOLD))
    sz.Add(t1, 0, wx.ALIGN_CENTER, 5)

    sz.Add((FRAME_WIDTH, 15))

    sz.Add(dm_wx.Paths(self, 'Xml'), 0, wx.ALIGN_LEFT, 5)
    sz.Add((FRAME_WIDTH, 10))

    sz.Add(dm_wx.Limits(self, 'Xml'), 0, wx.ALIGN_LEFT, 5)
    sz.Add((FRAME_WIDTH, 10))

    sz.Add(dm_wx.ExternalStorage(self, 'DArcMailXml'), 0, wx.ALIGN_LEFT, 5)
    sz.Add((FRAME_WIDTH, 10))

    sz.Add(dm_wx.ActionButtons(self, 'convert to XML'), 0, wx.ALIGN_CENTER, 5)
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
      elif v == 'chunksize':
        self.name2component[v].SetSelection(self.name2default[v])
      elif v == 'max_internal':
        self.name2component[v].SetSelection(self.name2default[v])
      else:
        self.name2component[v].SetValue(self.name2default[v])
    fcb = self.name2component['folder_cb']
    fl = self.name2component['folder']
    if fcb.GetValue():
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
#    if self.max_internal == dmc.ALLOCATE_BY_DISPOSITION:
    if self.max_internal == 0:
      self.logf.write('external content: all attachments' + EOL)
    else:
      self.logf.write('external content: all attachments > ' + \
        str(self.max_internal) + ' bytes' +EOL)
    if self.chunksize:
      self.logf.write('chunk size: ' + str(self.chunksize) + EOL)
    if self.folder:
      self.logf.write('folder: ' + self.folder + EOL)
    self.logf.write('external storage subdirectory levels: ' + \
        str(self.external_subdir_levels) + EOL)
    self.logf.write('xml-wrap externally stored content: ' + \
        str(self.xml_wrap) + EOL)

  ####################################################################
  def FindFolders (self, dir):
    for f in os.listdir(dir):
      path = os.path.join(dir, f)
      if os.path.isdir(path):
        self.FindFolders(path)
      else:
        m = re.match('.+\.mbox$', f, re.I)
        if m:
          folder = re.sub('\.mbox$', '', f, flags=re.I)
          self.folder_data.append((folder, path))

  ######################################################################
  def check_for_dup_folder_names(self, folder_data):
    fld_names = {}
    for (folder_name, folder_dir) in folder_data:
      if folder_name not in fld_names.keys():
        fld_names[folder_name] = 1
      else:
        fld_names[folder_name] = fld_names[folder_name] + 1
    dups = []
    for folder_name in fld_names.keys():
      if fld_names[folder_name] > 1:
        dups.append(folder_name)
    return dups

  ####################################################################
  def ValidateVariablesAndGo(self, event):
    ready = True

    self.account = self.name2component['account'].GetValue()
    if self.account:
      self.account = self.account.strip()
    if not self.account:
      msg = 'You must specify a name for the account'
      md = wx.MessageDialog(parent=self, message=msg, caption='Error',
          style=wx.OK|wx.ICON_EXCLAMATION)
      retcode = md.ShowModal()
      ready = False
      # no sense checking further if the account does not exist
      return

    self.account_dir = self.name2component['account_dir'].GetPath()
    msg = dm_wx.ValidateDirectory(self, self.account_dir)
    if msg != '':
      md = wx.MessageDialog(parent=self, message=msg, caption='Error',
          style=wx.OK|wx.ICON_EXCLAMATION)
      retcode = md.ShowModal()
      ready = False
      # no point in continuing
      return

    self.folder_data = []
    self.FindFolders(self.account_dir)
    if len(self.account_dir) < 1:
      msg = 'There are no mbox files under the account directory ' + \
        self.account_dir
      md = wx.MessageDialog(parent=self, message=msg, caption='Error',
          style=wx.OK|wx.ICON_EXCLAMATION)
      retcode = md.ShowModal()
      ready = False
      # no point in continuing
      return

    dups = self.check_for_dup_folder_names(self.folder_data)
    if len(dups) > 0:
      msg = 'Folder names must be unique in an account. ' + \
          'These folder names are used more than one time in ' + \
          'the account directory:' + EOL + EOL.join(dups)
      md = wx.MessageDialog(parent=self, message=msg, caption='Error',
          style=wx.OK|wx.ICON_EXCLAMATION)
      retcode = md.ShowModal()
      ready = False
      return

    msg = dm_wx.ValidateLimits(self, self.name2component['folder_cb'].GetValue(),
        self.name2component['folder'].GetValue())
    if msg != '':
      md = wx.MessageDialog(parent=self, message=msg, caption='Error',
          style=wx.CANCEL|wx.ICON_EXCLAMATION)
      retcode = md.ShowModal()
      ready = False
      return

    if self.folder:
      matching_folders = []
      for (f, mbox_path) in self.folder_data:
        if f == self.folder:
          matching_folders.append((f, mbox_path))
      n = len(matching_folders)
      if n == 1:
        self.folder_dir = matching_folders[0][1]
      else:
        if n == 0:
          msg = 'There is no mbox file named ' + self.folder + '.mbox' + \
            ' under the account directory'
        elif n > 1:
          msg = 'There is more than one mbox file named ' + self.folder + '.mbox' + \
            ' under the account directory'
    if msg != '':
      md = wx.MessageDialog(parent=self, message=msg, caption='Error',
          style=wx.CANCEL|wx.ICON_EXCLAMATION)
      retcode = md.ShowModal()
      ready = False
      return

#    if dmc.ALLOW_ALLOCATION_CHOICE:
#      if self.name2component['disposition_radio'].GetValue():
#        # -1 for max_internal will signal external storage by
#        # disposition==attachment rather than by size
#        self.max_internal = dmc.ALLOCATE_BY_DISPOSITION
#      elif self.name2component['size_radio'].GetValue():
#        mi = self.name2component['max_internal']
#        self.max_internal = int(mi.GetString(mi.GetCurrentSelection()))

    mi = self.name2component['max_internal']
    if mi.GetCurrentSelection() == 0:
      self.max_internal = 0
    else:
      self.max_internal = int(mi.GetString(mi.GetCurrentSelection()))

    cksizes = [0, 1000, 5000, 10000]
    ci = self.name2component['chunksize']
    self.chunksize = cksizes[ci.GetCurrentSelection()]

    if ready:
      if self.name2component['levels_cb'].GetValue():
        self.external_subdir_levels = 1
# No choice for XML wrap
#      self.xml_wrap = self.name2component['wrap_cb'].GetValue()
      self.logf = open(os.path.join(self.account_dir, self.log_name) , 'w')
      self.LogVariables()
      self.convert_data()
      self.ResetVariables()
      self.SetFocus()

  ######################################################################
  def convert_data (self):

    self.FindWindowByName('go_button').Disable()

    mx = mbox2xml.Mbox2Xml(
        self.logf,
        self.account,
        self.account_dir,
        self.folder,
        self.folder_dir,
        self.max_internal,
        self.external_subdir_levels,
        self.chunksize,
        self.xml_wrap)
    
#    self.pd = wx.ProgressDialog('Converting .mbox file to XML',
#      'Converting .mbox file to XML',
#      maximum=100, parent=self, style=wx.PD_APP_MODAL) 
    mx.new_output_file()
    mx.xc.xml_header()
    mx.xc.account_head(self.account)

    wait = wx.BusyCursor()

    if self.folder:
      mx.walk_folder(self.folder_dir)
    else:
      mx.walk_account_tree('.', self.account_dir)
    mx.xc.finish_account()
    mx.finish_output_file()

#    self.pd.Destroy()
    mx.write_log()

    del mx    
    del wait

    self.logf.close()
    self.logf = open(os.path.join(self.account_dir, self.log_name))
    message = self.logf.read()
    self.logf.close()
    summary_info = info_window.InfoWindow(self, 'convert mbox to XML Summary', message)
    summary_info.Show(True)
    summary_info.SetFocus()

    self.account          = None
    self.account_dir      = None
    self.folder           = None
    self.folder_dir       = None
    self.folder_cb        = None
    self.chunksize        = None
    self.folder_data      = []
    self.levels_cb        = None
    self.max_internal     = None
    self.external_subdir_levels = 0

    self.FindWindowByName('go_button').Enable()
