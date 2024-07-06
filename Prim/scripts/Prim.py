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
        self.setFixedWidth(150)
        
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
        self.test_label = QtWidgets.QLabel()
        self.test_label1 = QtWidgets.QLabel()
        self.test_label2 = QtWidgets.QLabel()
        self.test_label3 = QtWidgets.QLabel()
        self.test_label4 = QtWidgets.QLabel()

        path = "/Users/rafa/Documents/Dev/Prim/Prim/icons/test_primitive.png"
        self.test_label.setPixmap(QtGui.QPixmap(path))
        self.test_label1.setPixmap(QtGui.QPixmap(path))
        self.test_label2.setPixmap(QtGui.QPixmap(path))
        self.test_label3.setPixmap(QtGui.QPixmap(path))
        self.test_label4.setPixmap(QtGui.QPixmap(path))
        
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
