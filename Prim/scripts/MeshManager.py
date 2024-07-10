# TODO Functionality:
# - Check for corrupt data (e.g. file name changed) and prompt user

#TODO Data:
# - Current .prim file being used
# - Absolute path to module folder

def updateLibrary():
    pass

# Renders a 3/4, lambertian, black and white preview of the primitive. Stores as .png image.
def renderMeshPreview(name):
    # Check if corresponding .obj file exists
    # Render the mesh
    pass

# Creates (instances) mesh to the current MAYA scene.
def createMesh(name):
    pass

# Saves selected mesh in the scene to the .prim file, and updates library.
def savePrimitive(name, data):
    updateLibrary()
    pass

# Deletes mesh from .prim file, its .obj mesh, and its preview.
def deletePrimitive(name):
    pass
