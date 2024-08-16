<div align = "center">
  <h1>Prim</h1>
  <img src = https://github.com/Rafapp/Prim/assets/38381290/7b585bc9-704f-4745-8c1b-783d7c551255 width = "350px" align = "center">
  <h2>A python Qt plugin for managing & sharing 3D primitives in Maya</h2>
</div>

## Features
- Saving in-scene meshes as named primitives to `.prim` library.
- Exporting and Importing a primitive library with data from all its meshes using the `.prim` file format.
- Mesh thumbnails, with custom capture angles.

## Installation
### Adding as a Maya module:

[Video tutorial](https://youtu.be/OK2ueSc0YoU)

1. Download, and unzip the [latest release](https://github.com/Rafapp/Prim/releases) of Prim in a location of your choosing.
2. Adding the environment file:
- a
- b
- c
Add to maya .env found here:
  /Users/rafa/Library/Preferences/Autodesk/maya/2025/
This line:
  MAYA_MODULE_PATH = /Users/rafa/Documents/Dev/Prim/Prim

4. Go to maya env file. Add module path to a user created dir.
5. Put prim in that dir.
6. Run maya, plugin manager, and click on load and enable. Enable auto load too.
