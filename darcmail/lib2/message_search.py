#!/usr/bin/env python
######################################################################
## $Revision: 1.3 $
## $Date: 2016/02/11 23:38:42 $
## Author: Carl Schaefer, Smithsonian Institution Archives 
######################################################################

import re
import wx
import  wx.lib.scrolledpanel as scrolled
import db_access as dba
import dm_common as dmc
import dm_wx
from dm_wx import FRAME_WIDTH, FRAME_HEIGHT
import message_list

####################################################################
## MessageParams
####################################################################
class SearchParams ():

  ##################################################################
  def __init__ (self,
      global_id='',
      date_from='',
      date_to='',
      folder='',
      from_line='',
      to_line='',
      cc_line='',
      bcc_line='',
      replies='',
      subject='',
      attachment='',
      body='',
      body_search_type='',
      selected_status='',
      sort_order=''):

    self.global_id  = global_id
    self.date_from  = date_from
    self.date_to    = date_to
    self.from_line  = from_line
    self.to_line    = to_line
    self.cc_line    = cc_line
    self.bcc_line   = bcc_line
    self.replies    = replies
    self.subject    = subject
    self.folder     = folder
    self.body       = body
    self.attachment = attachment
    self.body       = body
    self.body_search_type = body_search_type
    self.selected_status  = selected_status
    self.sort_order = sort_order

    self.params = [
      ('Selected', selected_status),
      ('Global ID', global_id),
      ('Date From', date_from),
      ('Date To', date_to),
      ('From', from_line),
      ('To', to_line),
      ('Cc', cc_line),
      ('Bcc', bcc_line),
      ('Replies', replies),
      ('Subject', subject),
      ('Folder', folder),
      ('Attachment Name', attachment),
      ('Body Search', body),
      ('Plain/HTML', body_search_type),
      ('Sort Order', sort_order) ]

  ##################################################################
  def params_text (self):
    plist = []
    for (label, value) in self.params:
      if value:
        if not self.body and label == 'Plain/HTML':
          continue
        plist.append(label + '="' + value + '"')
    return ', '.join(plist)
      
