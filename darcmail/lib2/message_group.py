#!/usr/bin/env python
######################################################################
## $Revision: 1.1 $
## $Date: 2016/02/11 23:38:42 $
## Author: Carl Schaefer, Smithsonian Institution Archives 
######################################################################

import db_access as dba

message_groups = {}

######################################################################
def message_group_for_account (account_id):
  global message_groups
  if account_id not in message_groups.keys():
    message_groups[account_id] = set()
  return message_groups[account_id]
