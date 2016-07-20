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
import db_access as dba
import dm_common as dmc
import dm_wx
from dm_wx import FRAME_WIDTH, FRAME_HEIGHT
import dm_defaults as dmd
import wx.lib.newevent

####################################################################
## LogonPanel
####################################################################
class LogonPanel (scrolled.ScrolledPanel):

  variable_names = [
    'host',
    'username',
    'password',
    'database'
  ]

  name2default   = {
    'host'            : dmd.DEFAULT_HOST,
    'username'        : dmd.DEFAULT_USER,
    'password'        : dmd.DEFAULT_PASSWORD,
    'database'        : dmd.DEFAULT_DATABASE
  }

  name2component = {}

  cnx             = None
  username        = None
  password        = None
  host            = None
  database        = None
  
  ####################################################################
  def __init__ (self, parent, name):

    wx.ScrolledWindow.__init__ (self, parent=parent, id=-1, name=name)

    normal_font_size = self.GetFont().GetPointSize()  # get the current size
    bigger_font_size = normal_font_size + 3

    sz = wx.BoxSizer(orient=wx.VERTICAL)
    sz.Add((FRAME_WIDTH, 10))

    t1 = wx.StaticText(self, id=-1, label=
        'Login to DArcMail Database')
    t1.SetFont(wx.Font(bigger_font_size, wx.SWISS, wx.NORMAL, wx.BOLD))
    sz.Add(t1, 0, wx.ALIGN_CENTER, 5)

    sz.Add((FRAME_WIDTH, 15))

    sz.Add(dm_wx.DatabaseNames(self), 0, wx.ALIGN_LEFT, 5)
    sz.Add((FRAME_WIDTH, 10))

    sz.Add(dm_wx.ActionButtons(self, 'Login'), 0, wx.ALIGN_CENTER, 5)
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
#    self.name2component['exit_button'].Bind(wx.EVT_LEFT_UP, self.ExecuteExit)
    self.name2component['go_button'].Bind(wx.EVT_LEFT_UP, self.ValidateVariablesAndGo)

    self.LoginEvent, self.EVT_LOGIN = wx.lib.newevent.NewEvent()

  ####################################################################
  def ResetVariables (self):
    for v in self.variable_names:
      self.name2component[v].SetValue(self.name2default[v])

  ####################################################################
  def ExecuteReset (self, event):
    self.ResetVariables()
    self.GetParent().SetFocus()

  ####################################################################
  def ExecuteExit (self, event):
    # self is a
    #    LogonPanel within a
    #        wx.Frame

    self.GetParent().Close()

  ####################################################################
  def ValidateVariablesAndGo(self, event):
    ready = True
    msg = dm_wx.ValidateDatabaseVariables(self,
      self.name2component['username'].GetValue(),
      self.name2component['password'].GetValue(),
      self.name2component['host'].GetValue(),
      self.name2component['database'].GetValue())
    if msg != '':
      md = wx.MessageDialog(parent=self, message=msg, caption='Error',
          style=wx.OK|wx.ICON_EXCLAMATION)
      retcode = md.ShowModal()
      ready = False
    if ready:
      evt = self.LoginEvent(evt_type='logged in')
      frame = self.GetParent()
      wx.PostEvent(frame, evt)
