#####################################################
## NAME: Minimum Bounding Rectangle Tools
## Source Name: MBR_Tools.pyt
## Version: ArcGIS 10.1
## Author: Esri.
##                     
## Description: 
##
##
## O.C. - cfrye - Mar 20, 2006
## Update - cfrye - Mar, 20, 2006
## Update - mfunk - Aug, 3, 2012 - update to 10.1 and PYT
## Update - mfunk - Aug, 8, 2012 - Add MBR bearing attribute
#####################################################
import os, traceback, types, math
import arcpy

debug = False # flag additional debug messaging

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "MBRTools"
        self.alias = "mbr"

        # List of tool classes
        self.tools = [MBRPolygons,MBRAnalysis]

class MBRPolygons(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Minimum Bounding Rectangle Polygons"
        self.description = "Creates a new polygon dataset containing a minimum bounding rectangle for each of the polygon features in the input dataset. Ideally the shapes should be single part."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        #Input polygon layer: 0, Required, Input
        param0 = arcpy.Parameter(
            displayName="Input polygon layer",
            name="inPolyLayer",
            datatype="Feature Layer",
            parameterType="Required",
            direction="Input"
        )
        # make sure we can only select polygon feature layers
        param0.filter.list = ["Polygon"]
        
        #Output polygon feature class: 1, Required, Output
        param1 = arcpy.Parameter(
            displayName="Output polygon feature class",
            name="outPolyFC",
            datatype="Feature Class",
            parameterType="Required",
            direction="Output"
        )
        
        params = [param0,param1]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        
        # input and output parameters
        inPolyLayer = parameters[0].valueAsText
        outPolyFc = parameters[1].valueAsText 
        
        try:
            # copy input to output
            arcpy.CopyFeatures_management(inPolyLayer,outPolyFc)
            
            # check L2W & MBR fields, add if missing
            if "L2WRatio" not in arcpy.ListFields(outPolyFc):
                arcpy.AddMessage("Adding L2WRatio field ...")
                arcpy.AddField_management(outPolyFc,"L2WRatio","LONG",32,8,"#","Length to width ratio")
            if "MBRArea" not in arcpy.ListFields(outPolyFc):
                arcpy.AddMessage("Adding MBRArea field ...")
                arcpy.AddField_management(outPolyFc,"MBRArea","LONG",32,8,"#","Polygon to MBR area ratio")
            if "MBRBearing" not in arcpy.ListFields(outPolyFc):
                arcpy.AddMessage("Adding MBRBearing field ...")
                arcpy.AddField_management(outPolyFc,"MBRBearing","LONG",32,8,"#","Bearing angle of MBR (degrees)")
            
            # cursor through each field and calc properties
            arcpy.AddMessage("Updating " + str(arcpy.GetCount_management(outPolyFc).getOutput(0)) + " geometry and description fields ...")
            rows = arcpy.da.UpdateCursor(outPolyFc,["SHAPE@","L2WRatio","MBRArea","MBRBearing","OID@"])
            for row in rows:
                feat = row[0]
                hullRect = row[0].hullRectangle.split(" ")
                polyArea = row[0].area
                hullArray = arcpy.Array()
                x0 = float(str(hullRect[0]))
                y0 = float(str(hullRect[1]))
                p0 = arcpy.Point(x0,y0)
                hullArray.add(p0)
                
                x1 = float(str(hullRect[2]))
                y1 = float(str(hullRect[3]))
                p1 = arcpy.Point(x1,y1)
                hullArray.add(p1)
                
                x2 = float(str(hullRect[4]))
                y2 = float(str(hullRect[5]))
                p2 = arcpy.Point(x2,y2)
                hullArray.add(p2)
                
                x3 = float(str(hullRect[6]))
                y3 = float(str(hullRect[7]))
                p3 = arcpy.Point(x3,y3)
                hullArray.add(p3)
                hullPoly = arcpy.Polygon(hullArray)
                
                Dx0 = x0 - x1
                Dy0 = y0 - y1
                Dx1 = x1 - x2
                Dy1 = y1 - y2
                w2 = ((Dx0 * Dx0) + (Dy0 * Dy0)) ** 0.5
                l2 = ((Dx1 * Dx1) + (Dy1 * Dy1)) ** 0.5
                
                #Calculate MBR bearing
                quadBearing = None
                arithBearing = None
                geoBearing = None
                if (w2 > l2):
                    quadBearing = math.degrees(math.atan2(y1 - y0,x1 - x0))
                if (w2 < l2):
                    quadBearing = math.degrees(math.atan2(y2 - y1,x2 - x1))
                if (w2 == l2):
                    quadBearing = math.degrees(math.atan2(y2 - y1,x2 - x1))
                    arcpy.AddMessage("Feature with OBJECTID " + str(row[4]) + " has a square MBR.")
                    
                if quadBearing < 0.0:
                    arithBearing = 360.0 + quadBearing
                else:
                    arithBearing = quadBearing
                    
                if debug == True: arcpy.AddMessage("quadBearing: " + str(quadBearing) + ", arithBearing: " + str(arithBearing))
                geoBearing = self.Geo2Arithmetic(arithBearing) # convert arithmetic bearings to geographic bearings
        
                a2 = w2 * l2
                HA = (polyArea / a2) * 100
                RatioL2W = l2 / w2
                
                # update cursor items
                row[0] = hullPoly
                row[1] = RatioL2W
                row[2] = HA
                row[3] = geoBearing
                
                # update existing row with new values
                rows.updateRow(row)
            del row
            del rows
            
            
        
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
            msgs = "\nArcPy ERRORS:\n" + arcpy.GetMessages() + "\n"
        
            # Return python error messages for use in script tool or Python Window
            arcpy.AddError(pymsg)
            arcpy.AddError(msgs)
        
            # Print Python error messages for use in Python / Python Window
            print pymsg + "\n"
            print msgs
            
        return
    
    def Geo2Arithmetic(self, inAngle):
        inAngle = math.fmod(inAngle,360.0)
        outAngle = None
        #0 to 90
        if (inAngle >= 0.0 and inAngle <= 90.0):
            outAngle = math.fabs(inAngle - 90.0)
        # 90 to 360
        if (inAngle >= 90.0 and inAngle < 360.0):
            outAngle = 360.0 - (inAngle - 90.0)
        if debug == True: arcpy.AddMessage("inAngle: " + str(inAngle) + ", outAngle: " + str(outAngle))
        return float(outAngle)


class MBRAnalysis(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Minimum Bounding Rectangle Polygon Analyzer"
        self.description = "Adds fields that describe a polygon shape's relationship to its minimum bounding rectangle. The contents of these fields supports queries for determining how to label these features and for how to select these features for generalization."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
                #Input polygon layer: 0, Required, Input
        param0 = arcpy.Parameter(
            displayName="Input polygon layer",
            name="inPolyLayer",
            datatype="Feature Layer",
            parameterType="Required",
            direction="Input"
        )
        # make sure we can only select polygon feature layers
        param0.filter.list = ["Polygon"]
        
        #Output polygon feature class: 1, Required, Output
        param1 = arcpy.Parameter(
            displayName="Output polygon feature class",
            name="outPolyFC",
            datatype="Feature Class",
            parameterType="Required",
            direction="Output"
        )
        params = [param0,param1]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        
        # input and output parameters
        inPolyLayer = parameters[0].valueAsText
        outPolyFc = parameters[1].valueAsText  
        
        try:
            # copy input to output
            arcpy.CopyFeatures_management(inPolyLayer,outPolyFc)
            
            #Add Fields
            inputFieldList = arcpy.ListFields(inPolyLayer)
            inputFieldNameList = []
            for f in inputFieldList: inputFieldNameList.append(f.name)
            del inputFieldList
            
            #Check to see if the new fields already exist, if not create them
            if not "HullWidth" in inputFieldNameList:
                arcpy.AddMessage("Adding HullWidth field ...")
                arcpy.AddField_management(outPolyFc,"HullWidth","DOUBLE",32,8,"","Hull Width")
            if not "HullLen" in inputFieldNameList:
                arcpy.AddMessage("Adding HullLen field ...")
                arcpy.AddField_management(outPolyFc,"HullLen","DOUBLE",32,8,"","Hull Length")
            if not "MBRArea" in inputFieldNameList:
                arcpy.AddMessage("Adding MBRArea field ...")
                arcpy.AddField_management(outPolyFc,"MBRArea","DOUBLE",32,8,"","Polygon to MBR area ratio")
            if not "L2WRatio" in inputFieldNameList:
                arcpy.AddMessage("Adding L2WRatio field ...")
                arcpy.AddField_management(outPolyFc,"L2WRatio","DOUBLE",32,8,"","Length to width ratio")
            if not "PartCount" in inputFieldNameList:
                arcpy.AddMessage("Adding PartCount field ...")
                arcpy.AddField_management(outPolyFc,"PartCount","LONG",32,8,"","Number of parts in feature")
            if "MBRBearing" not in arcpy.ListFields(outPolyFc):
                arcpy.AddMessage("Adding MBRBearing field ...")
                arcpy.AddField_management(outPolyFc,"MBRBearing","LONG",32,8,"#","Bearing angle of MBR (degrees)")
                
        
            #Get Values for Fields
            arcpy.AddMessage("Updating " + str(arcpy.GetCount_management(outPolyFc).getOutput(0)) + " fields from geometry properties ...")
            rows = arcpy.da.UpdateCursor(outPolyFc,["SHAPE@","HullWidth","HullLen","MBRArea","L2WRatio","PartCount","MBRBearing","OID@"])
            for row in rows:
                geometryArea = row[0].area
                geometryPartCount = row[0].partCount
            
                # get geometry properties
                MbrCoords = row[0].hullRectangle.split(" ")
                x0 = float(str(MbrCoords[0]))
                y0 = float(str(MbrCoords[1]))
                x1 = float(str(MbrCoords[2]))
                y1 = float(str(MbrCoords[3]))
                x2 = float(str(MbrCoords[4]))
                y2 = float(str(MbrCoords[5]))
                Dx0 = x0 - x1
                Dy0 = y0 - y1
                Dx1 = x1 - x2
                Dy1 = y1 - y2
                w2 = ((Dx0 * Dx0) + (Dy0 * Dy0)) ** 0.5
                l2 = ((Dx1 * Dx1) + (Dy1 * Dy1)) ** 0.5
                a2 = w2 * l2
                HA = (geometryArea / a2) * 100
                RatioL2W = l2 / w2
                
                #Calculate MBR bearing (bearing of longest side)
                quadBearing = None
                arithBearing = None
                geoBearing = None
                # which is longest side?
                if (w2 > l2):
                    quadBearing = math.degrees(math.atan2(y1 - y0,x1 - x0))
                if (w2 < l2):
                    quadBearing = math.degrees(math.atan2(y2 - y1,x2 - x1))
                if (w2 == l2):
                    quadBearing = math.degrees(math.atan2(y2 - y1,x2 - x1))
                    arcpy.AddMessage("Feature with OBJECTID " + str(row[4]) + " has a square MBR.")  
                # ATAN2 quadBearing to arithmetic bearing 
                if quadBearing < 0.0:
                    arithBearing = 360.0 + quadBearing
                else:
                    arithBearing = quadBearing
                
                if debug == True: arcpy.AddMessage("quadBearing: " + str(quadBearing) + ", arithBearing: " + str(arithBearing))
                # arithmetic bearing to geographic bearing
                geoBearing = self.Geo2Arithmetic(arithBearing) # convert arithmetic bearings to geographic bearings
                
                # update fields in row
                row[1] = w2 # HullWidth
                row[2] = l2 # HullLen
                row[3] = HA # MBRArea
                row[5] = geometryPartCount # PartCount
                row[4] = RatioL2W # L2WRatio
                row[6] = geoBearing # MBRBearing
                
                rows.updateRow(row)
            del row
            del rows
            arcpy.AddMessage("Successfully added shape type metrics to polygon data")
        
        
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
            msgs = "\nArcPy ERRORS:\n" + arcpy.GetMessages() + "\n"
        
            # Return python error messages for use in script tool or Python Window
            arcpy.AddError(pymsg)
            arcpy.AddError(msgs)
        
            # Print Python error messages for use in Python / Python Window
            print pymsg + "\n"
            print msgs
        return
    
    def Geo2Arithmetic(self, inAngle):
        inAngle = math.fmod(inAngle,360.0)
        outAngle = None
        #0 to 90
        if (inAngle >= 0.0 and inAngle <= 90.0):
            outAngle = math.fabs(inAngle - 90.0)
        # 90 to 360
        if (inAngle >= 90.0 and inAngle < 360.0):
            outAngle = 360.0 - (inAngle - 90.0)
        if debug == True: arcpy.AddMessage("inAngle: " + str(inAngle) + ", outAngle: " + str(outAngle))
        return float(outAngle)
