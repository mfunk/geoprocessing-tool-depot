geoprocessing-tool-depot
======================

This repo is a collection of ArcGIS geoprocessing tools that I made to do some simple repetitive jobs or made for a
coworker to do some task. They don't really fit into a toolbox or template in ArcGIS, so I put them here. If you think
they're useful give them a try. If you find a problem or have a request, add them to the Issues list. But just be aware...

THERE IS NO GUARANTEE THAT I WILL MAINTAIN OR FIX ANY ISSUES

I've got plenty of intention of doing so, but time and other interests usually work against me.

What you'll find so far in toolboxes:
* General Data Management Tools.tbx
    * Delete Domains By Type

* Geometry Tools.tbx
    * Add Sinuosity Measure To Lines: Geoprocessing tool that adds sinuosity measure to line features. Sinuosity is
measured as the line's path length divided by the distance between the start
point and endpoint.

* MBR (Minimum Bounding Rectangle) Tools
I stole [these tools](http://blogs.esri.com/esri/arcgis/2008/03/21/selecting-polygons-for-maps-at-smaller-scales/) from [Charlie Frye](http://blogs.esri.com/esri/arcgis/author/cfrye/),
Esri's Chief Cartographer, for a project. Well not exactly stole, but borrowed and modified. Charlie shows some really slick ways of
describing polygons by their shape. I cannot take any credit for these tools, that goes to Charlie. My modifications were to take his
tools and put them into a Python Toolbox (PYT).
    * Minimum Bounding Rectangle Polygon Analyzer: Adds fields that describe a polygon shape's relationship to its minimum bounding
    rectangle. The contents of these fields supports queries for determining how to label these features and for how to select these
    features for generalization.
    * Minimum Bounding Rectangle Polygon: Creates a new polygon dataset containing a minimum bounding rectangle for each of the polygon
    features in the input dataset. Ideally the shapes should be single part.
    

## Instructions
1. Download the .tbx, .py and .py.xml files.
2. In ArcMap, go to the .tbx file.
3. Open the tools, read the help, etc.


## Requirements
* These tools run in ArcGIS Desktop 10.3 and up.
* Python 2.7
* The tool's .py file can be modified in a text editor (e.g. Notepad++) or any Python IDE (e.g. Komodo)