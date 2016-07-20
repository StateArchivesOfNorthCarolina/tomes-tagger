#!/usr/bin/env python
######################################################################
## $Revision: 1.5 $
## $Date: 2016/02/19 13:10:20 $
## Author: Carl Schaefer, Smithsonian Institution Archives 
######################################################################

import sys
import os
import re
import string
import hashlib
import uuid
import mailbox
import email
import base64
import xml_common
import message_log
import stop_watch
import dm_common as dmc
from dm_common import EOL
import dm_defaults as dmd
from xml_common import message_predef_seq, body_predef_seq, \
    message_predef, body_predef, \
    isOtherMimeHeader, escape_xml

eol_chars           = 'CRLF'
MLOG_NAME           = 'MessageSummary'

## name/address formats
## "Last, First" <last@abc.gov>
na_case1 = '("([^"]+,?[^"]+") *<[^>]*>)'
## last@abc.gov
na_case2 = '([^",<> ]+@[^",<> ]+)'
## First Last <last@abc.gov>
na_case3 = '([^",]+ *<[^>]+>)'
na_rx = re.compile('(' + '|'.join((na_case1, na_case2, na_case3)) + ')')

log_file_name = 'mbox2db.log.txt'

######################################################################
class GlobalIdRecord ():

  def __init__ (self):
   self.glidr = set()

  def add_message (self, glid):
    self.glidr.add(glid)

  def has_message (self, glid):
    return glid in self.glidr

######################################################################
def check_file_for_reading (f):
  if not os.path.exists(f):
    print 'mbox file ' + f + ' does not exist'
    return False
  if not os.path.isfile(f):
    print f + ' must be a file, not a directory'
    return False
  if not os.access(f, os.R_OK):
    print 'mbox file ' + f + ' is not readable' 
    return False
  return True

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

######################################################################
class FolderInfo ():
  def __init__ (self, mbox_path=None, folder_path=None,
      relative_path=None, folder_name=None):
    self.mbox_path     = mbox_path
    self.folder_path   = folder_path
    self.relative_path = relative_path
    self.folder_name   = folder_name

