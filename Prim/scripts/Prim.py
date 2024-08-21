try:
    from shiboken2 import wrapInstance # Convert C++ pointers to python
    from PySide2 import QtCore 
    from PySide2 import QtWidgets
    from PySide2 import QtGui
except ImportError:
    from shiboken6 import wrapInstance 
    from PySide6 import QtWidgets
    from PySide6 import QtCore
    from PySide6 import QtGui

from MeshManager import instanceMesh, savePrimitiveData, deletePrimitiveData, generateMeshesFromPrimFile, renderMeshPreview
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
import maya.OpenMayaUI as omui
import maya.cmds as cmds # TODO: CMDS should go on separate file
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

def show_decision_dialog(prompt):
    result = cmds.confirmDialog(
        title='Warning',
        message=prompt,
        button=['Yes', 'No'],
        defaultButton='Yes',
        cancelButton='No',
        dismissString='No')

    if result == 'Yes':
        return True
    else:
        return False

def clear_layout(layout):
  while layout.count():
    child = layout.takeAt(0)
    if child.widget():
      child.widget().setParent(None)

def mayaWindow():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

def show_error_dialog(prompt):
    cmds.confirmDialog(
        title='Error',
        message=prompt,
        button='Ok',
        dismissString='Ok'
    )

"""
Widget that shows a primitive in the UI. Contains:
- primitive name
- primitive thumbnail
- create button
- delete button
"""
class primitiveWidget(QtWidgets.QWidget):
    # Constructor: PrimitiveWidget("path")
    def __init__(self, name):
        super().__init__()

        self.name = name

        # Get thumbnail, set to default if not found 
        self.thumbnail_path = self.getThumbnail()

        # Creation functions
        self.createWidgets()
        self.createLayouts()
        self.createConnections()

        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)

    def getThumbnail(self):
        dir_path = os.path.dirname(os.path.realpath(__file__)) + "/../primitives/thumbnails"
        files = cmds.getFileList(folder = dir_path)

        if not files: 
            print("Error: Thumbnails folder is empty") 
            return

        png_files = [f for f in files if f.endswith('.png')]
        if not png_files: 
            print("Error: No .png files found in thumbnails folder") 
            return

        image_path = None
        for item in png_files:
            full_name = os.path.join(dir_path, item)
            file_name, ext = os.path.splitext(os.path.basename(full_name))
            if file_name == self.name:
                print(f"Found thumbnail for primitive: {self.name}")
                image_path = full_name
                break

        if not image_path:
            print(f"Error: Could not find thumbnail for primitive \"{self.name}\", setting to default ...")
            image_path = os.path.dirname(os.path.realpath(__file__)) + "/../primitives/thumbnails/default.png"

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
        confirm = show_decision_dialog("Are you sure you wish to delete this primitive?\n\nThis action is irreversible!")
        if confirm == False: return

        deletePrimitiveData(self.name)
        if self.name in mainWindow.window_instance.primitive_widgets:
            del mainWindow.window_instance.primitive_widgets[self.name]
        mainWindow.window_instance.refreshPrimitiveWidgets()

