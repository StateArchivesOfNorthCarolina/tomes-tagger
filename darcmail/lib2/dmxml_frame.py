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
from wx import DirPickerCtrl
import  wx.lib.scrolledpanel as scrolled
import dm_common as dmc
import dm_wx
from dm_wx import FRAME_WIDTH, FRAME_HEIGHT, FRAME_XPOS, FRAME_YPOS
import dmxml_panel

######################################################################
class DMXmlFrame(wx.Frame):

  ####################################################################
  def __init__(self, parent, title):
    wx.Frame.__init__(self, parent, -1, title,
        pos=(FRAME_XPOS, FRAME_YPOS), size=(FRAME_WIDTH, FRAME_HEIGHT))

    self.qb = wx.ToggleButton(self, id=-1, label='Quit', name='quit_button')
    self.qb.Bind(wx.EVT_LEFT_UP, self.ExecuteExit)

    self.xlp = dmxml_panel.DMXmlPanel(self, 'export_panel')

    self.buttons = wx.BoxSizer(wx.HORIZONTAL)
    
    self.buttons.Add(self.qb, 0, wx.ALL, 3)

    self.top_sizer = wx.BoxSizer(orient=wx.VERTICAL)
    self.top_sizer.Add(self.buttons, 0, wx.LEFT|wx.TOP, 3)
    self.top_sizer.Add(self.xlp, 1, wx.EXPAND)
    self.xlp.Show()
    self.SetSizer(self.top_sizer)
    self.Layout()

  ####################################################################
  def ExecuteExit (self, event):
    self.Close()
