import maya.api.OpenMaya as om
import maya.cmds as cmds #TODO: Move maya.cmds to separate file
import maya.mel as mel
import sys
import os

# Maya Python API 2.0
def maya_useNewAPI():
    pass

def show_confirmation_dialog(prompt):
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

def show_error_dialog(prompt):
    cmds.confirmDialog(
        title='Error',
        message=prompt,
        button='Ok',
        dismissString='Ok'
    )

"""
- Render 3/4 view, simple lambertian black and white preview of the primitive
- Saves output as .png file in /thumbnails
"""
def renderMeshPreview(name, objData):
    # Check if corresponding .obj file exists
    # Render the mesh
    pass

"""
- Instance an existing primitive's mesh to the maya scene using its name
"""
def instanceMesh(mesh_name):
    dir_path = os.path.dirname(os.path.realpath(__file__)) + "/../primitives/meshes"
    
    files = cmds.getFileList(folder = dir_path)
    if not files: 
        print("Error: Meshes folder is empty") 
        return

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

"""
- Get selected mesh in scene
- Add its name, and .obj text data to .prim file
"""
def savePrimitiveData(mesh_name):
    if not mesh_name:
        show_error_dialog("Please provide a primitive name")
        return

    # Check for files in /meshes
    dir_path = os.path.dirname(os.path.realpath(__file__)) + "/../primitives/meshes"
    files = cmds.getFileList(folder = dir_path)
        obj_files = [f for f in files if f.endswith('.obj')]
        if obj_files: 
            for item in obj_files:
                full_name = os.path.join(dir_path, item)
                file_name, ext = os.path.splitext(os.path.basename(full_name))
                if file_name == mesh_name:
                    show_error_dialog(f"Mesh with name {mesh_name} already exists. Please try a new name.")
                    return

    selected = cmds.ls(sl=True,long=True) or []
    selectCount = len(selected)

    if selectCount < 1:
        show_error_dialog("Error: Please select at least one mesh")
        return
    elif selectCount > 1:
        show_error_dialog("Error: Please select only one mesh")
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

    # Add .obj text data
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

"""
- Deletes mesh text data from .prim file
- Deletes .obj mesh
- Deletes .png thumbnail
"""
def deletePrimitiveData(mesh_name):
    confirm = show_confirmation_dialog("Are you sure you wish to delete this primitive?\n\nThis action is irreversible!")
    if confirm == False: return

    dir_path = os.path.dirname(os.path.realpath(__file__)) + "/../primitives/meshes"
    
    # Delete .obj file if existing
    files = cmds.getFileList(folder = dir_path)
    if files: 
        obj_files = [f for f in files if f.endswith('.obj')]
        if obj_files: 
            mesh_path = None
            for item in obj_files:
                full_name = os.path.join(dir_path, item)
                file_name, ext = os.path.splitext(os.path.basename(full_name))
                if file_name == mesh_name:
                    mesh_path = full_name
                    break

            if mesh_path:
                os.remove(mesh_path)
            else: 
                print("Error: Could not find mesh for primitive \"" + mesh_name + "\" to delete, skipping deletion ...")
            
    # Delete primitive text data from the .prim file 
    # TODO: Check if there's a better way to do this without creating circular dependencies
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

    #TODO: Delete .png thumbnails from \thumbnails folder
    print("Succesfully deleted primitive: " + "\"" + mesh_name + "\"")

"""
- Delete all .obj files
- Generate all new meshes from name and .obj text data in 
.prim file
"""
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
            if skip and "endMesh" in line:
                skip = False
                print(f"Saving: {name}")
                obj_meshes[name] = obj_data
                obj_data = []
            if not skip:
                obj_data.append(current_line)
            previous_line = current_line
    # TODO: Now that dictionary has name, and .obj file text data, generate and save .obj meshes
