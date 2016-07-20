#!/usr/bin/env python
######################################################################
## $Revision: 1.2 $
## $Date: 2016/02/11 23:38:41 $
## Author: Carl Schaefer, Smithsonian Institution Archives 
######################################################################

import wx
import wx.html as wxhtml
import db_access as dba
import dm_common as dmc
import dm_wx
from dm_wx import FRAME_WIDTH, FRAME_HEIGHT
import message_group

####################################################################
## AccountInfo
####################################################################
class AccountInfo (wx.Panel):
  def __init__ (self, name, browse, results_notebook, cnx, data):
    wx.Panel.__init__ (self, parent=results_notebook, id=-1, name=name)
    self.browse = browse
    self.results_notebook = results_notebook
    self.results = results_notebook.GetParent()
    self.cnx  = cnx
    self.acc = data
    self.normal_font_size = self.GetFont().GetPointSize()
    self.bigger_font_size = self.normal_font_size + 3

    self.sb        = self.make_set_account()
    self.acc_attrs = self.make_acc_attrs()
    self.flist     = self.make_folder_list()

    sizer = wx.BoxSizer(wx.VERTICAL)

    sizer.Add((FRAME_WIDTH, 10))
    sizer.Add(self.sb, 0, wx.ALIGN_CENTER)

    sizer.Add((FRAME_WIDTH, 5))
    sizer.Add(self.acc_attrs, 1, wx.EXPAND|wx.LEFT, 5)

    sizer.Add((FRAME_WIDTH, 5))
    aname = wx.StaticText(self, id=-1, label='Folders')
    aname.SetFont(wx.Font(self.normal_font_size, wx.SWISS, wx.NORMAL, wx.BOLD))
    sizer.Add(aname, 0, wx.ALIGN_CENTER)

    sizer.Add((FRAME_WIDTH, 5))
    sizer.Add(self.flist, 1, wx.EXPAND|wx.LEFT, 5)
    self.SetSizer(sizer)

    self.results.page_id = self.results.page_id + 1
    results_notebook.AddPage(self, str(self.results.page_id), select=True)
    self.browse.switch_to_results()

  ####################################################################
  def make_set_account (self):
    sb = wx.Button(self, id=-1, name='set_account', label='Set Account')
    self.Bind(wx.EVT_BUTTON, self.OnSetAccount, sb)
    return sb

  ####################################################################
  def make_acc_attrs (self):
    attributes = [
      ('Account&nbsp;name', self.acc.account_name),
      ('Id', str(self.acc.account_id)),
      ('Account&nbsp;directory', self.acc.account_directory),
      ('Message&nbsp;count', "{:,}".format(self.acc.message_count)),
      ('First&nbsp;message&nbsp;date', str(self.acc.start_date)),
      ('Last&nbsp;message&nbsp;date', str(self.acc.end_date)),
      ("'From'&nbsp;addresses", "{:,}".format(self.acc.from_count)),
      ("'To'&nbsp;addresses", "{:,}".format(self.acc.to_count)),
      ("'Cc'&nbsp;addresses", "{:,}".format(self.acc.cc_count)),
      ("'Bcc'&nbsp;addresses", "{:,}".format(self.acc.bcc_count)),
      ('External&nbsp;content&nbsp;files', "{:,}".format(self.acc.external_files))
    ]
    s = '<table border="0" cellpadding="1" cellspacing="1">'
    for (name, value) in attributes:
      s = s + '<tr><td><b>' + name + '</b></td><td>' + value + '</td></tr>'
    s = s + '</table>'
    h = wxhtml.HtmlWindow(self, id=-1, name='',
        size=(FRAME_WIDTH-50, 240))
    h.SetPage(s)
    return h

  ####################################################################
  def make_folder_list (self):
    flc = wx.ListView(self,
        size=(FRAME_WIDTH-50, 240),
        style=wx.LC_REPORT|wx.LC_SINGLE_SEL)
    flc.InsertColumn(0, 'Id',  width=60)
    flc.InsertColumn(1, 'Name', width=100)
    flc.InsertColumn(2, 'Messages', width=60)
    flc.InsertColumn(3, 'Start Date', width=90)
    flc.InsertColumn(4, 'End Date', width=90)
    flc.InsertColumn(5, 'Relative Path', width=200)
    for fld in self.acc.folders:
      flc.Append((fld.folder_id, fld.folder_name, "{:,}".format(fld.message_count),
          fld.start_date, fld.end_date, fld.relative_path))
    self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnFolderClick, flc)
    return flc

  ####################################################################
  def OnFolderClick(self, event):
    i = event.m_itemIndex
    self.flist.Select(i, False)

  ####################################################################
  def OnSetAccount(self, event):
    old_account_id = self.browse.current_account_id
    new_account_id = self.acc.account_id
    self.browse.current_account_id   = new_account_id
    self.browse.current_account_name = self.acc.account_name
    md = wx.MessageDialog(parent=self, message="Current account is set to '" + \
        self.acc.account_name + "'", caption='Current Account',
        style=wx.OK|wx.ICON_EXCLAMATION)
    retcode = md.ShowModal()
    if old_account_id and old_account_id != new_account_id:
      # parent is ResultsPanel.nb
      # parent of parent is ResultsPanel
      self.GetParent().GetParent().delete_obsolete_pages(new_account_id)
