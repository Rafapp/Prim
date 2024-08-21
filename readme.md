<div align = "center">
  <h1>Prim</h1>
  <img src = https://github.com/Rafapp/Prim/assets/38381290/7b585bc9-704f-4745-8c1b-783d7c551255 width = "350px" align = "center">
  <h2>A python Qt plugin for managing & sharing 3D primitives in Maya</h2>
</div>

## Features
- Saving in-scene meshes as named primitives to `.prim` library.
- ( INSERT GIF )
- Exporting and Importing a primitive library with data from all its meshes using the `.prim` file format.
- ( INSERT GIF )
- Mesh thumbnails, with custom capture angles.
- ( INSERT GIF )

## Installation
[VIDEO TUTORIAL AVAILABLE](https://youtu.be/OK2ueSc0YoU)

1. Download, and unzip the [latest release](https://github.com/Rafapp/Prim/releases) of `Prim.zip` in a location of your choosing.
2. Adding the module to maya's environment file:
   1. Find the `Maya.env` file in your Maya installation.
       * Windows: `C:\Users\<YourUsername>\Documents\maya\<MayaVersion>\Maya.env`
       * MacOS: `/Users/<YourUsernamer>/Library/Preferences/Autodesk/maya/2<MayaVersion>/Maya.env`
       * Linux: `/home/<YourUsername>/maya/<MayaVersion>/Maya.env`
         
   2. Edit the `Maya.env` file with a text editor and add this line:
       * `MAYA_MODULE_PATH = <Path to your prim installation folder>`
       * Example: `MAYA_MODULE_PATH = /Users/rafa/Documents/Dev/Prim`

3. Open maya's plug-in manager in `Windows > Settings/Preferences > Plug-in manager`
<img width="448" alt="image" src="https://github.com/user-attachments/assets/6f0fcf2b-7b05-401a-ae59-877a5559b25f">


5. Search for `PrimPlugin.py` and ONLY check `Loaded`. Do not check `Auto load`, this will duplicate icons in your shelf every time you open Maya.
<img width="637" alt="image" src="https://github.com/user-attachments/assets/cbe7ef5d-b455-420f-9345-ca1a04a6d369">

6. Prim will be added to your `Custom` shelf
<img width="1007" alt="Screenshot 2024-08-21 at 11 58 24 AM" src="https://github.com/user-attachments/assets/c71aca58-6700-4416-bc39-b11c37e8c279">
