import maya.api.OpenMaya as om
import maya.cmds as cmds
import maya.mel as mel
import sys
import os

# We are using Maya Python API 2.0
def maya_useNewAPI():
    pass


# Helper function, creates error dialogue
def show_error_dialog(prompt):
    cmds.confirmDialog(
        title='Error',
        message=prompt,
        button='Ok',
        dismissString='Ok'
    )

"""
Renders a preview of the mesh being saved using the viewport camera
- Saves as .png file in /../primitives/thumbnails
"""
def renderMeshPreview(name):
    width = 100
    height = 100
    curFrame = int(cmds.currentTime(query=True))

    dir_path = os.path.dirname(os.path.realpath(__file__)) + "/../primitives/thumbnails"
    fullPath = dir_path + "/" + name + ".png"

    # TODO: Add button to choose if user wants wireframe, which will toggle this de-select
    # cmds.select(clear=True)
    cmds.playblast(fr=curFrame, v=False, fmt="image", c="png", orn=False, cf=fullPath, wh=[width,height], p=100)

def instanceMesh(mesh_name):
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
def savePrimitiveData(mesh_name):
    if not mesh_name:
        show_error_dialog("Please provide a primitive name")
        return

    # Check for files in /meshes
    dir_path = os.path.dirname(os.path.realpath(__file__)) + "/../primitives/meshes"
    files = cmds.getFileList(folder = dir_path)

    if files: 
        obj_files = [f for f in files if f.endswith('.obj')]
        if obj_files: 
            for item in obj_files:
                full_name = os.path.join(dir_path, item)
                file_name, ext = os.path.splitext(os.path.basename(full_name))
                if file_name == mesh_name:
                    show_error_dialog(f"Mesh with name {mesh_name} already exists. Please try a new name.\n\n(Note: Saving a primitive with the same name will update its preview)")
                    return

    dir_path = os.path.dirname(os.path.realpath(__file__)) + "/../primitives/meshes"
    full_dir_path = dir_path + "/" + mesh_name + ".obj"
    cmds.file(full_dir_path,
              force=True,
              options="groups=0;ptgroups=0;materials=0;smoothing=0;normals=0;exportTextures=0",
              type="OBJexport", 
              pr=True, 
              es=True)
    print(f"Saved: {mesh_name}.obj")

    # Add header for this primitive (mesh name, beginMesh)
    from Prim import get_current_prim_file_path
    current_prim = get_current_prim_file_path()
    prim_file = open(current_prim, "a")
    newprimitive_str = f"\n{mesh_name}\nbeginMesh\n"
    prim_file.write(newprimitive_str)

    # Add .obj data
    obj_file = open(full_dir_path, "r")
    next(obj_file)
    next(obj_file)
    objdata_str = obj_file.read()
    prim_file.write(objdata_str)
    endprimitive_str = "endMesh"
    prim_file.write(endprimitive_str)

    # Close files
    prim_file.close()
    obj_file.close()

    print(f"Updated .prim file: {current_prim}")

# Deletes mesh from .prim file, its .obj mesh, and its preview.
def deletePrimitiveData(mesh_name):

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
        print("Error: Could not find mesh for primitive \"" + mesh_name + "\" to delete ...")
        return

    # Delete the mesh's .obj file
    os.remove(mesh_path)

    # Delete primitive data from the .prim file 
    from Prim import get_current_prim_file_path
    primfile = get_current_prim_file_path()
    with open(primfile, 'r') as file:
        lines = file.readlines()
    
    with open(primfile, 'w') as file:
        skip = False
        for line in lines:
            if mesh_name in line:
                skip = True
            if not skip:
                file.write(line)
            if skip and "endMesh" in line:
                skip = False
 
    print("Succesfully deleted primitive: " + "\"" + mesh_name + "\"")

# Generates .obj files from .prim file
def generateMeshesFromPrimFile():
    from Prim import get_current_prim_file_path
    primfile = get_current_prim_file_path()

    obj_meshes = {}

    # Read prim file, create dictionary of mesh name to mesh obj data 
    with open(primfile, 'r') as file:
        lines = file.readlines()
        previous_line = None
        obj_data = []
        skip = True 
        name = ""

        for line in lines:
            current_line = line.strip()
            if "beginMesh" in line:
                name = previous_line
                skip = False
            if skip == False:
                obj_data.append(current_line)
            if "endMesh" in line:
                skip = True 
                print("Generated: " + name + ".obj")
                obj_meshes[name] = obj_data
                obj_data = []
            
            previous_line = current_line

    # Create the .obj files from the dictionary
    meshes_path = os.path.dirname(os.path.realpath(__file__)) + "/../primitives/meshes/"
    print(obj_meshes)
    for name, data in obj_meshes.items():
        print("New mesh from .prim file: \"" + name + "\" created")
        with open(os.path.join(meshes_path, name + ".obj"), 'w') as file:
            file.write('\n'.join(data) + '\n')
