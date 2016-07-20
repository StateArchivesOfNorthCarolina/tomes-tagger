#!/usr/bin/env python
######################################################################
## $Revision: 1.2 $
## $Date: 2015/11/13 16:12:18 $
## Author: Carl Schaefer, Smithsonian Institution Archives 
######################################################################

import re
import wx
import  wx.lib.scrolledpanel as scrolled
import db_access as dba
import dm_common as dmc
import dm_wx
from dm_wx import FRAME_WIDTH, FRAME_HEIGHT
import address_list

####################################################################
## AddressSearch
####################################################################
class AddressSearch (scrolled.ScrolledPanel):

  variable_names = [
    'address',
  ]
  name2default   = {
    'address'         : ''
  }
  name2component = {}
  cnx              = None
  browse           = None
  browse_notebook  = None
  results          = None
  results_notebook = None
  address          = None
 
  ####################################################################
  def __init__ (self, parent, name):

    wx.ScrolledWindow.__init__ (self, parent=parent, id=-1, name=name)

    normal_font_size = self.GetFont().GetPointSize()  # get the current size
    bigger_font_size = normal_font_size + 3

    box = wx.StaticBoxSizer(wx.StaticBox(self, -1, "" ), wx.VERTICAL)
    grid = wx.FlexGridSizer(cols=2)
    grid.Add(wx.StaticText(self, id=-1, label='Search String'),
        0, wx.ALIGN_RIGHT|wx.TOP, 5)
    txc = wx.TextCtrl(self, id=-1, name='address', size=(200, -1))
    grid.Add(txc, 0, wx.ALIGN_LEFT|wx.LEFT|wx.TOP|wx.BOTTOM, 5)
    box.Add(grid, 0, wx.ALIGN_LEFT|wx.LEFT, 5)
#    t2 = wx.StaticText(self, id=-1, label='automatically wild-carded left and right')
#    t2.SetFont(wx.Font(normal_font_size, wx.SWISS, wx.ITALIC, wx.NORMAL))
#    box.Add(t2, 0, wx.ALIGN_CENTER)

    sz = wx.BoxSizer(orient=wx.VERTICAL)
    sz.Add((FRAME_WIDTH, 15))
    sz.Add(box, 0, wx.ALIGN_CENTER)
    sz.Add((FRAME_WIDTH, 15))
    sz.Add(dm_wx.ActionButtons(self, 'Search for Address/Name'), 0, wx.ALIGN_CENTER, 5)

    self.SetSizer(sz)
    self.SetupScrolling()

    for v in self.variable_names:
      self.name2component[v] = self.FindWindowByName(v)
    self.ResetVariables()
    for b in dm_wx.button_names:
      self.name2component[b] = self.FindWindowByName(b)

    self.name2component['reset_button'].Bind(wx.EVT_LEFT_UP, self.ExecuteReset)
    self.name2component['go_button'].Bind(wx.EVT_LEFT_UP, self.ValidateVariablesAndGo)

  ####################################################################
  def ResetVariables (self):
    for v in self.variable_names:
      self.name2component[v].SetValue(self.name2default[v])

  ####################################################################
  def ExecuteReset (self, event):
    self.ResetVariables()
    self.GetParent().SetFocus()

  ####################################################################
  def ValidateVariablesAndGo(self, event):
    ready = True
    if not self.browse.current_account_id:
      md = wx.MessageDialog(parent=self, message="Before searching for " + \
          "addresses or messages, you must set a default account",
          caption='Default account not set',
          style=wx.OK|wx.ICON_EXCLAMATION)
      retcode = md.ShowModal()
      ready = False
      self.browse.switch_to_account_search()
      return
    self.address = self.name2component['address'].GetValue().strip()
    if ready:
      self.search_address()

  ######################################################################
  def search_address (self):
    address_info = dba.search_address_name(self.cnx,
        self.browse.current_account_id, self.address)
    if len(address_info) == 0:
      md = wx.MessageDialog(parent=self,
          message="No address/name matching search string",
          caption='No data',
          style=wx.OK|wx.ICON_EXCLAMATION)
      retcode = md.ShowModal()
    else:
      self.results.page_id = self.results.page_id + 1
      page_name = str(self.results.page_id)
      address_list.AddressList(self.browse, self.results_notebook,
          page_name, self.cnx, address_info)
      self.browse.switch_to_results()