######################################################################
## Mbox2Xml
######################################################################
class Mbox2Xml ():

  #####################################################################
  def __init__ (self, logf, account_name, account_directory,
      folder_name, folder_directory, max_internal_size,
      external_subdir_levels, output_chunksize, xml_wrap):

    self.logf              = logf
    self.account_name      = account_name
    self.account_directory = account_directory
    self.folder_name       = folder_name
    self.folder_directory  = folder_directory
      ## folder_directory will change as the account_directory is walked
      ## folder_directory is relative to account_directory
    self.max_internal_size     = max_internal_size
    self.external_subdir_levels = external_subdir_levels
    self.output_chunksize  = output_chunksize
    self.xml_wrap          = xml_wrap

    self.lc_original2xml   = self.build_tag_dictionary()
    self.xc                = xml_common.XMLCommon()

    self.warnings           = {}
    self.progress_dialog    = None
    self.estimated_total_messages = 0
    self.total_mbox_messages = 0    ## number before removing duplicates
    self.skipped_duplicates  = 0
    self.total_msg_count     = 0    ## total messages in XML output
    self.message_count       = 0    ## resettable count for chunking
    self.output_files       = []
    self.increment          = None
    self.progress_dialog    = None
    self.external_content_files = 0
    self.sw = stop_watch.StopWatch()
    self.glidr = GlobalIdRecord()

  #####################################################################
  def build_tag_dictionary (self):
    dict = {
      'boundary' : 'BoundaryString',
      'cc' : 'Cc',
      'charset' : 'Charset',
      'content-id' : 'ContentId',
      'content-type' : 'ContentType',
      'content-disposition' : 'Disposition',
      'filename' : 'DispositionFileName',
      'from' : 'From',
      'in-reply-to' : 'InReplyTo',
      'message-id' : 'MessageId',
      'mime-version' : 'MimeVersion',
      'date' : 'OrigDate',
      'references' : 'References',
      'sender' : 'Sender',
      'subject' : 'Subject',
      'to' : 'To',
      'content-transfer-encoding' : 'TransferEncoding',
      'bcc' : 'Bcc'
    }
    return dict

  #####################################################################
  def set_progress_dialog (self, progress_dialog, estimated_total_messages):
    self.progress_dialog = progress_dialog
    self.estimated_total_messages = estimated_total_messages

  ######################################################################
  def warning (self, w):
    if w in self.warnings.keys():
      self.warnings[w] = self.warnings[w] + 1
    else:
      self.warnings[w] = 1

  ######################################################################
  def write_warnings (self):
    for w in self.warnings.keys():
      self.logf.write(w + ' (' + str(self.warnings[w]) + ' times)' + EOL)

  ######################################################################
  def write_log (self):
    for fn in self.output_files:
      self.logf.write('output file: ' + fn + EOL)
    self.logf.write(EOL)
    self.logf.write('########## WARNINGS ##########' + EOL)
    self.write_warnings()
    self.logf.write(EOL)
    self.logf.write('########## SUMMARY ##########' + EOL)
    self.logf.write('total messages in mbox file(s): ' + \
        str(self.total_mbox_messages) + EOL)
    self.logf.write('duplicate messages skipped: ' + \
        str(self.skipped_duplicates) + EOL)
    self.logf.write('total messages in XML output: ' + str(self.total_msg_count) + EOL)
    self.logf.write('external content files: ' + str(self.external_content_files) + EOL)
    self.logf.write(EOL)
    self.logf.write('########## ELAPSED TIME ##########' + EOL)
    self.logf.write(self.sw.elapsed_time() + EOL)

  ######################################################################
  def add_subdirs (self, storage_root, uuid):
    # take the second group
    d1 = uuid[ 9:11]
    d2 = uuid[11:13]
    SUBDIR_LEVELS = self.external_subdir_levels
    added_levels = ''
    if SUBDIR_LEVELS == 0:
      return added_levels
    elif SUBDIR_LEVELS > 2:
      print 'too many subdir levels: ', SUBDIR_LEVELS
      sys.exit(1) 
    else:
      subdir = os.path.join(storage_root, d1)
      added_levels = d1
      if not os.path.exists(subdir):
        os.mkdir(subdir)
        os.chmod(subdir, dmd.EXTERNAL_CONTENT_DIRECTORY_PERMISSIONS)
      elif not os.path.isdir(subdir):
        print subdir, ' is not a directory '
        sys.exit(1)
      if SUBDIR_LEVELS == 1:
        return added_levels
      else:                   # SUBDIR_LEVELS == 2
        subdir = os.path.join(subdir, d2)
        added_levels = os.path.join(d1, d2)
        if not os.path.exists(subdir):
          os.mkdir(subdir)
          os.chmod(subdir, dmd.EXTERNAL_CONTENT_DIRECTORY_PERMISSIONS)
        elif not os.path.isdir(subdir):
          print subdir, ' is not a directory '
          sys.exit(1)
        return added_levels

  ######################################################################
  def get_content (self, part):
    content = part.as_string()
    # Skip headers, go to the content
    content_start = content.find('\n\n')
    # ..and skip the two linefeeds
    content = content[content_start+2:]
    m = re.match('^\s*$', content)
    if m:
      return (0, '')
    else:
      if part.get('Content-Transfer-Encoding') == 'quoted-printable':
       # have to remove some illegal quoted-printable moves that mbox makes
        content = re.sub('(=\r\n)|(=\r)|(=\n)', '', content)
      return (len(content), content)

  ######################################################################
  def external_content (self, part, content, fld):
    ## we are not attempting to optimize external storage,
    ## so just go with the 'full_sha1_digest'

    # uuid4 makes random uuids (not based on host id and time)
    cs_uuid = str(uuid.uuid4())
    stored_file_name = ''
    if self.xml_wrap:
      stored_file_name = cs_uuid + '.xml'
    else:
      stored_file_name = cs_uuid + '.raw'
    added_levels = self.add_subdirs(fld.folder_path, cs_uuid)
    stored_file_name = os.path.join(added_levels, stored_file_name)
    full_stored_file_name = os.path.join(fld.folder_path, stored_file_name)
    fh = open(full_stored_file_name, 'wb')
    os.chmod(full_stored_file_name, dmd.EXTERNAL_CONTENT_FILE_PERMISSIONS)
    self.external_content_files = self.external_content_files + 1

    if self.xml_wrap:
      content_type              = part.get_content_type()
      content_transfer_encoding = part.get('Content-Transfer-Encoding')
      disposition               = part.get('Content-Disposition')
      if re.match('attachment', disposition):
        disposition = 'attachment'
      disposition_filename      = part.get_filename()

      fh.write('<ExternalBodyPart>' + EOL)
      fh.write('<LocalUniqueID>' + cs_uuid + '</LocalUniqueID>' + EOL)
      fh.write('<ContentType>' + content_type + '</ContentType>' + EOL)
      if disposition:
        fh.write('<Disposition>' + disposition + '</Disposition>' + EOL)
      if disposition_filename:
        fh.write('<DispositionFileName>' + escape_xml(disposition_filename) + \
            '</DispositionFileName>' + EOL)
      if content_transfer_encoding:
        fh.write('<ContentTransferEncoding>' + content_transfer_encoding + \
            '</ContentTransferEncoding>' + EOL)
      fh.write('<Content>' + EOL)
      if content_transfer_encoding == 'base64':
        fh.write(content)
      else:
        fh.write(escape_xml(content))
      fh.write('</Content>' + EOL)
      fh.write('</ExternalBodyPart>' + EOL)

    else:
      fh.write(content)
    fh.close()

    fh = open(full_stored_file_name, 'rb')
    full_sha1  = hashlib.sha1()
    full_sha1.update(fh.read())
    full_sha1_digest = full_sha1.hexdigest()
    fh.close()
    return (stored_file_name, full_sha1_digest)

  #####################################################################
  def do_content(self, part, fld):
    (content_length, content_text) = self.get_content(part)
    if content_length < 1:
      return
    cd = part.get('Content-Disposition')
    is_attachment = cd and re.match('attachment', cd)
    make_external = False
