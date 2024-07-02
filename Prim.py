try:
    from PySide2 import QtWidgets # UI components 
    from PySide2 import QtCore # Core classes and functions
    from shiboken2 import wrapInstance
except ImportError:
    from PySide6 import QtCore
    from PySide6 import QtWidgets
    from shiboken6 import wrapInstance

import maya.api.OpenMaya as om
import maya.cmds as cmds
import maya.OpenMayaUI as omui

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

class PrimWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(PrimWindow, self).__init__(parent)
        
        # Window UI
        self.setWindowTitle("Prim")
        self.name_line_edit = QtWidgets.QLineEdit()
        self.cube_btn = QtWidgets.QPushButton("Create Cube")
        self.sphere_btn = QtWidgets.QPushButton("Create Sphere")

        # Layout
        layout = QtWidgets.QVBoxLayout() # Vertical
        layout.addWidget(self.name_line_edit)
        layout.addWidget(self.cube_btn)
        layout.addWidget(self.sphere_btn)
        self.setLayout(layout)

        # Connect buttons to events
        self.cube_btn.clicked.connect(self.create_cube)
        self.sphere_btn.clicked.connect(self.create_sphere)

    def get_name(self):
        return(self.name_line_edit.text())

    def create_cube(self):
        cmds.polyCube(name=self.get_name())

    def create_sphere(self):
        cmds.polySphere(name=self.get_name())
        
# We are using Maya Python API 2.0
def maya_useNewAPI():
    pass

def initializePlugin(plugin):
    vendor = "Rafael Padilla Perez"
    version = "1.0.0"
    om.MFnPlugin(plugin, vendor, version)

    # Create and show the Qt window
    main_window = maya_main_window()
    win = PrimWindow(parent=main_window)
    win.show()

def uninitializePlugin(plugin):
    pass
