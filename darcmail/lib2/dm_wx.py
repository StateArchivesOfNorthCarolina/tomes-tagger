#!/usr/bin/env python
######################################################################
## $Revision: 1.2 $
## $Date: 2016/02/11 23:38:42 $
## Author: Carl Schaefer, Smithsonian Institution Archives 
######################################################################

import time
import os
import re
import wx
from wx import DirPickerCtrl
import db_access as dba
import dm_common as dmc
import dm_defaults as dmd
import xml_common

FRAME_WIDTH  = 650
FRAME_HEIGHT = 700
FRAME_XPOS   = 250
FRAME_YPOS   = 150

LIST_RESULT_SIZE = (FRAME_WIDTH-50, FRAME_HEIGHT-150)

button_names = [
    'reset_button',
    'go_button',
    'default_button'
]

MAX_LIST_SIZE            = 30
MAX_DISPLAYED_PAGE_LINKS = 6

####################################################################
def ValidateLogFile (p):
  ## called AFTER ValidateDirectory
  if p.logf:
    p.logf.close()
  p.log_name = os.path.join(
    p.directory,
    'log.' + p.sub_dir + '.txt')
  try:
    p.logf = open(p.log_name, 'w')
  except:
    return 'cannot open log file ' + p.log_name + ' for writing'
  return ''
    
####################################################################
def FindFolderName (folder_data, fname):
  for (folder_name, folder_mbox, folder_dir, folder_size,
      folder_id) in folder_data:
    if fname == folder_name:
      return (folder_name, folder_mbox, folder_dir, folder_size,
          folder_id)
  return (None, None, None, None, None)

####################################################################
def FindMboxFiles (p, folder_data, parent):
  for f in os.listdir(parent):
    child = os.path.join(parent, f)
    if os.path.isdir(child):
      FindMboxFiles(p, folder_data, child)
    else:
      m = re.match('.*\.mbox$', f)
      if m:
        folder_name = re.sub('\.mbox$', '', f)
        folder_mbox = os.path.basename(child)
        folder_dir  = os.path.dirname(child)
        folder_size = os.path.getsize(child)
        folder_id   = None
        if p.account_id:
          folder_id = dba.get_folder_id(p.cnx, p.account_id,
            folder_name, None, make=False)
        folder_data.append((folder_name, folder_mbox, folder_dir,
            folder_size, folder_id))

####################################################################
def ValidateDirectory (p, account_dir):
  if account_dir:
    p.account_dir = os.path.abspath(account_dir.strip())
    if not os.path.exists(p.account_dir):
      return 'account directory ' + p.account_dir + \
            ' does not exist'
    elif not os.path.isdir(p.account_dir):
      return p.dir + ' is not a directory'
    else:
      return ''
  else:
    return 'null account directory'

####################################################################
def ValidateAccount (p, account):
  p.account = account.strip();
  if p.account == '':
    return 'You must specify the name of the email account'
  return ''

####################################################################
def ValidateLimits (p, folder_flag, folder):
  p.folder_cb = folder_flag
  p.folder    = folder.strip()  
  if p.folder_cb:
    if p.folder == '':
      return 'If limiting to a folder, you must give the folder name'
    else:
      pass
  return ''

####################################################################
def ValidateDatabaseVariables (p, user, passwd, dbhost, db):
  p.username = user.strip()
  p.password = passwd
  p.host     = dbhost.strip()
  p.database = db.strip()
  if p.cnx != None:
    p.cnx.close()
    p.cnx = None
  try:
    p.cnx = dba.connect(p.username,
        p.password, p.host, p.database)
  except:
    p.cnx = None
    return 'cannot connect to ' + p.database + '@' + p.host + \
        ' using username ' + p.username + ' and password specified'
  return '' 

####################################################################
def ExternalStorage (p, pname):
  box = wx.StaticBoxSizer(wx.StaticBox(p, -1, "" ), wx.VERTICAL)
  box.Add(wx.StaticText(p, id=-1, label='External Content Storage...'),
      0, wx.ALIGN_CENTER|wx.ALL, 5)

