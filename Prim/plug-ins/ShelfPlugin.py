import maya.api.OpenMaya as om
import maya.cmds as cmds
import maya.mel as mel

# -----------------------------------------------------------------------
# Shelf plugin: Initializes plugin, and adds to shelf with launch command.
# -----------------------------------------------------------------------

# We are using Maya Python API 2.0
def maya_useNewAPI():
    pass

def addPrimToShelf():
    command = 'from Prim import mainWindow;mainWindow.showWindow()'
    current_shelf = mel.eval('tabLayout -q -selectTab $gShelfTopLevel')

    if cmds.shelfButton('primButton', exists=True):
        return
    #TODO: Make the installer install the icon in the proper place.
    cmds.shelfButton(
        'primButton',
        parent=current_shelf,
        label='Prim',
        command=command,
        image='prim_icon.png',
        sourceType='python'
    )

def initializePlugin(plugin):
    vendor = "Rafael Padilla Perez"
    version = "1.0.0"
    om.MFnPlugin(plugin, vendor, version)

    # Add to shelf, and start up
    addPrimToShelf()

def uninitializePlugin(plugin):
    pass