#    if self.max_internal_size == -1 and is_attachment:
#      ## decision is disposition-based
#      make_external = True
    if is_attachment and content_length > self.max_internal_size:
      ## decision is size-based
      make_external = True
    if make_external:
      (stored_file_name, sha1_digest) = \
          self.external_content(part, content_text, fld)
      self.xc.ExtBodyContent('./' + stored_file_name, str(self.xc.getLocalId()),
          self.xml_wrap, sha1_digest)
    else:
      transfer_encoding = part.get('Content-Transfer-Encoding')
      self.xc.Content(content_text, transfer_encoding)

 ######################################################################
  def do_child_message (self, part, fld, merrors):
    # <ChildMessage> needs to have these two initial headers
    # <LocalId>
    # <MessageID>    --- but this one appears to be absent...
    self.xc.prl('<SingleBody>')
    self.xc.indent()
    child = None
    ok = True
    pls = part.get_payload()
    if not pls or len(pls) == 0:
      ok = False
      me = 'no MessageId for child'
      self.warning(me)
      merrors.append(me)
    elif len(pls) > 1:
      ok = False
      me = 'child message has multiple parts'
      self.warning(me)
      merrors.append(me)
    else:
      child = pls[0]
      htags = child.keys()
      for tag in ['From', 'To', 'Date', 'Subject']:
        if tag not in htags:
          me = 'child message lacks required header ' + tag + ':'
          self.warning(me)
          merrors.append(me)
          ok = False
          break
    if ok:
      self.do_part_headers(part)
      self.xc.prl('<ChildMessage>')
      self.xc.indent()
      self.xc.terminal('LocalId', str(self.xc.getLocalId()))
      (predef, non_predef) = self.process_headers(child)
      if 'MessageId' not in predef.keys():
        self.xc.terminal('MessageId', str(uuid.uuid4()))
      dummy = message_log.MessageLogRow()
      self.do_message_headers(child, dummy)
      self.do_part(child, fld, merrors, first_part=True)
      self.xc.exdent()
      self.xc.prl('</ChildMessage>')
    else:
      self.xc.Content(part.as_string(), transfer_encoding=None)
    self.xc.exdent()
    self.xc.prl('</SingleBody>')

 ######################################################################
  def do_part (self, part, fld, merrors, first_part=False):
    # parts with Content-Type == 'message/...' are parsed
    # such that part.is_multipart() is True, but they
    # need to be chid messages
    # message/rfc822
    # message/delivery-status
    content_type = part.get_content_type()
    if re.match('message/rfc822', content_type):
      self.do_child_message(part, fld, merrors)
    elif re.match('message/', content_type):
      me = 'skipping message part with ContentType: ' + content_type
      self.warning(me)
      merrors.append(me)
    elif part.is_multipart():
      self.xc.prl('<MultiBody>')
      self.xc.indent()
      if not part.get_boundary():
        me = 'multipart with no boundary string'
        self.warning(me)
        merrors.append(me)
      self.do_part_headers(part)
      # any content for a "main" multipart is a preamble
      if part.preamble:
        self.xc.terminal('Preamble', part.preamble)
      for subpart in part.get_payload():
        self.do_part(subpart, fld, merrors, first_part=False)
      self.xc.exdent()
      self.xc.prl('</MultiBody>')
    else:
      self.xc.prl('<SingleBody>')
      self.xc.indent()
      self.do_part_headers(part)
      self.do_content(part, fld)
      self.xc.exdent()
      self.xc.prl('</SingleBody>')
    if part.defects:
      for d in part.defects:
        me = 'message defect: ' + str(d)
        self.warning(me)
        merrors.append(me)

  ######################################################################
  def do_message_headers (self, em, mlrow):
    regular_date = None
    (predef, non_predef) = self.process_headers(em)
    for tag in message_predef_seq:
      if tag in predef.keys() and tag not in body_predef:
        if tag == 'OrigDate':
          self.xc.terminal(tag, dmc.strict_datetime(predef[tag]))
          regular_date = predef[tag]
          mlrow.add_date(regular_date)
        else:
          if tag   == 'From':
            mlrow.add_from(predef[tag])
          elif tag == 'To':
            mlrow.add_to(predef[tag])
          elif tag == 'Subject':
            mlrow.add_subject(predef[tag])
          elif tag == 'Date':
            mlrow.add_date(regular_date)
          elif tag == 'MessageId':
            mlrow.add_messageid(predef[tag])
          self.xc.terminal(tag, predef[tag])
    if regular_date:
      self.xc.Header('Date', regular_date)
    for tag in non_predef.keys():
      if not isOtherMimeHeader(tag):
        self.xc.Header(tag, non_predef[tag])

  ######################################################################
  def do_part_headers (self, part):
    (predef, non_predef) = self.process_headers(part)
    for tag in body_predef_seq:
      if tag in predef.keys() and tag not in message_predef:
        self.xc.terminal(tag, predef[tag])
    for tag in non_predef:
      if isOtherMimeHeader(tag):
        self.xc.OtherMimeHeader(tag, non_predef[tag])

  ######################################################################
  def process_headers (self, em):
    predef      = {}
    non_predef  = {}
    for (tag, value) in em.items():
      if not value:
