#!/usr/bin/env python
######################################################################
## $Revision: 1.2 $
## $Date: 2016/02/11 23:38:42 $
## Author: Carl Schaefer, Smithsonian Institution Archives 
######################################################################

import time
import sys
import os
import re
import wx
from wx import DirPickerCtrl
import  wx.lib.scrolledpanel as scrolled
import db_access as dba
import dm_common as dmc
import dm_wx
from dm_wx import FRAME_WIDTH, FRAME_HEIGHT, FRAME_XPOS, FRAME_YPOS
import load_panel
import export_panel
import delete_panel
import logon_panel
import browse_panel

######################################################################
class DMFrame(wx.Frame):

  ####################################################################
  def __init__(self, parent, title):
    wx.Frame.__init__(self, parent, -1, title,
        pos=(FRAME_XPOS, FRAME_YPOS), size=(FRAME_WIDTH, FRAME_HEIGHT))

    self.qb = wx.ToggleButton(self, id=-1, label='Quit', name='quit_button')
    self.qb.Bind(wx.EVT_LEFT_UP, self.ExecuteExit)

    self.gp = logon_panel.LogonPanel(self, 'login_panel')
    self.Bind(self.gp.EVT_LOGIN, self.login_handler)

    self.lb = wx.ToggleButton(self, id=-1, label='Load',   name='load_button')
    self.db = wx.ToggleButton(self, id=-1, label='Delete', name='delete_button')
    self.xb = wx.ToggleButton(self, id=-1, label='Export', name='export_button')
    self.bb = wx.ToggleButton(self, id=-1, label='Browse', name='browse_button')

    self.lp = load_panel.LoadPanel(self,     'load_panel')
    self.dp = delete_panel.DeletePanel(self, 'delete_panel')
    self.bp = browse_panel.BrowsePanel(self, 'browse_panel')
    self.xp = export_panel.ExportPanel(self, 'export_panel')

    self.bs_and_ps = []
    for handle in ['load', 'delete', 'export', 'browse']:
      self.bs_and_ps.append( (
          self.FindWindowByName(handle+'_button'),
          self.FindWindowByName(handle+'_panel')
      ) )

    self.buttons = wx.BoxSizer(wx.HORIZONTAL)
    
    self.buttons.Add(self.qb, 0, wx.ALL, 3)
    for (b, p) in self.bs_and_ps:
      self.Bind(wx.EVT_TOGGLEBUTTON, self.OnToggle, b)
      self.buttons.Add(b, 0, wx.ALL, 3)

    self.top_sizer = wx.BoxSizer(orient=wx.VERTICAL)
    self.top_sizer.Add(self.buttons, 0, wx.LEFT|wx.TOP, 3)
    self.top_sizer.Add(self.gp, 1, wx.EXPAND)
    for (b, p) in self.bs_and_ps:
      self.top_sizer.Add(p, 1, wx.EXPAND)
      b.Hide()
      p.Hide()
    self.gp.Show()
    self.SetSizer(self.top_sizer)
    self.Layout()

  ####################################################################
  def login_handler (self, event):
    for name in ['load_panel', 'delete_panel', 'browse_panel',
        'account_search', 'message_search', 'address_search', 'results_panel']:
      self.FindWindowByName(name).cnx = self.gp.cnx
    self.gp.Hide()
    for (b, p) in self.bs_and_ps:
      b.Show()
    self.lp.Show()
    self.lb.SetValue(True)
    self.Layout()
    self.SetFocus()

  ####################################################################
  def OnToggle (self, event):
    b0 = event.GetEventObject()
    if b0 == self.xb and not self.bp.current_account_id:
      md = wx.MessageDialog(parent=self, message="Before creating an export " + \
          "you must set a default account",
          caption='Default account not set',
          style=wx.OK|wx.ICON_EXCLAMATION)
      retcode = md.ShowModal()
      b0.SetValue(False)
    else:
      for (b, p) in self.bs_and_ps:
        if b != b0:
          b.SetValue(False)
          p.Hide()
        else:
          p.Show()
      b0.SetValue(True)
      self.Layout()

  ####################################################################
  def ExecuteExit (self, event):
    self.Close()

######################################################################
