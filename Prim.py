try:
    from shiboken2 import wrapInstance # Convert C++ pointers to python
    from PySide2 import QtCore # Core classes and functions
    from PySide2 import QtWidgets # UI components 
except ImportError:
    from shiboken6 import wrapInstance 
    from PySide6 import QtWidgets
    from PySide6 import QtCore

import maya.api.OpenMaya as om
import maya.OpenMayaUI as omui
import maya.cmds as cmds
import maya.mel as mel
import sys
import os

win = None

def mayaWindow():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

class mainWindow(QtWidgets.QMainWindow):

    window_instance = None

    # Highlight the window if already opened
    @classmethod
    def showWindow(cls):
        if not cls.window_instance:
            cls.window_instance = mainWindow()  # Make sure to set the class variable
            print("Created instance!")
        else:
            print("Instance already exists.")
            
        print(f"window_instance: {cls.window_instance}")
        
        if cls.window_instance.isHidden():
            cls.window_instance.show()
        else:
            cls.window_instance.raise_()
            cls.window_instance.activateWindow() 

    def __init__(self, parent=mayaWindow()):
        super().__init__(parent)
        self.setWindowTitle("Prim")
        self.setMinimumSize(150, 200)
        
        # MacOS support
        if sys.platform=="darwin":
            self.setWindowFlag(QtCore.Qt.Tool, True)

        self.createMenus()
        self.createWidgets()
        self.createLayouts()
        self.createConnections()

    def createMenus(self):
        self.menuBar().addMenu("File")
        self.menuBar().addMenu("Edit")

    def createWidgets(self):
        # Central widget
        self.central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.primitive_label = QtWidgets.QLabel("New primitive name")
        self.primitive_name = QtWidgets.QLineEdit()
        self.create = QtWidgets.QPushButton("Save primitive")
 
    def createLayouts(self):
        # TODO: QtWidgets.QGridLayout(self) for 3D primitive preview
        # On every new widget we do addwidget(widget, row, column)
        layout = QtWidgets.QVBoxLayout(self.central_widget)
        layout.addWidget(self.primitive_label)
        layout.addWidget(self.primitive_name)
        layout.addWidget(self.create)
        layout.addStretch()

    def createConnections(self):
        self.create.clicked.connect(self.savePrimitive)

    def savePrimitive(self):
        name = self.primitive_name.text()
        print("Primitive saved ...")

# We are using Maya Python API 2.0
def maya_useNewAPI():
    pass

def addPrimToShelf():
    command = 'mainWindow.showWindow()'
    current_shelf = mel.eval('tabLayout -q -selectTab $gShelfTopLevel')

    if cmds.shelfButton('primButton', exists=True):
        return

    cmds.shelfButton(
        'primButton',
        parent=current_shelf,
        label='Prim',
        command=command,
        image='prim_icon.png',
        sourceType='python'
    )

def initializePlugin(plugin):
    global win

    # Make sure there's a single window
    if win is not None: 
        win.close()
        win.deleteLater()
        win = None

    vendor = "Rafael Padilla Perez"
    version = "1.0.0"
    om.MFnPlugin(plugin, vendor, version)

    # Add to shelf, and start up
    addPrimToShelf()
    win = mainWindow()
    win.show()

def uninitializePlugin(plugin):
    global win
    if win is not None:
        win.close()
        win = None