#        self.warning('skipping tag ' +  tag + '; empty value')
        continue
      xml_tag = ''
      ltag = tag.lower()
      if ltag in self.lc_original2xml.keys():
        xml_tag = self.lc_original2xml[ltag]
      if xml_tag != '':
        # it's a predefined tag
        if xml_tag == 'ContentType':
          predef[xml_tag] = em.get_content_type()
          charset = em.get_content_charset();
          if charset:
            predef['Charset'] = charset
          boundary = em.get_boundary()
          if boundary:
            predef['BoundaryString'] = boundary
        elif xml_tag == 'TransferEncoding':
          predef[xml_tag] = value
        elif xml_tag == 'Disposition':
          m = re.match('attachment', value)
          if m:
            predef[xml_tag] = 'attachment'
            fn = em.get_filename()
            if fn:
              predef['DispositionFileName'] = fn
        else:
          predef[xml_tag] = value
      else:
        # it's NOT a predefined tag
        non_predef[tag] = value
    return (predef, non_predef)

  ######################################################################
  def do_message (self, em, eol, sha1_digest, fld):
    merrors = []
    (predef, non_predef) = self.process_headers(em)
    mlrow = message_log.MessageLogRow()
    if 'MessageId' not in predef.keys():
      merrors.append('no "MessageId" header for message')
    self.xc.prl('<Message>')
    self.xc.indent()
    self.xc.terminal('RelPath', fld.relative_path)
    self.xc.terminal('LocalId', str(self.xc.getLocalId()))
    if 'MessageId' not in predef.keys():
      self.xc.terminal('MessageId', str(uuid.uuid4()))
    self.do_message_headers(em, mlrow)
    self.do_part(em, fld, merrors, first_part=True)
    self.xc.terminal('Eol', eol)
    self.xc.Hash('SHA1', sha1_digest)
    self.xc.exdent()
    self.xc.prl('</Message>')
    mlrow.add_hash(sha1_digest)
    mlrow.add_errors(len(merrors))
    if len(merrors) > 0:
      mlrow.add_firstmessage(merrors[0])
    self.mlf.writerow(mlrow)

  #####################################################################
  def finish_output_file (self):
    xml_file = self.xc.get_fh()
    if xml_file:
      xml_file.close()
    self.xc.set_fh(None)
    self.mlog.close()
    self.mlog = None
    self.mlf  = None

  #####################################################################
  def new_output_file (self):
    sanitized_account_name = \
        re.sub('[/?<>\\\\:*|"^]', '_', self.account_name)
    sanitized_account_name = re.sub('[^ -~]', '_', sanitized_account_name)
    xml_file = ''
    if self.output_chunksize > 0:
      if not self.increment:
        self.increment = 'aa'
        self.output_file_count = 1
      else:
        self.output_file_count = self.output_file_count + 1
        p = self.increment[0]
        q = self.increment[1]
        if q == 'z':
          if p == 'z':
            print "maximum number of output files reached; quitting"
            sys.exit(0)
          else:
            p = chr(ord(p) + 1)
            q = 'a'
        else:
          q = chr(ord(q) + 1)
        self.increment = p + q
      xml_file = os.path.join(self.account_directory,
        (self.folder_name if self.folder_name else sanitized_account_name) +
        '.' + self.increment + '.xml')
      mlfn = os.path.join(self.account_directory, MLOG_NAME + \
        '.' + self.increment + '.csv')
    else:
      xml_file = os.path.join(self.account_directory,
        (self.folder_name if self.folder_name else sanitized_account_name) + \
        '.xml')
      mlfn = os.path.join(self.account_directory, MLOG_NAME + '.csv')
    fh = open(xml_file, 'wb')
    os.chmod(xml_file, dmd.XML_FILE_PERMISSIONS)
    self.output_files.append(xml_file)
    self.xc.set_fh(fh)
    self.mlog = open(mlfn, 'wb')
    self.mlf = message_log.MessageLog(self.mlog)
    
  ######################################################################
  def do_mbox_folder (self, fld):
    self.xc.folder_head(fld.folder_name)
    mb = mailbox.mbox(fld.mbox_path, create=False)
    for i in range(len(mb)):
      self.total_mbox_messages = self.total_mbox_messages + 1
      mes = mb.get_message(i)
      mes_string = mes.as_string()
      (eol, sha1_digest) = message_hash(mes_string)
      em = email.message_from_string(mes_string)
      glid = em['Message-ID']
      if glid and self.glidr.has_message(glid):
        self.skipped_duplicates = self.skipped_duplicates + 1
        self.warning('skipping duplicate message: ' + glid + \
        ' in folder ' + fld.folder_name)
        continue
      else:
        self.glidr.add_message(glid)
      self.total_msg_count = self.total_msg_count + 1
      self.message_count = self.message_count + 1
      if self.output_chunksize > 0 and self.message_count > self.output_chunksize:
        self.xc.finish_folder(fld.folder_name, eol_chars)
        self.xc.finish_account()
        self.finish_output_file()
        self.new_output_file()
        self.xc.xml_header()
        self.xc.account_head(self.account_name)
        self.xc.folder_head(fld.folder_name)
        self.message_count = 1