#  if dmc.ALLOW_ALLOCATION_CHOICE:
#    disposition_radio = wx.RadioButton(p, -1, " By Disposition ",
#        name="disposition_radio", style = wx.RB_GROUP )
#    size_radio  = wx.RadioButton(p, -1, " By Size ", name="size_radio")

#    hbz  = wx.BoxSizer(wx.HORIZONTAL)
#    hbz.Add(disposition_radio, 0, wx.ALIGN_LEFT|wx.ALL, 5)
#    hbz.Add((20, 5))
#    hbz.Add(size_radio, 0, wx.ALIGN_LEFT|wx.ALL, 5)
#    box.Add(hbz, 0, wx.ALIGN_LEFT|wx.ALL, 5)

  grid = wx.FlexGridSizer(cols=2)

  if pname == 'DArcMail':
    max_internal_label = wx.StaticText(p, id=-1, name="max_internal_label",
       label="Max size for internal storage:")
    max = wx.ComboBox(p, id=-1, name='max_internal', style=wx.CB_DROPDOWN,
       choices=['0', '10000', '20000', '30000', '40000', '50000', '60000'])
    grid.Add(max_internal_label, 0, wx.ALIGN_RIGHT|wx.TOP|wx.BOTTOM, 5)
    grid.Add(max, 0, wx.ALIGN_LEFT|wx.LEFT|wx.BOTTOM, 5)

  elif pname == 'DArcMailXml':
    max_internal_label = wx.StaticText(p, id=-1, name="max_internal_label",
       label="Max size for internal storage of attachments:")
    max = wx.ComboBox(p, id=-1, name='max_internal', style=wx.CB_DROPDOWN,
       choices=['0', '10000', '20000', '30000', '40000', '50000', '60000'])
    grid.Add(max_internal_label, 0, wx.ALIGN_RIGHT|wx.TOP|wx.BOTTOM, 5)
    grid.Add(max, 0, wx.ALIGN_LEFT|wx.LEFT|wx.BOTTOM, 5)

  grid.Add(wx.StaticText(p, id=-1,
      label='Create subdirectories for external storage?:'),
      0, wx.ALIGN_RIGHT|wx.TOP, 5)
  cb = wx.CheckBox(p, id=-1, name='levels_cb', label='yes')
  grid.Add(cb, 0, wx.ALIGN_LEFT|wx.TOP, 5)

  if dmc.ALLOW_WRAP_CHOICE:
    grid.Add(wx.StaticText(p, id=-1, label="Wrap external content in XML?"),
        0, wx.ALIGN_RIGHT|wx.TOP, 5)
    cb = wx.CheckBox(p, id=-1, name='wrap_cb', label='yes')
    grid.Add(cb, 0, wx.ALIGN_LEFT|wx.TOP, 5)

  box.Add(grid)
  return box

######################################################################
def Limits (p, panel_type):

  grid = wx.FlexGridSizer(cols=2)

  grid.Add(wx.StaticText(p, id=-1, label='Do only one folder?:'),
      0, wx.ALIGN_RIGHT|wx.TOP|wx.BOTTOM|wx.RIGHT, 5)
  hsz = wx.BoxSizer(orient=wx.HORIZONTAL)
  txc = wx.TextCtrl(p, id=-1, name='folder', size=(200, -1))
  ncb = wx.CheckBox(p, id=-1, name='folder_cb', label='yes, limit to:')
  hsz.Add(ncb, 0, wx.RIGHT|wx.TOP, 5)
  hsz.Add(txc, 0, wx.LEFT|wx.TOP, 5)
  grid.Add(hsz, 0, wx.ALIGN_LEFT)

  if panel_type == 'Delete':
    pass
