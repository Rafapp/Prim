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

from MeshManager import instanceMesh, savePrimitiveData, deletePrimitiveData
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
import maya.OpenMayaUI as omui
import maya.cmds as cmds
import maya.mel as mel
import subprocess
import shutil
import sys
import os

# Global variable for the file being dynamically edited by prim
current_prim_file_path = None

def get_current_prim_file_path():
    global current_prim_file_path
    return current_prim_file_path

def clear_layout(layout):
    if not layout: return
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()
        else:
            clear_layout(item.layout())

def mayaWindow():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

# Helper function, creates error dialogue
def show_error_dialog(prompt):
    cmds.confirmDialog(
        title='Error',
        message=prompt,
        button='Ok',
        dismissString='Ok'
    )

class primitiveWidget(QtWidgets.QWidget):
    # Constructor: PrimitiveWidget("path")
    def __init__(self, name):
        super().__init__()

        self.name = name

        # Get thumbnail, set to default if not found 
        thumbnail_path = self.getThumbnail()
        if not thumbnail_path: thumbnail_path = os.path.dirname(os.path.realpath(__file__)) + "/../primitives/thumbnails/default.png"
        self.thumbnail_path = thumbnail_path

        # Creation functions
        self.createWidgets()
        self.createLayouts()
        self.createConnections()

        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)

    def getThumbnail(self):
        # Check for files in /thumbnails
        dir_path = os.path.dirname(os.path.realpath(__file__)) + "/../primitives/thumbnails"
        files = cmds.getFileList(folder = dir_path)

        if not files: 
            print("Error: Thumbnails folder is empty") 
            return

        # Check for .png files in /thumbnails
        png_files = [f for f in files if f.endswith('.png')]
        if not png_files: 
            print("Error: No .png files found in thumbnails folder") 
            return

        image_path = None
        for item in png_files:
            full_name = os.path.join(dir_path, item)
            file_name, ext = os.path.splitext(os.path.basename(full_name))
            if file_name == self.name:
                image_path = full_name
                break

        # Check if mesh with that specific name was found.
        if not image_path:
            print(f"Error: Could not find thumbnail for primitive \"{self.name}\"")
            return

        return image_path
     
    def createWidgets(self):
        # Labels
        self.name_label = QtWidgets.QLabel(self.name)
        self.image_label = QtWidgets.QLabel()
        self.image_label.setPixmap(QtGui.QPixmap(self.thumbnail_path))

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
        instanceMesh(self.name)

    def deletePrimitive(self):
        deletePrimitiveData(self.name)
        pass

class mainWindow(MayaQWidgetDockableMixin, QtWidgets.QMainWindow):
    window_instance = None
    primitive_widgets = {} 

    # Highlight the window if already opened
    @classmethod
    def showWindow(cls):
        if not cls.window_instance:
            cls.window_instance = mainWindow()  # Make sure to set the class variable
        
        if cls.window_instance.isHidden():
            cls.window_instance.show(dockable=True)
        else:
            cls.window_instance.raise_()
            cls.window_instance.activateWindow() 

    def __init__(self, parent=mayaWindow()):
        super().__init__(parent)
        self.setWindowTitle("Prim")
        self.setMinimumHeight(250)
        self.setMinimumWidth(200)
        
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
        self.refresh_action.triggered.connect(self.refreshPrimitiveWidgets)
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
        self.gallery_layout = QtWidgets.QVBoxLayout(gallery_widget)

        self.gallery_layout.addStretch()
        self.scroll_area.setWidget(gallery_widget)  # Set the gallery widget as the scroll area's widget

    def createConnections(self):
        self.saveprimitive_button.clicked.connect(self.savePrimitive)

    # Connection functions
    def updateCurrentFile(self, file_path): 
        # Update current file path data
        global current_prim_file_path 
        current_prim_file_path = file_path

        # Update current file label at top of window
        file_name = os.path.basename(file_path).split('.')
        title = file_name[0]
        if len(title) > 15:
            title = title[0:15] + "..."

        self.current_file_label.setText("Current library: " + title)
        print(f"Current prim file updated to: {file_path}")

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
                    # TODO Create a confirm dialog function, no reason to repeat this ...
                    if file_name == user_file_name:
                        show_confirmation_dialog("A local primitive already has this name, try another name.")
                        return

        if not user_file_name:
            show_confirmation_dialog("Please enter a non-empty name")
            return

        full_filename = user_file_name + ".prim" 

        # TODO This breaks with spaces in file name
        open(os.path.join(dir_path, full_filename), 'w')
        print("New prim library file with name: \"" + user_file_name + "\" created")

        # Update current file
        self.updateCurrentFile(os.path.join(dir_path, full_filename))

    def openPrimitiveFile(self):
        # Open file, and update current file data
        dir_path = os.path.dirname(os.path.realpath(__file__)) + "/../primitives/libraries"
        path = cmds.fileDialog2(startingDirectory=dir_path, fileFilter="Primitive Library(*.prim)", fileMode=1, dialogStyle=2)

        self.updateCurrentFile(path[0])
        print(f"Opened primitive library: {current_prim_file_path}")

    def exportPrimitiveFile(self):
        if current_prim_file_path == None:
            show_confirmation_dialog("Please open a primitive library first")
            return

        def copyAndRename(src_path, dest_path, new_name):
            print(f"copy from src: {src_path} to: {dest_path}")
            shutil.copy(src_path, dest_path + "/" + new_name)

        path = cmds.fileDialog2(fileMode=0, caption="Save As", fileFilter="Primitive Library(*.prim)") 
        file_name = os.path.basename(path[0])
        dest_dir = os.path.dirname(path[0])
        copyAndRename(current_prim_file_path, dest_dir, file_name)

    # Create a widget object, add to dictionary
    def addPrimitiveWidget(self, name):
        widget = primitiveWidget(name)
        self.primitive_widgets[name] = widget
        pass

    # Refresh the UI with any new primitives in the dictionary
    def refreshPrimitiveWidgets(self):
        clear_layout(self.gallery_layout)
        # Read the prim file, and get the name of the primitives, create widgets for them
        for widget in self.primitive_widgets.values():
            self.gallery_layout.addWidget(widget)
        self.gallery_layout.addStretch()

    def redirectHelp(self):
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
        if not current_prim_file_path:
            show_error_dialog("Open a primitive library (.prim) file first")
            return

        name = self.primitive_name.text()
        self.addPrimitiveWidget(name)
        savePrimitiveData(name)
