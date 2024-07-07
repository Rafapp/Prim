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

import maya.OpenMayaUI as omui
import maya.mel as mel
import sys

def mayaWindow():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

class primitiveWidget(QtWidgets.QWidget):
    # Constructor: PrimitiveWidget("path")
    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path

        self.createWidgets()
        self.createLayouts()
        self.createConnections()

        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)

    def createWidgets(self):
        # Labels
        self.name_label = QtWidgets.QLabel("Primitive name")
        self.image_label = QtWidgets.QLabel()
        self.image_label.setPixmap(QtGui.QPixmap(self.image_path))

        self.name_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.image_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        # Buttons
        self.create_button = QtWidgets.QPushButton("Create")
        self.delete_button = QtWidgets.QPushButton("Delete")

    def createLayouts(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        button_layout = QtWidgets.QHBoxLayout()

        main_layout.addWidget(self.name_label)
        main_layout.addWidget(self.image_label)

        button_layout.addStretch()
        button_layout.addWidget(self.create_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()

        main_layout.addLayout(button_layout)

    def createConnections(self):
        self.create_button.clicked.connect(self.createPrimitive)
        self.delete_button.clicked.connect(self.deletePrimitive)

    def createPrimitive(self):
        print("created primitive")

    def deletePrimitive(self):
        print("deleted primitive")

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
        self.setMinimumHeight(250)
        self.setFixedWidth(200)
        
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
        
        # Scroll area setup
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setBackgroundRole(QtGui.QPalette.ColorRole.Dark)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def createLayouts(self):
        main_layout = QtWidgets.QVBoxLayout(self.central_widget)
        main_layout.addWidget(self.primitive_label)
        main_layout.addWidget(self.primitive_name)
        main_layout.addWidget(self.saveprimitive_button)
        main_layout.addWidget(self.scroll_area)

        gallery_widget = QtWidgets.QWidget()  # Widget to contain the gallery layout
        gallery_layout = QtWidgets.QVBoxLayout(gallery_widget) # TODO Add primitive custom widgets here 

        # TODO add primitives dynamically
        self.test_primitive = primitiveWidget("/Users/rafa/Documents/Dev/Prim/Prim/icons/test_primitive.png")
        self.test_primitive2 = primitiveWidget("/Users/rafa/Documents/Dev/Prim/Prim/icons/test_primitive.png")
        gallery_layout.addWidget(self.test_primitive)
        gallery_layout.addWidget(self.test_primitive2)

        gallery_layout.addStretch()
        self.scroll_area.setWidget(gallery_widget)  # Set the gallery widget as the scroll area's widget

    def createConnections(self):
        self.saveprimitive_button.clicked.connect(self.savePrimitive)

    def savePrimitive(self):
        name = self.primitive_name.text()
        print("Primitive saved ...")

# We are using Maya Python API 2.0
def maya_useNewAPI():
    pass
