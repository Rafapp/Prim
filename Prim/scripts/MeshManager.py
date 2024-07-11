# TODO Functionality:
# - Check for corrupt data (e.g. file name changed) and prompt user

#TODO Data:
# - Current .prim file being used
# - Absolute path to module folder

import maya.api.OpenMaya as om
import maya.cmds as cmds
import maya.mel as mel
import sys
import os

# We are using Maya Python API 2.0
def maya_useNewAPI():
    pass

# Helper function, creates a confirmation dialogue
def show_warning_dialog(prompt):
    result = cmds.confirmDialog(
        title='Warning',
        message=prompt,
        button=['Yes', 'No'],
        defaultButton='Yes',
        cancelButton='No',
        dismissString='No'
    )

    if result == 'Yes':
        return True
    else:
        return False

def updateLibrary():
    pass

# Renders a 3/4, lambertian, black and white preview of the primitive. Stores as .png image.
def renderMeshPreview(name):
    # Check if corresponding .obj file exists
    # Render the mesh
    pass

# Creates (instances) mesh to the current MAYA scene.
def createMesh(mesh_name):
    # Navigate to meshes folder in module 
    dir_path = os.path.dirname(os.path.realpath(__file__)) + "/../primitives/meshes"
    
    # Check for files in /meshes
    files = cmds.getFileList(folder = dir_path)
    if not files: 
        print("Error: Meshes folder is empty") 
        return

    # Check for .obj files in /meshes
    obj_files = [f for f in files if f.endswith('.obj')]
    if not obj_files: 
        print("Error: No .obj files found in meshes folder") 
        return

    mesh_path = None
    for item in obj_files:
        full_name = os.path.join(dir_path, item)
        file_name, ext = os.path.splitext(os.path.basename(full_name))
        if file_name == mesh_name:
            mesh_path = full_name
            break

    # Check if mesh with that specific name was found.
    if not mesh_path:
        print("Error: Could not find mesh for primitive \"" + mesh_name + "\"")
        return
 
    # Import the primitive to the scene. 
    mesh = cmds.file(mesh_path, i = True, rnn=True)
    transforms = cmds.ls(mesh, type='transform')

    # Rename the newly created mesh. 
    for i, object in enumerate(transforms):
        name = '%s_%s' % (mesh_name, str(i+1).zfill(3))
        cmds.rename(object, name)

    print("Succesfully created primitive: " + "\"" + mesh_name + "\"")

# Saves selected mesh in the scene to the .prim file, and updates library.
def savePrimitive(name, data):
    updateLibrary()
    pass

# Deletes mesh from .prim file, its .obj mesh, and its preview.
def deletePrimitive(mesh_name):
    confirm = show_warning_dialog("Are you sure you wish to delete this primitive?\n\nThis action is irreversible!")
    if confirm == False: return

    # Navigate to meshes folder in module 
    dir_path = os.path.dirname(os.path.realpath(__file__)) + "/../primitives/meshes"
    
    # Check for files in /meshes
    files = cmds.getFileList(folder = dir_path)
    if not files: 
        print("Error: Meshes folder is empty") 
        return

    # Check for .obj files in /meshes
    obj_files = [f for f in files if f.endswith('.obj')]
    if not obj_files: 
        print("Error: No .obj files found in meshes folder") 
        return

    mesh_path = None
    for item in obj_files:
        full_name = os.path.join(dir_path, item)
        file_name, ext = os.path.splitext(os.path.basename(full_name))
        if file_name == mesh_name:
            mesh_path = full_name
            break

    # Check if mesh with that specific name was found.
    if not mesh_path:
        print("Error: Could not find mesh for primitive \"" + mesh_name + "\"")
        return

    # Delete the mesh's .obj file
    os.remove(mesh_path)

    # Update the .prim file
 
    print("Succesfully deleted primitive: " + "\"" + mesh_name + "\"")
