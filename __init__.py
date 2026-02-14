# -*- coding: utf-8 -*-
from importlib import reload
import traceback

import maya.cmds as cmds
import maya.mel as mel

# default settings
def default_settings():
    cmds.selectPref(tso=True)

try:
    default_settings()
except:
    print(traceback.format_exc())