 #!/usr/bin/env python
######################################################################
## $Revision: 1.2 $
## $Date: 2016/02/11 23:38:42 $
## Author: Carl Schaefer, Smithsonian Institution Archives 
######################################################################

import wx
#import  wx.lib.scrolledpanel as scrolled
import db_access as dba
import dm_common as dmc
import account_search
import message_search
import address_search
import results_panel

####################################################################
## BrowsePanel
####################################################################
class BrowsePanel (wx.Panel):
  cnx                  = None
  current_account_id   = None 
  current_account_name = None 

  ####################################################################
  def __init__ (self, parent, name):

    wx.Panel.__init__ (self, parent=parent, id=-1, name=name)

    normal_font_size = self.GetFont().GetPointSize()  # get the current size
    bigger_font_size = normal_font_size + 3

    self.nb = wx.Notebook(self, -1)
    self.csp = account_search.AccountSearch(self.nb, 'account_search')
    self.msp = message_search.MessageSearch(self.nb, 'message_search')
    self.asp = address_search.AddressSearch(self.nb, 'address_search')
    self.rsp = results_panel.ResultsPanel(self.nb, 'results_panel')
    self.nb.AddPage(self.csp, 'Account')       # 0
    self.nb.AddPage(self.msp, 'Message')       # 1
    self.nb.AddPage(self.asp, 'Address/Name')  # 2
    self.nb.AddPage(self.rsp, 'Results')       # 3
    for p in [self.csp, self.msp, self.asp, self.rsp]:
      p.cnx              = self.cnx
      p.browse           = self
      p.browse_notebook  = self.nb
      p.results          = self.rsp
      p.results_notebook = self.rsp.nb
    sizer = wx.BoxSizer(orient=wx.VERTICAL)
    sizer.Add(self.nb, 1, wx.EXPAND)
    self.SetSizer(sizer)

  ####################################################################
  def switch_to_results (self):
    self.nb.SetSelection(3)
    self.rsp.SetFocus()

  ####################################################################
  def switch_to_account_search (self):
    self.nb.SetSelection(0)

