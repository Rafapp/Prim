try:
    from shiboken2 import wrapInstance # Convert C++ pointers to python
    from PySide2 import QtCore # Core classes and functions
    from PySide2 import QtWidgets
    from PySide2 import QtGui
except ImportError:
    from shiboken6 import wrapInstance 
    from PySide6 import QtWidgets
    from PySide6 import QtCore
    from PySide6 import QtGui

import maya.api.OpenMaya as om
import maya.OpenMayaUI as omui
import maya.cmds as cmds
import maya.mel as mel
import importlib
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

        # Text field/buttons
        self.primitive_label = QtWidgets.QLabel("New primitive name")
        self.primitive_name = QtWidgets.QLineEdit()
        self.saveprimitive_button = QtWidgets.QPushButton("Save primitive")

        # Primitive gallery labels
        self.test_label = QtWidgets.QLabel("testlabel\n\n\n\n\n")
        self.test_label1 = QtWidgets.QLabel("testlabel\n\n\n\n\n")
        self.test_label2 = QtWidgets.QLabel("testlabel\n\n\n\n\n")
        self.test_label3 = QtWidgets.QLabel("testlabel\n\n\n\n\n")
        self.test_label4 = QtWidgets.QLabel("testlabel\n\n\n\n\n")

        # Scroll area setup
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setBackgroundRole(QtGui.QPalette.ColorRole.Dark)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

    def createLayouts(self):
        main_layout = QtWidgets.QVBoxLayout(self.central_widget)
        main_layout.addWidget(self.primitive_label)
        main_layout.addWidget(self.primitive_name)
        main_layout.addWidget(self.saveprimitive_button)
        main_layout.addWidget(self.scroll_area)

        gallery_widget = QtWidgets.QWidget()  # Widget to contain the gallery layout
        gallery_layout = QtWidgets.QVBoxLayout(gallery_widget)
        gallery_layout.addWidget(self.test_label)
        gallery_layout.addWidget(self.test_label1)
        gallery_layout.addWidget(self.test_label2)
        gallery_layout.addWidget(self.test_label3)
        gallery_layout.addWidget(self.test_label4)

        self.scroll_area.setWidget(gallery_widget)  # Set the gallery widget as the scroll area's widget


    def createConnections(self):
        self.saveprimitive_button.clicked.connect(self.savePrimitive)

    def savePrimitive(self):
        name = self.primitive_name.text()
        print("Primitive saved ...")

# We are using Maya Python API 2.0
def maya_useNewAPI():
    pass

def addPrimToShelf():
    command = 'from Prim import mainWindow;mainWindow.showWindow()'
    current_shelf = mel.eval('tabLayout -q -selectTab $gShelfTopLevel')

    if cmds.shelfButton('primButton', exists=True):
        return
    #TODO: Make the installer install the icon in the proper place.
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

def uninitializePlugin(plugin):
    global win
    if win is not None:
        win.close()
        win = None
