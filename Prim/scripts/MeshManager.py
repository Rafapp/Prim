# TODO Functionality:
# - Check for corrupt data (e.g. file name changed) and prompt user

#TODO Data:
# - Current .prim file being used
# - Absolute path to module folder

import maya.api.OpenMaya as om
import maya.cmds as cmds
import maya.mel as mel
import sys

# We are using Maya Python API 2.0
def maya_useNewAPI():
    pass

def updateLibrary():
    pass

# Renders a 3/4, lambertian, black and white preview of the primitive. Stores as .png image.
def renderMeshPreview(name):
    # Check if corresponding .obj file exists
    # Render the mesh
    pass

# Creates (instances) mesh to the current MAYA scene.
def createMesh(name):
    imported_objects = cmds.file("/Users/rafa/Documents/Dev/Prim/Prim/primitives/meshes/sphere.obj", i = True, rnn=True)
    transforms = cmds.ls(imported_objects, type='transform')

    for i, object in enumerate(transforms):
        # rename it
        goodName = '%s_%s' % ("sphere", str(i+1).zfill(3))
        cmds.rename(object, goodName)

# Saves selected mesh in the scene to the .prim file, and updates library.
def savePrimitive(name, data):
    updateLibrary()
    pass

# Deletes mesh from .prim file, its .obj mesh, and its preview.
def deletePrimitive(name):
    pass
