geoprocessing-tool-depot
======================

This repo is a collection of ArcGIS geoprocessing tools that I made to do some simple repetitive jobs or made for a
coworker to do some task. They don't really fit into a toolbox or template in ArcGIS, so I put them here. If you think
they're useful give them a try. If you find a problem or have a request, add them to the Issues list. But just be aware...

THERE IS NO GUARANTEE THAT I WILL MAINTAIN OR FIX ANY ISSUES

I've got plenty of intention of doing so, but time and other interests usually work against me.

What you'll find so far in toolboxes (folder):
* General Data Management Tools.tbx
    * Delete Domains By Type

* Geometry Tools.tbx
    * Add Sinuosity Measure To Lines: Geoprocessing tool that adds sinuosity measure to line features. Sinuosity is
measured as the line's path length divided by the distance between the start
point and endpoint.

* layers (folder): contains output .lyr files for the tools.

* scripts (folder): contains the script files used in the toolboxes.
    

## Instructions
1. Download the .tbx, .py and .py.xml files.
2. In ArcMap, go to the .tbx file.
3. Open the tools, read the help, etc.


## Requirements
* These tools run in ArcGIS Desktop 10.3 and up.
* Python 2.7
* The tool's .py file can be modified in a text editor or any Python IDE