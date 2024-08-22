<div align = "center">
  <h1>Prim</h1>
  <img src = https://github.com/Rafapp/Prim/assets/38381290/7b585bc9-704f-4745-8c1b-783d7c551255 width = "350px" align = "center">
  <h3>A python Qt plugin for managing & sharing 3D primitives in Maya</h2>
</div>

<div align = "center">
  <h1>Features</h1>
  <h3>Saving in-scene meshes as named primitives to .prim library</h2>
  <img src = https://github.com/user-attachments/assets/f375b1e3-6fd5-4b30-ba3c-27cec5eafc44 width = "500px" align = "center">
  <h3>Exporting and Importing a primitive library with data from all its meshes using the .prim file format</h3>
  <img src = https://github.com/user-attachments/assets/0affb0ff-f554-4c14-89d1-05fdc6355153 width = "500px" align = "center">
  <h3>Mesh thumbnails, with custom capture angles, and optional wireframe</h3>
  <img src = https://github.com/user-attachments/assets/b843b96c-8052-4f4e-9bd0-d7067401446d width = "500px" align = "center">
</div>

## Installation

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
