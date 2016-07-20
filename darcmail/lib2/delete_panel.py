#!/usr/bin/env python
######################################################################
## $Source: /Users/Carl/cvsroot/DArcMail/src/python/delete_panel.py,v $
## $Revision: 1.2 $
## $Date: 2016/02/11 23:38:42 $
## Author: Carl Schaefer, Smithsonian Institution Archives 
######################################################################

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
import delete_data
import stop_watch
import info_window

####################################################################
## DeletePanel
####################################################################
class DeletePanel (scrolled.ScrolledPanel):

  variable_names = [
    'account',
    'folder',
    'folder_cb'
#    'rmex_cb'
  ]

  name2default   = {
    'account'         : '',
    'folder'          : '',
    'folder_cb'       : False
#    'rmex_cb'         : True
  }

  log_name        = 'dm_delete.log.txt'

  ####################################################################
  def __init__ (self, parent, name):

    wx.ScrolledWindow.__init__ (self, parent=parent, id=-1, name=name)

    self.name2component  = {}
    self.account         = None
    self.account_dir     = None
    self.account_id      = None
    self.folder          = None
    self.folder_cb       = None
    self.rmex_cb         = True
    self.logf            = None
    self.cnx             = None
    self.username        = None
    self.host            = None
    self.database        = None
    self.folder_data     = None

    normal_font_size = self.GetFont().GetPointSize()  # get the current size
    bigger_font_size = normal_font_size + 3

    sz = wx.BoxSizer(orient=wx.VERTICAL)
    sz.Add((FRAME_WIDTH, 10))

    t1 = wx.StaticText(self, id=-1, label=
        'Delete DArcMail Data')
    t1.SetFont(wx.Font(bigger_font_size, wx.SWISS, wx.NORMAL, wx.BOLD))
    sz.Add(t1, 0, wx.ALIGN_CENTER, 5)

    sz.Add((FRAME_WIDTH, 15))

    sz.Add(dm_wx.Paths(self, 'Delete'), 0, wx.ALIGN_LEFT, 5)
    sz.Add((FRAME_WIDTH, 10))

    sz.Add(dm_wx.Limits(self, 'Delete'), 0, wx.ALIGN_LEFT, 5)
    sz.Add((FRAME_WIDTH, 10))

    sz.Add(dm_wx.ActionButtons(self, 'Delete Data'), 0, wx.ALIGN_CENTER, 5)
    sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
    sizer.Add((20,FRAME_HEIGHT))
    sizer.Add(sz, 1, wx.EXPAND)
    self.SetSizer(sizer)
    self.SetupScrolling()

    for v in self.variable_names:
      self.name2component[v] = self.FindWindowByName(v)

    self.ResetVariables()

    for b in dm_wx.button_names:
      self.name2component[b] = self.FindWindowByName(b)

    self.name2component['reset_button'].Bind(wx.EVT_LEFT_UP, self.ExecuteReset)
    self.name2component['go_button'].Bind(wx.EVT_LEFT_UP, self.ValidateVariablesAndGo)

    wx.EVT_CHECKBOX(self, self.name2component['folder_cb'].GetId(),
        self.FolderSpec)

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
  def LogVariables(self):
    self.logf.write('########## SETTINGS ##########' + EOL)
    self.logf.write('account: ' + self.account + EOL)
    self.logf.write('account directory: ' + self.account_dir + EOL)
    self.logf.write('remove externally stored content: ' + \
        str(self.rmex_cb) + EOL)
    self.logf.write(EOL)

    if self.folder_cb:
      self.logf.write('do only one folder: ' + self.folder + '.mbox' + EOL)
    else:
      self.logf.write('delete all folders in account: True' + EOL)
    self.logf.write(EOL)

  ####################################################################
  def ValidateVariablesAndGo(self, event):
    ready = True

    msg = dm_wx.ValidateAccount(self, self.name2component['account'].GetValue())
    if msg != '':
      md = wx.MessageDialog(parent=self, message=msg, caption='Error',
          style=wx.OK|wx.ICON_EXCLAMATION)
      retcode = md.ShowModal()
      ready = False
    else:
      self.account_id = dba.get_account_id(self.cnx, self.account, make=False)
      if self.account_id == None:
        msg = 'No account ' + self.account
        md = wx.MessageDialog(parent=self, message=msg, caption='Error',
            style=wx.OK|wx.ICON_EXCLAMATION)
        retcode = md.ShowModal()
        ready = False
        # no sense checking further if the account does not exist
        return

    self.account_dir = dba.get_account_directory(self.cnx, self.account_id)
    msg = dm_wx.ValidateDirectory(self, self.account_dir)
    if msg != '':
      md = wx.MessageDialog(parent=self, message=msg, caption='Error',
          style=wx.OK|wx.ICON_EXCLAMATION)
      retcode = md.ShowModal()
      ready = False
      # no point in continuing
      return

    self.folder_data = []
    dm_wx.FindMboxFiles(self, self.folder_data, self.account_dir)

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
        elif fid == None:
          msg = 'Folder ' + self.folder + ' is not in the database' + EOL
          md = wx.MessageDialog(parent=self, message=msg, caption='Error',
             style=wx.OK|wx.ICON_EXCLAMATION)
          retcode = md.ShowModal()
          ready = False
        else:
          self.folder_dir = fdir
#    self.rmex_cb = self.name2component['rmex_cb'].GetValue()

    if ready:
      self.logf = open(os.path.join(self.account_dir, self.log_name) , 'w')
      self.LogVariables()
      self.delete_data()
      self.ResetVariables()
      self.SetFocus()

  ######################################################################
  def delete_data (self):

    sw = stop_watch.StopWatch()

    self.pd = wx.ProgressDialog('Deleting data from DArcMail',
      'Deleting data from DArcMail',
      maximum=100, parent=self, style=wx.PD_APP_MODAL) 

    dd = delete_data.DeleteData(self.cnx, self.account, self.account_dir,
        self.account_id, self.folder, self.rmex_cb)
    folders = dba.get_folders_for_account(self.cnx, self.account_id)
    for dbf in folders:
      if not self.folder or dbf.folder_name == self.folder:
        dd.delete_one_folder(dbf)
        self.cnx.commit()
    dd.delete_addresses_and_names()
    if not self.folder:
      dba.delete_account(self.cnx, self.account_id)
    self.cnx.commit()

    del dd

    self.logf.write(EOL + '########## ELAPSED TIME ##########' + EOL)
    self.logf.write(sw.elapsed_time() + EOL)

    self.pd.Destroy()
    self.logf.close()
    self.logf = open(os.path.join(self.account_dir, self.log_name))
    message = self.logf.read()
    self.logf.close()
    summary_info = info_window.InfoWindow(self, 'Delete Summary', message)
    summary_info.Show(True)
    summary_info.SetFocus()

    self.account         = None
    self.account_dir     = None
    self.account_id      = None
    self.folder          = None
    self.folder_cb       = None
    self.rmex_cb         = True
    self.folder_data     = None