#    grid.Add(wx.StaticText(p, id=-1, label='Remove externally stored content?:'),
#        0, wx.ALIGN_RIGHT|wx.TOP, 5)
#    cb = wx.CheckBox(p, id=-1, name='rmex_cb', label='yes')
#    grid.Add(cb, 0, wx.ALIGN_LEFT|wx.TOP, 5)

  elif panel_type == 'Xml':
    grid.Add(wx.StaticText(p, id=-1, label='Split large export into chunks?:'),
        0, wx.ALIGN_RIGHT|wx.TOP|wx.BOTTOM|wx.RIGHT, 5)
    hz1 = wx.BoxSizer(orient=wx.HORIZONTAL)
    chunk = wx.ComboBox(p, id=-1, name='chunksize', style=wx.CB_DROPDOWN,
        choices=["don't split", '1,000', '5,000', '10,000'])
    hz1.Add(chunk, 0, wx.ALIGN_LEFT, 5)
    hz1.Add(wx.StaticText(p, id=-1, label='messages per XML file'), 0, wx.LEFT|wx.TOP, 5)
    grid.Add(hz1, 0, wx.ALIGN_LEFT)

  box = wx.StaticBoxSizer(wx.StaticBox(p, -1, "" ), wx.VERTICAL)
  box.Add(grid)
  return box
  
######################################################################
def Paths (p, panel_type):

  box = wx.StaticBoxSizer(wx.StaticBox(p, -1, "" ), wx.VERTICAL)

  grid = wx.FlexGridSizer(cols=2)
  
  grid.Add(wx.StaticText(p, id=-1, label='Name:'),
      0, wx.ALIGN_RIGHT|wx.TOP, 5)
  txc = wx.TextCtrl(p, id=-1, name='account', size=(200, -1))
  grid.Add(txc, 0, wx.ALIGN_LEFT|wx.LEFT|wx.TOP|wx.BOTTOM, 5)

  if panel_type in  ['Load', 'Xml']:
    grid.Add(wx.StaticText(p, id=-1, label='Directory:'),
        0, wx.ALIGN_RIGHT|wx.TOP, 5)
    dpc = DirPickerCtrl(p, id=-1, size=(500,-1), name='account_dir')
    grid.Add(dpc, 0, wx.ALIGN_LEFT)

  box.Add(wx.StaticText(p, id=-1, label='Email Account Information...'),
      0, wx.ALIGN_CENTER|wx.ALL, 5)
  box.Add(grid, 0, wx.ALIGN_LEFT|wx.LEFT, 5)

  return box
  
######################################################################
def DatabaseNames (p):

  db_grid = wx.FlexGridSizer(cols=4)

  db_grid.Add(wx.StaticText(p, id=-1, label='Database Host:'),
      0, wx.ALIGN_RIGHT|wx.ALL, 5)
  db_grid.Add(wx.TextCtrl(p, id=-1, name='host', size=(150, -1)),
      0, wx.ALIGN_LEFT|wx.ALL, 5)
  db_grid.Add(wx.StaticText(p, id=-1, label='Database Name:'),
      0, wx.ALIGN_RIGHT|wx.ALL, 5)
  db_grid.Add(wx.TextCtrl(p, id=-1, name='database', size=(150, -1)),
      0, wx.ALIGN_LEFT|wx.ALL, 5)

  db_grid.Add(wx.StaticText(p, id=-1, label='UserName:'),
      0, wx.ALIGN_RIGHT|wx.ALL, 5)
  db_grid.Add(wx.TextCtrl(p, id=-1, name='username', size=(150, -1)),
      0, wx.ALIGN_LEFT|wx.ALL, 5)
  db_grid.Add(wx.StaticText(p, id=-1, label='Password:'),
      0, wx.ALIGN_RIGHT|wx.ALL, 5)
  db_grid.Add(wx.TextCtrl(p, id=-1, name='password', style=wx.TE_PASSWORD, size=(150, -1)),
      0, wx.ALIGN_LEFT|wx.ALL, 5)

  db_box = wx.StaticBoxSizer(wx.StaticBox(p, -1, "" ), wx.VERTICAL)
  db_box.Add(db_grid)

  return db_box

######################################################################
def ActionButtons (p, go_label):
  bx = wx.BoxSizer(orient=wx.HORIZONTAL)
  rb = wx.Button(p, id=-1, label='Reset', name='reset_button')
  gb = wx.Button(p, id=-1, label=go_label, name='go_button')
  bx.Add(rb, 1, wx.ALL, 5)
  bx.Add(gb, 1, wx.ALL, 5)
  return bx

