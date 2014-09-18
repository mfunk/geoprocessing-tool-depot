#!/usr/bin/env python

#------------------------------------------------------------------------------
# Copyright 2014 Esri
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#------------------------------------------------------------------------------
# 
# ==================================================
# DeleteDomainsByType.py
# --------------------------------------------------
# Built on ArcGIS 10.3
# ==================================================
# 
# Delete only domains of certain field type from inputGDB.
#
# 

# IMPORTS ==========================================
import os, sys, traceback
import arcpy
from arcpy import env

# LOCALS ===========================================
deleteme = [] # intermediate datasets to be deleted
debug = True # extra messaging during development
domainsToDelete = []

# FUNCTIONS ========================================
def DropDomain(source):
    arcpy.AddMessage("Dropping domains from " + str(source))
    fields = arcpy.ListFields(source)
    if fields:
        for field in fields:
            if field.domain != "":
                if field.domain in domainsToDelete:
                    arcpy.AddMessage("Dropping " + str(field.domain) + " from " + str(field.name))
                    arcpy.RemoveDomainFromField_management(source,str(field.name))
                else:
                    if debug == True: arcpy.AddMessage("Skipping " + str(field.domain))
    return


# ARGUMENTS ========================================
inputGDB = arcpy.GetParameterAsText(0)
domainTypeToRemove = arcpy.GetParameterAsText(1)

# MAIN =============================================
try:
    # get/set environment
    env.overwriteOutput = True
    env.workspace = inputGDB

    arcpy.AddWarning("All domains of type " + domainTypeToRemove + " will be removed from " + inputGDB)

    # get a list of domains
    domains = arcpy.da.ListDomains(inputGDB)
    numDomains = len(domains)
    
    arcpy.AddMessage("There are " + str(numDomains) + " domains in " + inputGDB)
    counter = 0
    
    arcpy.AddMessage("Making list of domains to remove ...")
    for domain in domains:
        if debug == True: arcpy.AddMessage(str(domain.name) + " is type " + str(domain.type))
        #TODO: option to exclude Representation Rules???
        if domain.type == domainTypeToRemove:
            domainsToDelete.append(domain.name)
            counter += 1
    del domain
    domainsToDelete.sort()
    
    arcpy.AddMessage("Found " + str(counter) + " domains of type " + domainTypeToRemove)
    if debug == True: arcpy.AddMessage("domainsToDelete: \n" + str(domainsToDelete))
    
    arcpy.AddMessage("Domains must be dropped from fields before they can be deleted ...")
    # get a list of all stand-alone tables in the inputGDB
    tables = arcpy.ListTables()
    for table in tables:
        # get a list of fields in the table
        DropDomain(table)
                    
    featureClasses = arcpy.ListFeatureClasses()
    for featureClass in featureClasses:
        DropDomain(featureClass)
        
    datasets = arcpy.ListDatasets()
    for dataset in datasets:
        newpath = os.path.join(inputGDB,dataset)
        env.workspace = newpath
        featureClasses = arcpy.ListFeatureClasses()
        for featureClass in featureClasses:
            DropDomain(featureClass)
            
    rasters = arcpy.ListRasters()
    for raster in rasters:
        if raster.hasRAT == True:
            DropDomain(raster)


    arcpy.AddMessage("Deleting domains ...")
    for domain in domainsToDelete:
        arcpy.AddMessage("Deleting " + str(domain))
        # Lets see if we can skip over any errors here and continue...
        try: 
            arcpy.DeleteDomain_management(inputGDB,domain)
        except:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            arcpy.AddWarning("Could not remove domain " + domain + "\n" + tbinfo + "\n" + arcpy.GetMessages())
            pass
   
   
    
    # Set output
    arcpy.SetParameter(2,inputGDB)
   
   
    
except arcpy.ExecuteError: 
    # Get the tool error messages 
    msgs = arcpy.GetMessages() 
    arcpy.AddError(msgs) 
    print(msgs)

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
    print(pymsg + "\n")
    print(msgs)

finally:
    if debug == False and len(deleteme) > 0:
        # cleanup intermediate datasets
        if debug == True: arcpy.AddMessage("Removing intermediate datasets...")
        for i in deleteme:
            if debug == True: arcpy.AddMessage("Removing: " + str(i))
            arcpy.Delete_management(i)
        if debug == True: arcpy.AddMessage("Done")
        
        


