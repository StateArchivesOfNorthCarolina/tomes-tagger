#!/usr/bin/env python
######################################################################
# $Revision: 1.1 $
# $Date: 2015/07/15 12:24:41 $
# Author: Carl Schaefer, Smithsonian Institution Archives
######################################################################

import sys
import os
import wx
from lib2 import dm_frame
import dm_defaults as dmd

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                             'lib'))

######################################################################
class DArcMail(wx.App):
  def OnInit(self):
    frame = dm_frame.DMFrame(None, 'DArcMail ' + dmd.VERSION)
    self.SetTopWindow(frame)
    frame.Show(True)
    return True

######################################################################
#app = DArcMail(redirect=True)
app = DArcMail(redirect=False)
app.MainLoop()