####################################################################
## MessageSearch
####################################################################
class MessageSearch (scrolled.ScrolledPanel):

  variable_names = [
    'global_id',
    'date_from',
    'date_to',
    'folder',
    'subject',
    'from_line',
    'to_line',
    'cc_line',
    'attachment',
    'body',
    'plain_cb',
    'html_cb',
    'any_rb',
    'sel_rb',
    'unsel_rb',
    'oldest_rb',
    'newest_rb'
  ]
  name2default   = {
    'global_id'  : '',
    'date_from'  : '',
    'date_to'    : '',
    'folder'     : '',
    'subject'    : '',
    'from_line'  : '',
    'to_line'    : '',
    'cc_line'    : '',
    'body'       : '',
    'attachment' : '',
    'plain_cb'   : True,
    'html_cb'    : False,
    'any_rb'     : True,
    'sel_rb'     : False,
    'unsel_rb'   : False,
    'oldest_rb'  : True,
    'newest_rb'  : False
  }
  name2component = {}
  account          = None
  account_id       = None
  cnx              = None
  browse           = None
  browse_notebook  = None
  results          = None
  results_notebook = None

  global_id        = None
  date_from        = None
  date_to          = None
  folder           = None
  subject          = None
  from_line        = None             
  to_line          = None             
  cc_line          = None             
  attachment       = None
  body             = None
  plain_cb         = None
  html_cb          = None
  any_rb           = None  
  sel_rb           = None
  unsel_rb         = None
  oldest_rb        = None
  newest_rb        = None
  selected_status  = None  # values: 'any', 'selected', 'unselected'

  ####################################################################
  def __init__ (self, parent, name):

    wx.ScrolledWindow.__init__ (self, parent=parent, id=-1, name=name)

    normal_font_size = self.GetFont().GetPointSize()  # get the current size
    bigger_font_size = normal_font_size + 3

    grid = wx.FlexGridSizer(cols=2)

    aname = wx.StaticText(self, id=-1, label='Sort Order')
    rb_sizer = wx.BoxSizer(wx.HORIZONTAL)
    oldest_rb = wx.RadioButton(self, id=-1, label=' Oldest first', name='oldest_rb', style=wx.RB_GROUP)
    newest_rb = wx.RadioButton(self, id=-1, label=' Newest first ', name='newest_rb')
    rb_sizer.Add(oldest_rb, 0, wx.RIGHT|wx.LEFT, 10)
    rb_sizer.Add(newest_rb, 0, wx.RIGHT|wx.LEFT, 10)
    grid.Add(aname, 0, wx.ALIGN_LEFT|wx.TOP|wx.RIGHT, 5)
    grid.Add(rb_sizer, 0, wx.ALIGN_LEFT|wx.TOP|wx.RIGHT, 5)

    aname = wx.StaticText(self, id=-1, label='Message status')
    rb_sizer = wx.BoxSizer(wx.HORIZONTAL)
    any_rb = wx.RadioButton(self, id=-1, label=' Any ', name='any_rb', style=wx.RB_GROUP)
    sel_rb = wx.RadioButton(self, id=-1, label=' Selected ', name='sel_rb')
    unsel_rb = wx.RadioButton(self, id=-1, label=' Unselected ', name='unsel_rb')
    rb_sizer.Add(any_rb, 0, wx.RIGHT|wx.LEFT, 10)
    rb_sizer.Add(sel_rb, 0, wx.RIGHT|wx.LEFT, 10)
    rb_sizer.Add(unsel_rb, 0, wx.RIGHT|wx.LEFT, 10)
    grid.Add(aname, 0, wx.ALIGN_LEFT|wx.TOP|wx.RIGHT, 5)
    grid.Add(rb_sizer, 0, wx.ALIGN_LEFT|wx.TOP|wx.RIGHT, 5)

    aname = wx.StaticText(self, id=-1, label='Global Id')
    aval  = wx.TextCtrl(self, id=-1, name='global_id', size=(400, -1))
    grid.Add(aname, 0, wx.ALIGN_LEFT|wx.TOP|wx.RIGHT, 5)
    grid.Add(aval,  0, wx.ALIGN_LEFT|wx.TOP|wx.RIGHT, 5)

    aname = wx.StaticText(self, id=-1, label='Date From')
    aval  = wx.TextCtrl(self, id=-1, name='date_from', size=(200, -1))
    grid.Add(aname, 0, wx.ALIGN_LEFT|wx.TOP|wx.RIGHT, 5)
    grid.Add(aval,  0, wx.ALIGN_LEFT|wx.TOP|wx.RIGHT, 5)

    aname = wx.StaticText(self, id=-1, label='Date To')
    aval  = wx.TextCtrl(self, id=-1, name='date_to', size=(200, -1))
    grid.Add(aname, 0, wx.ALIGN_LEFT|wx.TOP|wx.RIGHT, 5)
    grid.Add(aval,  0, wx.ALIGN_LEFT|wx.TOP|wx.RIGHT, 5)

    aname = wx.StaticText(self, id=-1, label='Folder')
    aval  = wx.TextCtrl(self, id=-1, name='folder', size=(200, -1))
    grid.Add(aname, 0, wx.ALIGN_LEFT|wx.TOP|wx.RIGHT, 5)
    grid.Add(aval,  0, wx.ALIGN_LEFT|wx.TOP|wx.RIGHT, 5)

    aname = wx.StaticText(self, id=-1, label='Subject Line')
    aval  = wx.TextCtrl(self, id=-1, name='subject', size=(400, -1))
    grid.Add(aname, 0, wx.ALIGN_LEFT|wx.TOP|wx.RIGHT, 5)
    grid.Add(aval,  0, wx.ALIGN_LEFT|wx.TOP|wx.RIGHT, 5)

    aname = wx.StaticText(self, id=-1, label='From Line')
    aval  = wx.TextCtrl(self, id=-1, name='from_line', size=(200, -1))
    grid.Add(aname, 0, wx.ALIGN_LEFT|wx.TOP|wx.RIGHT, 5)
    grid.Add(aval,  0, wx.ALIGN_LEFT|wx.TOP|wx.RIGHT, 5)

    aname = wx.StaticText(self, id=-1, label='To Line')
    aval  = wx.TextCtrl(self, id=-1, name='to_line', size=(200, -1))
    grid.Add(aname, 0, wx.ALIGN_LEFT|wx.TOP|wx.RIGHT, 5)
    grid.Add(aval,  0, wx.ALIGN_LEFT|wx.TOP|wx.RIGHT, 5)

    aname = wx.StaticText(self, id=-1, label='Cc Line')
    aval  = wx.TextCtrl(self, id=-1, name='cc_line', size=(200, -1))
    grid.Add(aname, 0, wx.ALIGN_LEFT|wx.TOP|wx.RIGHT, 5)
    grid.Add(aval,  0, wx.ALIGN_LEFT|wx.TOP|wx.RIGHT, 5)

    aname = wx.StaticText(self, id=-1, label='Attachment Name')
    aval  = wx.TextCtrl(self, id=-1, name='attachment', size=(200, -1))
    grid.Add(aname, 0, wx.ALIGN_LEFT|wx.TOP|wx.RIGHT, 5)
    grid.Add(aval,  0, wx.ALIGN_LEFT|wx.TOP|wx.RIGHT, 5)

    aname = wx.StaticText(self, id=-1, label='Body Text')
    aval  = wx.TextCtrl(self, id=-1, name='body', size=(400, -1))
    grid.Add(aname, 0, wx.ALIGN_LEFT|wx.TOP|wx.RIGHT, 5)
    grid.Add(aval,  0, wx.ALIGN_LEFT|wx.TOP|wx.RIGHT, 5)

    cb_sizer = wx.BoxSizer(wx.HORIZONTAL)
    plain_cb = wx.CheckBox(self, id=-1, name='plain_cb', label='text/plain')
    html_cb  = wx.CheckBox(self, id=-1, name='html_cb', label='text/html')
    cb_sizer.Add(wx.StaticText(self, id=-1, label='Search body text:'))
    cb_sizer.Add(plain_cb, 0, wx.RIGHT|wx.LEFT, 10)
    cb_sizer.Add(html_cb,  0, wx.LEFT, 10)
    grid.Add((5,5))
    grid.Add(cb_sizer, 0, wx.ALIGN_LEFT|wx.TOP|wx.RIGHT, 5)

    box = wx.StaticBoxSizer(wx.StaticBox(self, -1, "" ), wx.VERTICAL)
    box.Add(grid, 1, wx.EXPAND)

    hz = wx.BoxSizer(wx.HORIZONTAL)
    hz.Add(dm_wx.ActionButtons(self, 'Search for Messages'), 0)

    sizer = wx.BoxSizer(orient=wx.VERTICAL)
    sizer.Add((FRAME_WIDTH, 10))
