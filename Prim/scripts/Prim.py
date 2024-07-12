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

from MeshManager import updateLibrary, createMesh, savePrimitive, deletePrimitive
import maya.OpenMayaUI as omui
import maya.cmds as cmds
import maya.mel as mel
import subprocess
import sys

# Global variable for the file being dynamically edited by prim
current_prim_file_path = None

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
        createMesh("zebra")

    def deletePrimitive(self):
        deletePrimitive("cubecp")
        pass

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
        menu_bar = self.menuBar()

        # "File" menu
        self.file_menu = menu_bar.addMenu("File")
        self.new_action = QtGui.QAction("New", self)
        self.open_action = QtGui.QAction("Open", self)
        self.export_action = QtGui.QAction("Export", self)
        self.file_menu.addAction(self.new_action)
        self.file_menu.addAction(self.open_action)
        self.file_menu.addAction(self.export_action)
        self.new_action.triggered.connect(self.newPrimitiveFile)
        self.open_action.triggered.connect(self.openPrimitiveFile)
        self.export_action.triggered.connect(self.exportPrimitiveFile)

        # "Prim" menu
        self.prim_menu = menu_bar.addMenu("Prim")
        self.refresh_action = QtGui.QAction("Refresh", self)
        self.help_action = QtGui.QAction("Help", self)
        self.prim_menu.addAction(self.refresh_action)
        self.prim_menu.addAction(self.help_action)
        self.refresh_action.triggered.connect(self.refreshPrimitives)
        self.help_action.triggered.connect(self.redirectHelp)

    def createWidgets(self):
        # Central widget
        self.central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Label for current file being edited
        self.current_file_label = QtWidgets.QLabel("Current library: None")
        self.current_file_label.setStyleSheet("color:darkgrey")

        # Text field/buttons
        self.primitive_label = QtWidgets.QLabel("New primitive name")
        self.primitive_label.setStyleSheet("color:white")
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
        main_layout.addWidget(self.current_file_label)
        main_layout.addWidget(self.primitive_label)
        main_layout.addWidget(self.primitive_name)
        main_layout.addWidget(self.saveprimitive_button)
        main_layout.addWidget(self.scroll_area)

        gallery_widget = QtWidgets.QWidget()  # Widget to contain the gallery layout
        gallery_layout = QtWidgets.QVBoxLayout(gallery_widget) # TODO Add primitive custom widgets here 

        # TODO add primitives dynamically
        self.test_primitive = primitiveWidget("/Users/rafa/Documents/Dev/Prim/Prim/primitives/previews/test_primitive.png")
        self.test_primitive2 = primitiveWidget("/Users/rafa/Documents/Dev/Prim/Prim/primitives/previews/test_primitive.png")
        gallery_layout.addWidget(self.test_primitive)
        gallery_layout.addWidget(self.test_primitive2)

        gallery_layout.addStretch()
        self.scroll_area.setWidget(gallery_widget)  # Set the gallery widget as the scroll area's widget

    def createConnections(self):
        self.saveprimitive_button.clicked.connect(self.savePrimitive)

    # Connection functions
    def updateCurrentFileLabel(self, file_name):
        self.current_file_label.setText("Current library: " + file_name)

    def newPrimitiveFile(self):
        user_file_name = None

        # Give prompt with naming
        prompt = cmds.promptDialog(title="New"
                                      , message="Create new primitive library:"
                                      , messageAlign="center"
                                      , button=["Create", "Cancel"]
                                      , defaultButton="Create"
                                      , cancelButton="Cancel")
        if prompt != "Create": return
        user_file_name = cmds.promptDialog(query=True, text=True)
        dir_path = os.path.dirname(os.path.realpath(__file__)) + "/../primitives/libraries"

        # Check for files in /libraries
        files = cmds.getFileList(folder = dir_path)
        if files: 
            # Check for .prim files in /libraries
            prim_files = [f for f in files if f.endswith('.prim')]
            if prim_files: 
                for item in prim_files:
                    full_name = os.path.join(dir_path, item)
                    file_name, ext = os.path.splitext(os.path.basename(full_name))
                    if file_name == user_file_name:
                        cmds.confirmDialog(
                            title='Error',
                            message='A local primitive library already has this name, try again with a different name',
                            button='Ok',
                            dismissString='Ok'
                        )
                        return

        if not user_file_name:
            cmds.confirmDialog(
                title='Error',
                message='Please enter a non-empty name',
                button='Ok',
                dismissString='Ok'
            )
            return

        full_filename = user_file_name + ".prim" 
        open(os.path.join(dir_path, full_filename), 'w')
        print("New prim file with name: \"" + user_file_name + "\" created")
        # TODO This breaks with spaces in file name
        current_prim_file_path = dir_path + "/" + full_filename


    def openPrimitiveFile(self):
        dir_path = os.path.dirname(os.path.realpath(__file__)) + "/../primitives/libraries"
        path = cmds.fileDialog2(startingDirectory=dir_path, fileFilter="Primitive Library(*.prim)", fileMode=1, dialogStyle=2)
        print(f"Opened primitive library: {path}")
        file_name = os.path.basename(path[0])
        self.updateCurrentFileLabel(file_name)
        updateLibrary()
        pass

    def exportPrimitiveFile(self):
        print("export prim file")
        name = cmds.fileDialog2(fileMode=0, caption="Save As")
        pass

    def refreshPrimitives(self):
        print("refresh primitives")
        pass

    def redirectHelp(self):
        print("export prim file")
        url = "https://github.com/Rafapp/Prim"
        if sys.platform=='win32':
            os.startfile(url)
        elif sys.platform=='darwin':
            subprocess.Popen(['open', url])
        else:
            try:
                subprocess.Popen(['xdg-open', url])
            except OSError:
                print('Please open the link on your browser: ' + url)

    def savePrimitive(self):
        name = self.primitive_name.text()
        print(f"Primitive \"{name}\" saved ...")

# We are using Maya Python API 2.0