#      try:
      self.do_message(em, eol, sha1_digest, fld)
#      except Exception as e:
#        print str(e)
#        self.warning(str(e))
      if em.defects:
        for d in em.defects:
          self.warning('msg ' + str(i) + ', defect: ' + d)
      if self.progress_dialog and self.total_msg_count % 100 == 0:
        if self.total_msg_count < self.estimated_total_messages - 100:
#          pass
# updating by estimation often ends badly
# ... flow control in the dialog creator can get messed up
          self.progress_dialog.Update(self.total_msg_count)
    self.xc.finish_folder(fld.folder_name, eol_chars)
    mb.close()

  ######################################################################
  def walk_account_tree (self, relative_path, path):
    files = os.listdir(path)
    for f in files:
      if os.path.isdir(os.path.join(path, f)):
        self.walk_account_tree(os.path.join(relative_path, f), os.path.join(path, f))
      elif re.match('.+\.mbox$', f):
        folder_name = re.sub('\.mbox$', '', f)
        mbox_path = os.path.join(path, f)
        if not check_file_for_reading(mbox_path):
          sys.exit(0)
        fld = FolderInfo(mbox_path=mbox_path,
          folder_path=path,
          relative_path=relative_path,
          folder_name=folder_name)
        self.do_mbox_folder(fld)
      elif re.match('mbox', f):
          ##  Jeremy M. Gibson (State Archives of North Carolina)
          ##  2016-16-06 added this section for readpst compatibility
          print("Processing: " + path)
          head, tail = os.path.split(path)
          folder_name = tail
          mbox_path = os.path.join(path, f)
          fld = FolderInfo(mbox_path=mbox_path,
                           folder_path=path,
                           relative_path=relative_path,
                           folder_name=folder_name)
          self.do_mbox_folder(fld)

  ######################################################################
  def walk_folder (self, mbox_path):
    relative_path = os.path.join('.',
        os.path.relpath(mbox_path, self.account_directory))
    if not check_file_for_reading(mbox_path):
      sys.exit(0)
    fld = FolderInfo(mbox_path=mbox_path,
      folder_path=os.path.dirname(mbox_path),
      relative_path=relative_path,
      folder_name=self.folder_name)
    self.do_mbox_folder(fld)

######################################################################
def main ():
  pass

######################################################################
if __name__ == "__main__":
  main()