#    sizer.Add(t1, 0, wx.ALIGN_CENTER)
#    sizer.Add((FRAME_WIDTH, 10))
    sizer.Add(box, 0, wx.ALIGN_CENTER)
    sizer.Add((FRAME_WIDTH, 10))
    sizer.Add(hz, 0, wx.ALIGN_CENTER)
    self.SetSizer(sizer)
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
  def validate_date (self, date):
    m = re.match('^\d{4}(-\d{2}(-\d{2})?)?$', date)
    if m:
      return True
    else:
      return False

  ####################################################################
  def validate_date_to (self, date):
    if not date:
      return ''
    elif self.validate_date(date):
      if len(date) == 10:
        return date
      elif len(date) == 7:
        return date + '-31'
      elif len(date) == 4:
        return date + '-12-31'
    else:
      return None

  ####################################################################
  def validate_date_from (self, date):
    if not date:
      return ''
    elif self.validate_date(date):
      if len(date) == 10:
        return date
      elif len(date) == 7:
        return date + '-01'
      elif len(date) == 4:
        return date + '-01-01'
    else:
      return None

  ####################################################################
  def ValidateVariablesAndGo (self, event):
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
    self.body_search_type = 'both'
    self.global_id  = self.name2component['global_id'].GetValue().strip()
    self.date_from  = self.name2component['date_from'].GetValue().strip()
    self.date_to    = self.name2component['date_to'].GetValue().strip()
    self.folder     = self.name2component['folder'].GetValue().strip()
    self.from_line  = self.name2component['from_line'].GetValue().strip()
    self.to_line    = self.name2component['to_line'].GetValue().strip()
    self.cc_line    = self.name2component['cc_line'].GetValue().strip()
    self.subject    = self.name2component['subject'].GetValue().strip()
    self.body       = self.name2component['body'].GetValue().strip()
    self.attachment = self.name2component['attachment'].GetValue().strip()
    self.any_rb     = self.name2component['any_rb'].GetValue()
    self.sel_rb     = self.name2component['sel_rb'].GetValue()
    self.unsel_rb   = self.name2component['unsel_rb'].GetValue()
    self.oldest     = self.name2component['oldest_rb'].GetValue()
    self.newest     = self.name2component['newest_rb'].GetValue()

    self.selected_status = 'any'
    if self.sel_rb:
      self.selected_status = 'selected'
    elif self.unsel_rb:
      self.selected_status = 'unselected'

    self.plain_cb   = self.name2component['plain_cb'].GetValue()
    self.html_cb    = self.name2component['html_cb'].GetValue()
    if self.plain_cb and self.html_cb:
      self.body_search_type = 'both'
    elif self.plain_cb:
      self.body_search_type = 'plain'
    elif self.html_cb:
      self.body_search_type = 'html'
    else:
      if self.body:
        md = wx.MessageDialog(parent=self,
            message="If you specify a body search string, they you must check at " + \
            "at least one of the search types: text/plain or text/html",
            caption='Error',
            style=wx.OK|wx.ICON_EXCLAMATION)
        retcode = md.ShowModal()
        ready = False
      
    self.date_from = self.validate_date_from(self.date_from)
    if self.date_from == None:
      md = wx.MessageDialog(parent=self,
          message="Date must be like '2014' or '2014-03' or '2014-03-15'",
          caption='Error',
          style=wx.OK|wx.ICON_EXCLAMATION)
      retcode = md.ShowModal()
      ready = False
    self.date_to = self.validate_date_to(self.date_to)
    if self.date_to == None:
      md = wx.MessageDialog(parent=self,
          message="Date must be like '2014' or '2014-03' or '2014-03-15'",
          caption='Error',
          style=wx.OK|wx.ICON_EXCLAMATION)
      retcode = md.ShowModal()
      ready = False
    if ready:
      self.sort_order = 'newest' if self.newest else 'oldest'
      self.bcc_line   = ''   # only from address_info page
      self.replies_to = ''   # only from Get Replies on message_info page
      self.search_params = SearchParams(
        self.global_id,
        self.date_from,
        self.date_to,
        self.folder,
        self.from_line,
        self.to_line,
        self.cc_line,
        self.bcc_line,
        self.replies_to,
        self.subject,
        self.attachment,
        self.body,
        self.body_search_type,
        self.selected_status,
        self.sort_order
      )
      self.search_message()

  ######################################################################
  def search_message (self):
    message_info = dba.search_message(self.cnx,
        self.browse.current_account_id, self.search_params)
    if len(message_info) == 0:
      md = wx.MessageDialog(parent=self,
          message="No messages matching search criteria",
          caption='No data',
          style=wx.OK|wx.ICON_EXCLAMATION)
      retcode = md.ShowModal()
    else:
      self.results.page_id = self.results.page_id + 1
      page_name = str(self.results.page_id)
      message_list.MessageList(self.browse, self.results_notebook,
          page_name, self.cnx, message_info, self.search_params)
      self.browse.switch_to_results()
