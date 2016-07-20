#!/usr/bin/env python
######################################################################
## $Revision: 1.1 $
## $Date: 2016/02/11 23:38:42 $
## Author: Carl Schaefer, Smithsonian Institution Archives 
######################################################################

import time
import sys
import os
import re
import mailbox
import email
import wx
import  wx.lib.scrolledpanel as scrolled
from wx import DirPickerCtrl
import db_access as dba
import dm_common as dmc
from dm_common import EOL
import dm_defaults as dmd
import dm_wx
from dm_wx import FRAME_WIDTH, FRAME_HEIGHT, FRAME_XPOS, FRAME_YPOS
import message_group
import stop_watch
import info_window
import message_log
import hashlib

######################################################################
def message_hash (s):
  eol = None
  n = len(s)
## can't seem to get this eol match to work correctly
## not sure why...
  if s.rfind('\r') == n-1 or s.rfind('\r\n') == n-2:
    eol = 'CRLF'
  elif s.rfind('\n') == n-1:
    eol = 'LF'
  else:
#    print 'error: no reconized EOL at end of message'
    eol = None
  sha1  = hashlib.sha1()
  sha1.update(s)
  return (eol, sha1.hexdigest())

####################################################################
## ExportPanel
####################################################################
class ExportPanel (scrolled.ScrolledPanel):

  name2default   = {
    'folder_select'    : 0,
    'include_rb'       : True,
    'export_directory' : dmd.DEFAULT_EXPORT_DIRECTORY_PREFIX
  }
 
  ####################################################################
  def __init__ (self, parent, name):

    wx.ScrolledWindow.__init__ (self, parent=parent, id=-1, name=name)

    self.account_id        = None
    self.account_name      = ''
    self.account_directory = ''
    self.export_directory  = ''
    self.logf              = None
    self.cnx               = None
    self.log_name          = 'dm_export.log.txt'

    normal_font_size = self.GetFont().GetPointSize()  # get the current size
    bigger_font_size = normal_font_size + 3

    self.sizer = sizer = wx.BoxSizer(orient=wx.VERTICAL)
    self.SetSizer(sizer)
    self.SetupScrolling()


    sizer.Add((FRAME_WIDTH, 10))

    t1 = wx.StaticText(self, id=-1, label='Export Mbox File')
    t1.SetFont(wx.Font(bigger_font_size, wx.SWISS, wx.NORMAL, wx.BOLD))
    sizer.Add(t1, 0, wx.ALIGN_CENTER, 5)

    sizer.Add((FRAME_WIDTH, 15))

    box1 = wx.StaticBoxSizer(wx.StaticBox(self, -1, "" ), wx.VERTICAL)

    ##
    ## account name and directory
    ##

    account_grid = wx.FlexGridSizer(cols=2)
    grid_account_name = wx.StaticText(self, id=-1,
        label=self.account_name, name='static_account_name', style=wx.SIMPLE_BORDER)
    grid_account_directory = wx.StaticText(self, id=-1,
        label=self.account_directory, name='static_account_directory', style=wx.SIMPLE_BORDER)
    t1 = wx.StaticText(self, id=-1, label='Account:')
    account_grid.Add(t1, 0, wx.ALIGN_LEFT|wx.ALL, 5)
    account_grid.Add(grid_account_name, 0, wx.ALIGN_LEFT|wx.ALL, 5)
    t1 = wx.StaticText(self, id=-1, label='Account Directory:')
    account_grid.Add(t1, 0, wx.ALIGN_LEFT|wx.ALL, 5)
    account_grid.Add(grid_account_directory, 0, wx.ALIGN_LEFT|wx.ALL, 5)

    box1.Add(account_grid, 0, wx.ALIGN_LEFT, 5)

    box1.Add((-1, 15))

    ##
    ## export directory
    ##

    box1.Add(wx.StaticText(self, id=-1, label='Export Directory:'),
        0, wx.ALIGN_LEFT|wx.LEFT, 5)
    dpc = DirPickerCtrl(self, id=-1, size=(500,-1), name='export_directory')
    box1.Add(dpc, 0, wx.ALIGN_LEFT|wx.TOP|wx.LEFT, 5)
    
    sizer.Add(box1, 0, wx.ALIGN_LEFT|wx.ALL, 5)
    sizer.Add((FRAME_WIDTH, 15))

    box2 = wx.StaticBoxSizer(wx.StaticBox(self, -1, ""), wx.VERTICAL)

    ##
    ## folders
    ##

    hbox1 = self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
    hbox1.Add(wx.StaticText(self, id=-1, label='Select one or all folders:'),
        0, wx.ALIGN_LEFT|wx.ALL, 5)
    folder_select = wx.ComboBox(self, id=-1, style=wx.CB_DROPDOWN,
        choices=['[ALL FOLDERS'], name='folder_select')
    hbox1.Add(folder_select, 0, wx.ALIGN_LEFT|wx.LEFT|wx.BOTTOM, 5)
    box2.Add(hbox1, 0, wx.ALIGN_LEFT|wx.ALL, 5)

    ##
    ## include or exclude
    ##

    box2.Add(wx.StaticText(self, id=-1, label='Messages to be exported:'), 0, wx.ALIGN_LEFT|wx.ALL, 5)
    hbox2 = self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
    self.include_rb = wx.RadioButton(self, id=-1, name='include_rb', label='INCLUDE selected messages',
        style=wx.RB_GROUP)
    self.exclude_rb = wx.RadioButton(self, id=-1, name='exclude_rb', label='EXCLUDE selected messages')
    hbox2 = wx.BoxSizer(wx.HORIZONTAL)
    hbox2.Add((30, -1))
    hbox2.Add(self.include_rb, 0, wx.ALIGN_LEFT|wx.RIGHT, 5)
    hbox2.Add(self.exclude_rb, 0, wx.ALIGN_LEFT|wx.LEFT, 5)
    box2.Add(hbox2, 0, wx.ALIGN_LEFT|wx.LEFT|wx.TOP, 5)

    sizer.Add(box2, 0, wx.ALIGN_LEFT|wx.ALL, 5)

    ##
    ## action buttons
    ##
    sizer.Add(dm_wx.ActionButtons(self, 'Export Mbox'), 0, wx.ALIGN_CENTER, 5)
    sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
    sizer.Add((20,FRAME_HEIGHT))
    sizer.Add(sizer, 1, wx.EXPAND)

    self.FindWindowByName('reset_button').Bind(wx.EVT_LEFT_UP, self.ExecuteReset)
    self.FindWindowByName('go_button').Bind(wx.EVT_LEFT_UP, self.ValidateVariablesAndGo)
    self.Bind(wx.EVT_SHOW, self.NewExport)

  ####################################################################
  def get_folders (self):
    fids   = [0]
    fnames = ['[ALL FOLDERS]']
    fpaths = ['']
    mboxes = ['']
    query = "select f.id, f.folder_name, f.relative_path " + \
        "from folder f where f.account_id=" + str(self.account_id) + " " + \
        "order by f.folder_name"
    cursor = self.cnx.cursor()
    cursor.execute(query, None)
    for (fid, fname, fpath) in cursor:
      fids.append(fid)
      fnames.append(fname)
      fpaths.append(fpath)
      fp = os.path.abspath(os.path.join(self.account_directory, fpath))
      mbox = os.path.join(fp, fname + '.mbox')
      mboxes.append(mbox)
    cursor.close
    return (fids, fnames, fpaths, mboxes)

  ####################################################################
  def NewExport (self, event):
    if not event.GetShow():
      return
    bp = self.GetParent().bp
    if not self.cnx:
      self.cnx = bp.cnx
    if self.account_id != bp.current_account_id:
      self.make_account_header()
      self.make_folder_select()
      self.ExecuteReset()
      self.FindWindowByName('include_rb').SetValue(self.name2default['include_rb'])
      self.FindWindowByName('export_directory').SetPath(self.name2default['export_directory'])
      self.FindWindowByName('folder_select').SetSelection(self.name2default['folder_select'])
    self.Layout()

  ####################################################################
  def make_account_header (self):
    bp = self.GetParent().bp
    self.account_id   = bp.current_account_id
    self.account_name = bp.current_account_name
    self.account_directory = dba.get_account_directory(self.cnx, self.account_id)
    self.FindWindowByName('static_account_name').SetLabel(self.account_name)
    self.FindWindowByName('static_account_directory').SetLabel(self.account_directory)

  ####################################################################
  def make_folder_select (self):
    (self.fids, self.fnames, self.fpaths, self.mboxes) = self.get_folders()
    old_folder_select = self.FindWindowByName('folder_select')
    new_folder_select = wx.ComboBox(self, id=-1, style=wx.CB_DROPDOWN,
        choices=self.fnames)
    if old_folder_select:
      self.hbox1.Replace(old_folder_select, new_folder_select)
      old_folder_select.Destroy()
    else:
      self.hbox1.Add(new_folder_select, 0, wx.ALIGN_LEFT|wx.LEFT|wx.BOTTOM, 5)
    new_folder_select.SetName('folder_select')
    
  ####################################################################
  def ExecuteReset (self, event=None):
    self.FindWindowByName('include_rb').SetValue(True)
    self.FindWindowByName('export_directory').SetPath(self.name2default['export_directory'])
    self.FindWindowByName('folder_select').SetSelection(self.name2default['folder_select'])
    self.GetParent().SetFocus()

  ####################################################################
  def LogVariables(self):
    self.logf.write('########## SETTINGS ##########' + '\n')
    self.logf.write('account: ' + self.account_name + '\n')

  ######################################################################
  def ValidateFolders (self, idx, account_directory, fpaths, mboxes):
    if idx:    ## one folder
      mbox = mboxes[idx]
      if not os.path.exists(mbox):
        return 'mbox file ' + mbox + ' does not exist'
      elif not os.path.isfile(mbox):
        return 'mbox file ' + mbox + ' is not a file'
      else:
        return ''
    else:                  ## all folders
      for i in range(1,len(fpaths)):
        mbox = mboxes[i]
        if not os.path.exists(mbox):
          return 'mbox file ' + mbox + ' does not exist'
        elif not os.path.isfile(mbox):
          return 'mbox file ' + mbox + ' is not a file'
        else:
          return ''
    return ''

  ######################################################################
  def ValidateExportDirectory (self, dir):
    if dir:
      self.export_directory = d = os.path.abspath(dir.strip())
      if not os.path.exists(d):
        return 'export directory ' + d + \
              ' does not exist'
      elif not os.path.isdir(d):
        return d + ' is not a directory'
      else:
        return ''
    else:
      return 'null export directory'

  ######################################################################
  def ValidateVariablesAndGo (self, event):
    ready = True

    msg = self.ValidateExportDirectory(self.FindWindowByName('export_directory').GetPath())
    if msg != '':
      md = wx.MessageDialog(parent=self, message=msg, caption='Error',
          style=wx.OK|wx.ICON_EXCLAMATION)
      retcode = md.ShowModal()
      ready = False
      return

    idx = self.FindWindowByName('folder_select').GetSelection()
    msg = self.ValidateFolders(idx, self.account_directory, self.fpaths, self.mboxes)
    if msg != '':
      md = wx.MessageDialog(parent=self, message=msg, caption='Error',
          style=wx.OK|wx.ICON_EXCLAMATION)
      retcode = md.ShowModal()
      ready = False
      return

    if ready:
      if idx == 0:
        fids_to_scan      = self.fids[1:len(self.fids)]
        fnames_to_scan    = self.fnames[1:len(self.fnames)]
        mboxes            = self.mboxes[1:len(self.mboxes)]
      else:
        fids_to_scan      = [self.fids[idx]]
        fnames_to_scan    = [self.fnames[idx]]
        mboxes            = [self.mboxes[idx]]
      include = self.FindWindowByName('include_rb').GetValue()
      self.FindWindowByName('go_button').Disable()
      self.export_data(self.account_id, self.export_directory,
          fids_to_scan, fnames_to_scan, mboxes, include)
      self.FindWindowByName('go_button').Enable()
        
  ######################################################################
  def get_exportable_glids (self, account_id, fid, include):
    mg = message_group.message_group_for_account(account_id)
    glids = set()
    query = "select m.id, m.global_message_id, m.date_time " + \
      "from message m where m.folder_id=" + str(fid) + " " +\
      "order by m.date_time"
    cursor = self.cnx.cursor()
    cursor.execute(query, None)
    for (mid, glid, dt) in cursor:
      if include and mid in mg:
        glids.add(glid)
      elif not include and mid not in mg:
        glids.add(glid)
    cursor.close
    return glids

  ######################################################################
  def export_data (self, account_id, export_directory,
      fids, fnames, mboxes, include):
    self.logf = open(os.path.join(self.export_directory, self.log_name) , 'w')
    self.LogVariables()
    self.sw = stop_watch.StopWatch()
    for i in range(0,len(fids)):
      glids = self.get_exportable_glids(account_id, fids[i], include)
      if len(glids) > 0:
        busy = wx.BusyInfo('Exporting from folder ' + fnames[i])
        self.export_folder(export_directory, fids[i], fnames[i], mboxes[i], glids)
        busy = None
      else:
        self.logf.write('Folder ' + fnames[i] + ' has no selected messages ' + EOL)
    self.logf.write(EOL + '########## ELAPSED TIME ##########' + EOL)
    self.logf.write(self.sw.elapsed_time() + EOL)
    self.logf.close()
    self.logf = open(os.path.join(self.export_directory, self.log_name))
    message = self.logf.read()
    self.logf.close()
    summary_info = info_window.InfoWindow(self, 'Export Summary', message)
    summary_info.Show(True)
    summary_info.SetFocus()

  ######################################################################
  def message_summary_row (self, em, sha1_digest):
    merrors = []
    mlrow = message_log.MessageLogRow()
    for tag in ['From', 'To', 'Subject', 'Date', 'Message-ID']:
      if em[tag]:
        if tag   == 'From':
          mlrow.add_from(em[tag])
        elif tag == 'To':
          mlrow.add_to(em[tag])
        elif tag == 'Subject':
          mlrow.add_subject(em[tag])
        elif tag == 'Date':
          mlrow.add_date(em[tag])
        elif tag == 'Message-ID':
          mlrow.add_messageid(em[tag])
      else:
        merrors.append(tag + ' header is missing')
    mlrow.add_hash(sha1_digest)
    mlrow.add_errors(len(merrors))
    if len(merrors) > 0:
      mlrow.add_firstmessage(merrors[0])
    return mlrow

  ######################################################################
  def export_folder (self, export_directory, fid, fname, mbox, glids):
    mlfn = os.path.join(export_directory, fname + '.csv')
    mlog = open(mlfn, 'wb')
    mlf = message_log.MessageLog(mlog)
    exf = open(os.path.join(export_directory, fname + '.mbox'), 'wb')
    mb = mailbox.mbox(mbox, create=False)
    exported_msgs = 0
    for i in range(len(mb)):
      mes = mb.get_message(i)
      mes_string = mes.as_string()
      (eol, sha1_digest) = message_hash(mes_string)
      em = email.message_from_string(mes_string)
      glid = em.get('Message-ID')
      if glid in glids:
        # 'From '-line minus 'From ' and minus newline
        fl =  mes.get_from()
        exf.write('From ' + fl + os.linesep)
        exf.write(mes_string)
        exf.write(os.linesep)
        exported_msgs += 1
        mlf.writerow(self.message_summary_row(em, sha1_digest))
    exf.close()
    mlog.close()
    self.logf.write('Folder ' + fname + ': ' + \
        str(exported_msgs) + ' messages exported' + EOL)

  ####################################################################
  def LogVariables (self):
    self.logf.write('########## SETTINGS ##########' + EOL)
    self.logf.write('account: ' + self.account_name + EOL)
    self.logf.write('account directory: ' + self.account_directory + EOL)
    self.logf.write('export directory: ' + self.export_directory + EOL)
    idx = self.FindWindowByName('folder_select').GetSelection()
    self.logf.write('folder(s): ' + self.fnames[idx] + EOL)
    include = self.FindWindowByName('include_rb').GetValue()
    if include:
      self.logf.write('Export INCLUDES selected messages' + EOL)
    else:
      self.logf.write('Export EXCLUDES selected messages' + EOL)
    self.logf.write(EOL + '########## SUMMARY ##########' + EOL)

