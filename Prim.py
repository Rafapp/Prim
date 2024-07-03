try:
    from PySide2 import QtWidgets # UI components 
    from PySide2 import QtCore # Core classes and functions
    from shiboken2 import wrapInstance # Convert C++ pointers to python
except ImportError:
    from PySide6 import QtCore
    from PySide6 import QtWidgets
    from shiboken6 import wrapInstance 

import maya.api.OpenMaya as om
import maya.cmds as cmds
import maya.OpenMayaUI as omui

win = None

def maya_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

class MainWindow(QtWidgets.QDialog):
    def __init__(self, parent=maya_window()):
        super().__init__(parent)
        self.setWindowTitle("Prim")
        self.setMinimumSize(300, 400)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Tool)

# We are using Maya Python API 2.0
def maya_useNewAPI():
    pass

def initializePlugin(plugin):
    global win
    vendor = "Rafael Padilla Perez"
    version = "1.0.0"
    om.MFnPlugin(plugin, vendor, version)

    # Create and show the Qt window
    win = MainWindow()
    win.show()

def uninitializePlugin(plugin):
    global win
    if win is not None:
        win.close()
        win = None
