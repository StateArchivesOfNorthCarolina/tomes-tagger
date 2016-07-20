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
import  wx.lib.scrolledpanel as scrolled
import wx.lib.agw.flatnotebook as fnb
import db_access as dba
import dm_common as dmc

####################################################################
## ResultsPanel
####################################################################
class ResultsPanel (scrolled.ScrolledPanel):
  account          = None
  account_id       = None
  cnx              = None
  browse           = None
  browse_notebook  = None
  results          = None
  results_notebook = None

  ####################################################################
  def __init__ (self, parent, name):
    wx.ScrolledWindow.__init__ (self, parent=parent, id=-1, name=name)

    normal_font_size = self.GetFont().GetPointSize()  # get the current size
    bigger_font_size = normal_font_size + 3

    self.page_id = 0

    self.nb = fnb.FlatNotebook(self, -1)
# styles appear not to work
#      style=fnb.FNB_X_ON_TAB|fnb.FNB_NAV_BUTTONS_WHEN_NEEDED)

    sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
    sizer.Add(self.nb, 1, wx.EXPAND)
    self.SetSizer(sizer)
    self.SetupScrolling()

  ######################################################################
  def delete_obsolete_pages (self, new_current_account_id):
    # kill all except the the current page
    kills = []
    cp = self.nb.GetCurrentPage()
    for i in range(self.nb.GetPageCount()):
      p = self.nb.GetPage(i)
      if p != cp:
        kills.append(p)
    for k in kills:
      self.nb.DeletePage(self.nb.GetPageIndex(k))
    self.nb.Refresh()

