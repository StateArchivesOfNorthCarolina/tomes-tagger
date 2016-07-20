#!/usr/bin/env python
######################################################################
## $Revision: 1.2 $
## $Date: 2016/02/11 23:38:42 $
## Author: Carl Schaefer, Smithsonian Institution Archives 
######################################################################

import os
import re
import base64
import quopri
import wx
import wx.html as wxhtml

import wx.richtext as rt

import db_access as dba
import dm_common as dmc
import dm_defaults as dmd
import xml_common

hl_style = rt.RichTextAttr()
hl_style.SetBackgroundColour(dmd.DEFAULT_HIGHLITE_COLOR)

####################################################################
## ViewContent
####################################################################
class ViewContent (wx.Panel):

  ####################################################################
  def __init__ (self, browse, results_notebook, name, cnx, data, search_term=None):
    wx.Panel.__init__ (self, parent=results_notebook, id=-1, name=name)
    self.browse = browse
    self.results_notebook = results_notebook
    self.results = results_notebook.GetParent()
    self.cnx = cnx
    self.data = data
    self.search_term = search_term

    normal_font_size = self.GetFont().GetPointSize()  # get the current size
    bigger_font_size = normal_font_size + 3

    ctype   = data.content_type
    trenc   = data.transfer_encoding
    isatt   = data.is_attachment
    ofn     = data.original_file_name
    charset = data.charset

    cnt = None
    if data.is_internal:
      cnt   = dba.get_internal_content_text(self.cnx, self.data.content_id)
    else:
      (folder_name, relative_path, account_id, account_name) = \
          dba.get_folder_info(self.cnx, data.folder_id)
      acc_dir = dba.get_account_directory(self.cnx, account_id)
      fld_dir = os.path.join(acc_dir, relative_path)
      path = os.path.join(acc_dir, fld_dir, data.stored_file_name)
      input = open(path)
      cnt   = input.read()
      input.close()
    if trenc == 'base64':
      cnt = base64.b64decode(cnt)
    elif trenc == 'quoted-printable':
      cnt = quopri.decodestring(cnt)
      ## simplfy EOLs; otherwise spacing gets doubled
      cnt = re.sub('\r\n', '\n', cnt)
    elif ctype == 'text/plain' or ctype == 'message/rfc822':
      ## simplfy EOLs; otherwise spacing gets doubled
      cnt = re.sub('\r\n', '\n', cnt)

    ofn_header = None
    sizer = wx.BoxSizer(wx.VERTICAL)
    if isatt and ofn:
      ofn_header = wx.StaticText(self, id=-1, name='', label='Attachment: ' + ofn)
      ofn_header.SetFont(wx.Font(normal_font_size, wx.SWISS, wx.NORMAL, wx.BOLD))
      sizer.Add(ofn_header, 0, wx.ALL, 5)

    if ctype == 'text/plain' or ctype == 'message/rfc822':
      try:

# In principle if Content-Transfer-Encoding="8bit" and
# charset="iso-8599-1", then we could encode/decode back to Latin_1,
# but that still won't help with proprietary character sets like charset="Windows-1252".
# Probably not worth trying, but ...
        if data.is_internal and (trenc == '8bit' and charset.lower() == 'iso-8599-1'):
          txt = self.compose_rich_text(dmc.utf_to_latin1_string(cnt))
        else:
          txt = self.compose_rich_text(cnt)
      except Exception as e:
#        print 'SetValue for text/plain', str(e)
        txt = self.highlite_rich_text(dmc.encode_for_character_set(cnt,
            dmc.CHARACTER_SET, 'xml'))
      sizer.Add(txt, 1, wx.EXPAND|wx.ALL, 5)
    elif ctype == 'text/html':
      h = wxhtml.HtmlWindow(self, id=-1, name='')
      try:
        h.SetPage(self.highlite_html(cnt))
      except Exception as e:
#        print 'SetPage for text/html:', str(e)
        h.SetPage(self.highlite_html(dmc.encode_for_character_set(cnt,
            dmc.CHARACTER_SET, 'xml')))
      sizer.Add(h, 1, wx.EXPAND|wx.ALL, 5)

    self.SetSizer(sizer)
    self.results.page_id = self.results.page_id + 1
    results_notebook.AddPage(self, str(self.results.page_id), select=True)
    self.browse.switch_to_results()

  ####################################################################
  def highlite_rich_text (self, cnt):
    rtc = rt.RichTextCtrl(self, id=-1, name='',
        style=wx.TE_READONLY|wx.TE_MULTILINE)
    if self.search_term:
      ms = re.finditer(self.search_term, cnt, re.I)
      i = 0
      for m in ms:
        (start, end) = m.span()
        rtc.WriteText(cnt[i:start])
        rtc.BeginStyle(hl_style)
        rtc.WriteText(cnt[start:end])
        rtc.EndStyle()
        i = end
      rtc.WriteText(cnt[i:len(cnt)])
    else:
      rtc.WriteText(cnt)
    return rtc

  ####################################################################
  def highlite_html (self, cnt):
    s = ''
    if self.search_term:
      ms = re.finditer("(<[^>]*>)|(" + self.search_term + ")", cnt, re.I)
      i = 0
      for m in ms:
        if m.group(1):
          (start, end) = m.span(1)
          s = s + cnt[i:end]
        elif m.group(2):
          (start, end) = m.span(2)
          s = s + cnt[i:start]
          s = s + '<span style="background-color: ' + \
              dmd.DEFAULT_HIGHLITE_COLOR + '">' + cnt[start:end] + '</span>'
        i = end
      s = s + cnt[i:len(cnt)]
    else:
      s = cnt
    return s
