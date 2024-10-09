import sys
from maya.OpenMayaUI import MQtUtil
from shiboken2       import wrapInstance

from PySide2 import QtWidgets
from PySide2 import QtGui
from PySide2 import QtCore

def getMayaMainWindow() -> QtWidgets.QMainWindow:
    if sys.version_info.major >= 3:
        return wrapInstance(int(MQtUtil.mainWindow()), QtWidgets.QMainWindow)
    return wrapInstance(long(MQtUtil.mainWindow()), QtWidgets.QWidget)
    
