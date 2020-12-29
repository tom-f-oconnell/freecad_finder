
#### Usage

```
import freecad_finder
freecad_finder.add_freecad_dirs_to_syspath()

import FreeCAD

# ... your code using FreeCAD here ...
```

#### Installation

You must have Python >= 3.6, but no modules besides the standard library are
required.

To install:
```
git clone https://github.com/tom-f-oconnell/freecad_finder
cd freecad_finder
python3 -m pip install .
```

#### Reasoning

One of the forum posts I found that suggested modifying `sys.path` to accomplish
this: https://forum.freecadweb.org/viewtopic.php?f=22&t=38545#p329103

To see what FreeCAD normally adds to `sys.path`, compare the two cases below:

Using FreeCAD compiled from source in my Ubuntu 18.04, I have the following
`sys.path` in the Python inside the GUI FreeCAD:
```
['/home/tom/.local/lib/python3.6/site-packages/git/ext/gitdb',
 '/home/tom/src/FreeCAD/build/Mod/Inspection',
 '/home/tom/src/FreeCAD/build/Mod/Import',
 '/home/tom/src/FreeCAD/build/Mod/AddonManager',
 '/home/tom/src/FreeCAD/build/Mod/Fem',
 '/home/tom/src/FreeCAD/build/Mod/Start',
 '/home/tom/src/FreeCAD/build/Mod/Show',
 '/home/tom/src/FreeCAD/build/Mod/Web',
 '/home/tom/src/FreeCAD/build/Mod/Drawing',
 '/home/tom/src/FreeCAD/build/Mod/Spreadsheet',
 '/home/tom/src/FreeCAD/build/Mod/OpenSCAD',
 '/home/tom/src/FreeCAD/build/Mod/Arch',
 '/home/tom/src/FreeCAD/build/Mod/ReverseEngineering',
 '/home/tom/src/FreeCAD/build/Mod/Raytracing',
 '/home/tom/src/FreeCAD/build/Mod/Path',
 '/home/tom/src/FreeCAD/build/Mod/Points',
 '/home/tom/src/FreeCAD/build/Mod/Surface',
 '/home/tom/src/FreeCAD/build/Mod/Image',
 '/home/tom/src/FreeCAD/build/Mod/Tux',
 '/home/tom/src/FreeCAD/build/Mod/TechDraw',
 '/home/tom/src/FreeCAD/build/Mod/Sketcher',
 '/home/tom/src/FreeCAD/build/Mod/MeshPart',
 '/home/tom/src/FreeCAD/build/Mod/Measure',
 '/home/tom/src/FreeCAD/build/Mod/Test',
 '/home/tom/src/FreeCAD/build/Mod/Part',
 '/home/tom/src/FreeCAD/build/Mod/Material',
 '/home/tom/src/FreeCAD/build/Mod/PartDesign',
 '/home/tom/src/FreeCAD/build/Mod/Idf',
 '/home/tom/src/FreeCAD/build/Mod/Robot',
 '/home/tom/src/FreeCAD/build/Mod/Draft',
 '/home/tom/src/FreeCAD/build/Mod/Mesh',
 '/home/tom/src/FreeCAD/build/Mod',
 '/home/tom/src/FreeCAD/build/lib',
 '/home/tom/src/FreeCAD/build/Ext',
 '/home/tom/src/FreeCAD/build/bin',
 '/usr/lib/python36.zip',
 '/usr/lib/python3.6',
 '/usr/lib/python3.6/lib-dynload',
 '/home/tom/.local/lib/python3.6/site-packages',
 '/usr/local/lib/python3.6/dist-packages',
 '/usr/lib/python3/dist-packages',
 '/home/tom/.FreeCAD/Macro/',
 '/home/tom/src/FreeCAD/build/Macro',
 '/home/tom/.local/lib/python3.6/site-packages/gitdb/ext/smmap']
```

The contents of `sys.path` in my system `python3.6` (might be the same exact
python executable, though not sure):
```
['',
 '/home/tom/src/rdkit',
 '/home/tom/catkin/devel/lib/python2.7/dist-packages',
 '/opt/ros/melodic/lib/python2.7/dist-packages',
 '/home/tom/src/pymistake',
 '/usr/lib/python36.zip',
 '/usr/lib/python3.6',
 '/usr/lib/python3.6/lib-dynload',
 '/home/tom/.local/lib/python3.6/site-packages',
 '/usr/local/lib/python3.6/dist-packages',
 '/usr/lib/python3/dist-packages']
```

