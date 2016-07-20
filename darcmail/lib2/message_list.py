#!/usr/bin/env python
######################################################################
## $Revision: 1.2 $
## $Date: 2016/02/11 23:38:42 $
## Author: Carl Schaefer, Smithsonian Institution Archives 
######################################################################

import wx
import wx.lib.scrolledpanel as scrolled
import wx.lib.platebtn as platebtn
import re
import db_access as dba
import dm_common as dmc
import dm_wx
import paging
import message_info
import message_group

selection_choices = ['-', 'All', 'None']

####################################################################
## MessageList
####################################################################
#class MessageList(scrolled.ScrolledPanel):
class MessageList(wx.Panel):
  def __init__ (self, browse, results_notebook, name, cnx, data, search_params):
    wx.Window.__init__ (self, parent=results_notebook, id=-1, name=name)

    self.browse = browse
    self.results_notebook = results_notebook
    self.results = results_notebook.GetParent()
    self.cnx  = cnx
    self.data = data
    self.search_params = search_params
    self.search_term = search_params.body
    self.mg = message_group.message_group_for_account(self.browse.current_account_id)
    row_count = len(self.data)
    self.pi = paging.PagingInfo(row_count)

    self.top_pane = wx.Panel(self, id=-1, name='top_pane')
    self.select_combo = wx.ComboBox(self.top_pane, id=-1, name='select_combo',
        style=wx.CB_DROPDOWN, choices=selection_choices)
    self.select_combo.Bind(wx.EVT_COMBOBOX, self.OnSelect)
    self.top_sizer  = wx.BoxSizer(orient=wx.HORIZONTAL)
    self.top_sizer.Add(self.select_combo, 0, wx.ALIGN_LEFT|wx.ALL, 5)
    if row_count > dm_wx.MAX_LIST_SIZE:
      self.page_sizer = self.pi.page_links(self.pi.current_page, self.top_pane,
          self.OnPageButton)
      self.top_sizer.Add(self.page_sizer, 0, wx.ALIGN_LEFT|wx.ALL, 5)
    self.top_pane.SetSizer(self.top_sizer)

    self.bot_pane = scrolled.ScrolledPanel(self, id=-1, name='bot_pane')
    self.gs = self.make_list(self.bot_pane)
    self.bot_pane.SetupScrolling()
    self.bot_pane.SetSizer(self.gs)

    self.sizer = sizer = wx.BoxSizer(wx.VERTICAL)
    params_text = wx.StaticText(self, id=-1,
        label="Search Parameters: " + self.search_params.params_text())
    params_text.Wrap(dm_wx.FRAME_WIDTH-50)
    self.sizer.Add(params_text, 0, wx.ALIGN_LEFT|wx.ALL, 5)
    self.sizer.Add(self.top_pane, 0, wx.ALIGN_LEFT)
    self.sizer.Add(self.bot_pane, 1, wx.EXPAND|wx.ALIGN_LEFT)
    self.SetSizer(self.sizer)

    results_notebook.AddPage(self, str(self.results.page_id), select=True)
    self.browse.switch_to_results()

  ####################################################################
  def OnSelect (self, event):
    idx = self.FindWindowByName('select_combo').GetSelection()
    if selection_choices[idx] == 'All':
      for i in range(self.pi.current_lo_i, self.pi.current_hi_i):
        (mid, date, subj) = self.data[i]
        self.mg.add(mid)
    elif selection_choices[idx] == 'None':
      for i in range(self.pi.current_lo_i, self.pi.current_hi_i):
        (mid, date, subj) = self.data[i]
        if mid in self.mg:
          self.mg.remove(mid)
    self.RebuildList()

  ####################################################################
  def RebuildList (self):
    self.gs.DeleteWindows()
    self.gs = self.make_list(self.bot_pane)
    self.bot_pane.SetSizer(self.gs)
    self.sizer.Layout()

  ####################################################################
  def OnPageButton(self, event):
    eo = event.GetEventObject()
    label = eo.GetLabel()
    self.sizer.Hide(self.gs)
    self.sizer.Hide(self.page_sizer)
    self.page_sizer.DeleteWindows()
    self.top_sizer.Remove(self.page_sizer)
    current_page = self.pi.current_page
    if label == '<<':
      self.page_sizer = self.pi.page_links_left(self.top_pane, self.OnPageButton)
    elif label == '>>':
      self.page_sizer = self.pi.page_links_right(self.top_pane, self.OnPageButton)
    else:
      current_page = int(label)
      self.page_sizer = self.pi.page_links(current_page, self.top_pane, self.OnPageButton)
    self.top_sizer.Add(self.page_sizer, 0, wx.ALIGN_LEFT|wx.ALL, 5)
    self.top_pane.SetSizer(self.top_sizer)
    self.RebuildList()

  ####################################################################
  def make_list (self, parent):
    gs = wx.FlexGridSizer(cols=4)
    col1 = wx.StaticText(parent, id=-1, label='')   ## don't need header; just takes space
    col2 = wx.StaticText(parent, id=-1, label='Id')
    col3 = wx.StaticText(parent, id=-1, label='Date')
    col4 = wx.StaticText(parent, id=-1, label='Subject')
    gs.Add(col1, 0, wx.ALIGN_CENTER)
    gs.Add(col2, 0, wx.ALIGN_CENTER|wx.LEFT, 5)
    gs.Add(col3, 0, wx.ALIGN_CENTER|wx.LEFT, 5)
    gs.Add(col4, 1, wx.ALIGN_CENTER|wx.LEFT, 5)
    selected_count   = 0
    unselected_count = 0
    for i in range(self.pi.current_lo_i, self.pi.current_hi_i):
      (mid, date, subj) = self.data[i]
      col1 = wx.CheckBox(parent, id=-1, name='cb_' + str(mid), label='')
      if mid in self.mg:
        col1.SetValue(True)
        selected_count += 1
      else:
        col1.SetValue(False)
        unselected_count += 1
      if selected_count and unselected_count:
        self.FindWindowByName('select_combo').SetSelection(selection_choices.index('-'))
      elif selected_count:
        self.FindWindowByName('select_combo').SetSelection(selection_choices.index('All'))
      elif unselected_count:
        self.FindWindowByName('select_combo').SetSelection(selection_choices.index('None'))
      col1.Bind(wx.EVT_CHECKBOX, self.OnCheckBox)
      col2 = wx.lib.platebtn.PlateButton(parent, id=-1, name='mid_' + str(mid),
          label=str(mid), style=platebtn.PB_STYLE_SQUARE)
      col2.Bind(wx.EVT_BUTTON, self.OnMessageIdClick)
      col3 = wx.StaticText(parent, id=-1, name='', label=str(date))
      col4 = wx.StaticText(parent, id=-1, name='', label=subj)
      gs.Add(col1, 0, wx.ALIGN_LEFT)
      gs.Add(col2, 0, wx.ALIGN_LEFT|wx.LEFT, 5)
      gs.Add(col3, 0, wx.ALIGN_LEFT|wx.LEFT, 5)
      gs.Add(col4, 1, wx.ALIGN_LEFT|wx.LEFT, 5)
    return gs

  ####################################################################
  def OnCheckBox (self, event):
    eo = event.GetEventObject()
    name = eo.GetName()
    m = re.match('cb_(\d+)', eo.GetName())
    if m:
      mid = int(m.group(1))
    if eo.GetValue():
      self.mg.add(mid)
    else:
      if mid in self.mg:
        self.mg.remove(mid)
    self.RebuildList()

  ####################################################################
  def OnMessageIdClick (self, event):
    eo = event.GetEventObject()
    label = eo.GetLabel()
    mid   = int(label)
    message_info.MessageInfo('', self.browse, self.results_notebook,
        self.cnx, dba.DbMessage(self.cnx, mid), self.search_term)
