
# ==================================================
# Add Sinuosity Measure To Line.py
# --------------------------------------------------
# Built for ArcGIS 10.1
#
# Calculates the sinuosity (curviness) index for each line feature in the inputFeatures.
# The index is measured as the path length along the line divided by the
# shortest distance between it's starting point and endpoint.
#
# Measurement types:
# EUCLIDEAN - Measures the direct 2D or 3D distance between the line's vertices.
#
# GEODESIC - The shortest line between any two points on the earth's surface
#   on a spheroid (ellipsoid). One use for a geodesic line is when you want
#   to determine the shortest distance between two cities for an airplane's
#   flight path. This is also known as a great circle line if based on a sphere
#   rather than an ellipsoid.
#
# GREAT_ELLIPTIC - The line on a spheroid (ellipsoid) defined by the intersection
#   at the surface by a plane that passes through the center of the spheroid and
#   the start and endpoints of a segment. This is also known as a great circle
#   when a sphere is used.
#
# LOXODROME - A loxodrome is not the shortest distance between two points but
#   instead defines the line of constant bearing, or azimuth. Great circle
#   routes are often broken into a series of loxodromes, which simplifies
#   navigation. This is also known as a rhumb line.
#
# PLANAR - Planar measurement use 2D Cartesian mathematics to calculate lengths
#   and areas. This option is only available when measuring in a projected
#   coordinate system and the 2D plane of that coordinate system will be used
#   as the basis for the measurements.
#
# PRESERVE_SHAPE - This type calculates the area or length of the geometry on
#   the surface of the Earth ellipsoid, for geometry defined in a projected
#   or geographic coordinate system. This option preserves the shape of the
#   geometry in its coordinate system.
# ==================================================

# IMPORTS ==========================================
import os, traceback
import arcpy

# FUNCTIONS ========================================

# ARGUMENTS & LOCALS ===============================
inputFeatures = arcpy.GetParameterAsText(0)
sinuosityFieldName = arcpy.GetParameterAsText(1)
lengthMeasureType = arcpy.GetParameterAsText(2) #EUCLIDEAN | GEODESIC | GREAT_ELLIPTIC | LOXODROME | PLANAR | PRESERVE_SHAPE
deleteme = []
debug = False

try:
    
    # Does the input have Zs?
    hasZ = arcpy.Describe(inputFeatures).hasZ
    
    # if field does not exist, add it
    fields = arcpy.ListFields(inputFeatures)
    fieldNames = []
    for f in fields: fieldNames.append(f.name)
    del fields
    if not sinuosityFieldName in fieldNames:
        arcpy.AddMessage("Adding field " + sinuosityFieldName + "...")
        arcpy.AddField_management(inputFeatures,sinuosityFieldName,"DOUBLE","#","#","#","Sinuosity Index")
    else:
        arcpy.AddWarning(sinuosityFieldName + " field already exists. Updating existing field.")
        
    # Calculate sinuosity measure for each line
    arcpy.AddMessage("Adding measure to " + str(arcpy.GetCount_management(inputFeatures).getOutput(0)) + " features...")
    with arcpy.da.UpdateCursor(inputFeatures,["OID@","SHAPE@",sinuosityFieldName]) as rows:
        for row in rows:
            
            # find shortest distance from start point to end point
            oid = row[0]
            shape = row[1]
            firstPoint = arcpy.PointGeometry(shape.firstPoint)
            lastPoint = arcpy.PointGeometry(shape.lastPoint)
            shortestLength = firstPoint.distanceTo(lastPoint)
            
            # if the points are the same, it's a zero length feature or a closed loop
            if shortestLength == 0.0:
                arcpy.AddWarning(str(oid) + " is a closed loop or zero-length line. Sinuosity is null.")
                row[2] = None
            else:
                # calc path distance along the line
                if lengthMeasureType == "EUCLIDEAN" and hasZ == True:
                    pathLength = shape.length3D
                if lengthMeasureType == "GEODESIC":
                    pathLength = shape.getLength("GEODESIC")
                if lengthMeasureType == "GREAT_ELLIPTIC":
                    pathLength = shape.getLength("GREAT_ELLIPTIC")
                if lengthMeasureType == "LOXODROME":
                    pathLength = shape.getLength("LOXODROME")
                if lengthMeasureType == "PRESERVE_SHAPE":
                    pathLength = shape.getLength("PRESERVE_SHAPE")
                else:
                    pathLength = shape.length
                    
                row[2] = pathLength/shortestLength
                if debug == True: arcpy.AddMessage(str(oid) + ": " + str(pathLength) + ", " + str(shortestLength) + ", " + str(row[2]))
                
            rows.updateRow(row)
        
    arcpy.SetParameterAsText(3,inputFeatures)

except arcpy.ExecuteError: 
    # Get the tool error messages 
    msgs = arcpy.GetMessages() 
    arcpy.AddError(msgs) 
    print msgs

except:
    # Get the traceback object
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]

    # Concatenate information together concerning the error into a message string
    pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
    msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages() + "\n"

    # Return python error messages for use in script tool or Python Window
    arcpy.AddError(pymsg)
    arcpy.AddError(msgs)

    # Print Python error messages for use in Python / Python Window
    print pymsg + "\n"
    print msgs

finally:
    # cleanup intermediate datasets
    if debug == False and len(deleteme) > 0:
        arcpy.AddMessage("Removing intermediate datasets...")
        for i in deleteme:
            if debug == True: arcpy.AddMessage("Removing: " + str(i))
            arcpy.Delete_management(i)
        if debug == True: arcpy.AddMessage("Done")