"""
Main plugin window. Is child of maya's main window.
"""
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

        # Creation functions
        self.createMenus()
        self.createWidgets()
        self.createLayouts()
        self.createConnections()

    def createMenus(self):
        menu_bar = self.menuBar()

        # "File" menu
        self.file_menu = menu_bar.addMenu("File")
        self.new_action = QtGui.QAction("New primtive library", self)
        self.open_action = QtGui.QAction("Open primitive library", self)
        self.export_action = QtGui.QAction("Export current library", self)
        self.file_menu.addAction(self.new_action)
        self.file_menu.addAction(self.open_action)
        self.file_menu.addAction(self.export_action)
        self.new_action.triggered.connect(self.newPrimitiveLibrary)
        self.open_action.triggered.connect(self.openPrimitiveLibrary)
        self.export_action.triggered.connect(self.exportPrimitiveFile)

        # "Prim" menu
        self.prim_menu = menu_bar.addMenu("Prim")
        self.refresh_action = QtGui.QAction("Refresh primitives", self)
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

        self.gallery_widget = QtWidgets.QWidget()  # Widget to contain the gallery layout
        self.gallery_layout = QtWidgets.QVBoxLayout(self.gallery_widget)

        self.gallery_layout.addStretch()
        self.scroll_area.setWidget(self.gallery_widget)  # Set the gallery widget as the scroll area's widget

    def createConnections(self):
        self.saveprimitive_button.clicked.connect(self.savePrimitive)

    # Updates current .prim file label
    def updateCurrentFile(self, file_path): 
        global current_prim_file_path 
        current_prim_file_path = file_path

        file_name = os.path.basename(file_path).split('.')
        title = file_name[0]
        if len(title) > 15:
            title = title[0:15] + "..."

        self.current_file_label.setText("Current library: " + title)
        print(f"Current prim file updated to: {file_path}")

    # User creates new primitive library file
    def newPrimitiveLibrary(self):
        user_file_name = None

        # Give prompt with naming
        prompt = cmds.promptDialog(title="New",
                                   message="Create new primitive library:",
                                   messageAlign="center",
                                   button=["Create", "Cancel"],
                                   defaultButton="Create",
                                   cancelButton="Cancel")

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

        # Clear widgets
        self.primitive_widgets = {}
        self.refreshPrimitiveWidgets()

    # Imports a primitive library
    def openPrimitiveLibrary(self):

        # Open file, and update current file data
        libraries_path = os.path.dirname(os.path.realpath(__file__)) + "/../primitives/libraries"
        path = cmds.fileDialog2(startingDirectory=libraries_path, fileFilter="Primitive Library(*.prim)", fileMode=1, dialogStyle=2)
        if path[0]: self.updateCurrentFile(path[0])
        print(f"Opened primitive library: {current_prim_file_path}")

        # Delete all .obj meshes 
        meshes_path = os.path.dirname(os.path.realpath(__file__)) + "/../primitives/meshes/"
        files = cmds.getFileList(folder = meshes_path)
        if files: 
            obj_files = [f for f in files if f.endswith('.obj')]
            if obj_files: 
                for f in obj_files:
                    os.remove(meshes_path + f)

        #TODO: This deletes all images, but assumes they are regenerated on batch.
        # Delete all thumbnails (excluding the default.png)
#        thumbnails_path = os.path.dirname(os.path.realpath(__file__)) + "/../primitives/thumbnails/"
#        files = cmds.getFileList(folder = thumbnails_path)
#       if files: 
#           png_files = [f for f in files if f.endswith('.png')]
#           if png_files: 
#               for f in png_files:
#                   if f == "default.png": continue
#                   os.remove(thumbnails_path + f)

        # Generate .obj meshes from prim file 
        generateMeshesFromPrimFile()

        # Update primitive UI using .obj meshes
        self.primitive_widgets = {}
        files = cmds.getFileList(folder = meshes_path)
        if files: 
            obj_files = [f for f in files if f.endswith('.obj')]
            if obj_files: 
                for f in obj_files:
                    self.addPrimitiveWidget(f.split(".")[0])
        self.refreshPrimitiveWidgets()

    def exportPrimitiveFile(self):
        if current_prim_file_path == None:
            show_confirmation_dialog("Please open a primitive library first")
            return

        def copyAndRename(src_path, dest_path, new_name):
            shutil.copy(src_path, dest_path + "/" + new_name)

        path = cmds.fileDialog2(fileMode=0, caption="Save As", fileFilter="Primitive Library(*.prim)") 
        file_name = os.path.basename(path[0])
        dest_dir = os.path.dirname(path[0])
        copyAndRename(current_prim_file_path, dest_dir, file_name)

    # Create a widget object, add to dictionary
    def addPrimitiveWidget(self, name):
        widget = primitiveWidget(name)
        self.primitive_widgets[name] = widget

    # Refresh the UI with any primitive changes in the dictionary
    def refreshPrimitiveWidgets(self):
        clear_layout(self.gallery_layout)

        for name, widget in self.primitive_widgets.items():
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

    #TODO: Check for file integrity here to avoid repetition in MeshManager
    def savePrimitive(self):
        if not current_prim_file_path:
            show_error_dialog("Open a primitive library (.prim) file first")
            return

        name = self.primitive_name.text()
        savePrimitiveData(name)
        renderMeshPreview(name)
        self.addPrimitiveWidget(name)
        self.refreshPrimitiveWidgets()
