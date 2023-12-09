#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    File name: Capstone.py
    Author: Nicolas Giordano
    Description:  This scripts runs the 'Target Weather Stations for Yield Gap Analysis' geoprocessing tool within ArcGIS Pro. The tool is designed for obtaining the target weather stations required for conducting a yield gap analysis under the Yield Gap Atlas protocol. ‌
    Date created: 12/09/2023
    Python Version: 3.9.16
"""

import arcpy, os


## Define local variables
outGDB = arcpy.GetParameterAsText(0) 
countriesBoundaries = arcpy.GetParameterAsText(1) 
inCZ = arcpy.GetParameterAsText(2) 
areaPlanted = arcpy.GetParameterAsText(3) 
weatherStations = arcpy.GetParameterAsText(4) 
percAreaplanted = float(arcpy.GetParameterAsText(5)) 
selectedCountry = arcpy.GetParameterAsText(6) 
cropField = arcpy.GetParameterAsText(7)


outputPath = os.path.join(os.path.dirname(arcpy.env.workspace), outGDB)
## Set environment(s)
arcpy.env.overwriteOutput = True
## Specify the output spatial reference
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(4326)

# Check if the geodatabase exists
if not arcpy.Exists(outputPath):
    # Create the geodatabase if it doesn't exist
    arcpy.management.CreateFileGDB(os.path.dirname(arcpy.env.workspace), outGDB)
    print(f"Geodatabase '{outGDB}' created successfully.")
else:
    print(f"Geodatabase '{outGDB}' already exists.")
    
## Perform geoprocessing and trap errors
try:
    ## Check for availability of required extensions
    if arcpy.CheckProduct("ArcInfo") == "Available" or arcpy.CheckProduct("ArcInfo") == "AlreadyInitialized":
        
        ## Geoprocessing
        ## Step 1: Define output file names
        outCountry = os.path.join(outputPath, "{0}_Boudaries".format(selectedCountry))
        outAreaPlanted = os.path.join(outputPath, "{0}_{1}_Planted_Area".format(selectedCountry,cropField))
        outClimateZones = os.path.join(outputPath, "{0}_{1}_Area_Climate_Zones".format(selectedCountry,cropField))
        outBufferedWS = os.path.join(outputPath, "{0}_{1}_Area_Weather_Stations_Buffered".format(selectedCountry,cropField))
          
            
        ## Step 2: Select target country    
        arcpy.AddMessage("Your target country is {0}".format(selectedCountry))
        ## Filter rows based on the selected country and save output
        arcpy.analysis.Select(countriesBoundaries, outCountry, "admin = '{0}'".format(selectedCountry))
        
        
        ## Step 3: Select crop area planted based on target country
        arcpy.AddMessage("Selecting layer by {0} area planted in {1}".format(cropField,selectedCountry))
        arcpy.management.MakeXYEventLayer(areaPlanted, "x", "y", "temp1")
        arcpy.management.MakeFeatureLayer("temp1", "tempAreaPlantedLayer")
        arcpy.management.SelectLayerByLocation("tempAreaPlantedLayer","INTERSECT", outCountry)
        
        
        ## Step 4: Filter area planted to desired area planted by the user
        arcpy.AddMessage("Filtering {0} area planted to {1} % of the total planted area in {2}...".format(cropField,percAreaplanted,selectedCountry))
        ## Generate a list of OIDs that contain the target percentage of crop area planted.
        plantedArea = []
        ## Use a SearchCursor to fetch values and OIDs
        with arcpy.da.SearchCursor("tempAreaPlantedLayer", [cropField, "OID@"]) as cursor:
            for row in cursor:
                plantedArea.append(row)
        ## Set the threshold to the desired percentage of area planted
        threshold = (percAreaplanted/100) * sum(value[0] for value in plantedArea)
        ## In order to sum below, sort the list based on the "plantedArea" field in descending order
        plantedArea.sort(key=lambda x: x[0], reverse=True)
        OIDs = []
        totalArea = 0
        for point in plantedArea:
            totalArea += point[0]
            OIDs.append(point[1])
            if totalArea > threshold:
                break
        ## Convert the list of OIDs to a comma-separated string
        OIDs_str = ",".join(map(str, OIDs))
        ## From the tempAreaPlantedLayer select only those OID that make to the desired % planted area
        arcpy.management.SelectLayerByAttribute("tempAreaPlantedLayer", "NEW_SELECTION", "OBJECTID IN ({0})".format(OIDs_str))
        ## Save target area planted output
        arcpy.management.CopyFeatures("tempAreaPlantedLayer", outAreaPlanted)
        
        
        ## Step 5: Select the target climate zones
        arcpy.AddMessage("Clipping climate zones within the target planted area and target country...")
        arcpy.management.MakeFeatureLayer(inCZ, "clipCZLayer")
        ## Select climate zones within target area planted
        arcpy.management.SelectLayerByLocation("clipCZLayer","INTERSECT", outAreaPlanted)
        ## Clip the climate zones to the target country
        arcpy.analysis.Clip("clipCZLayer", outCountry, outClimateZones)
        
        
        ## Step 6: Generate weather stations buffers and clip buffers based on climate zone in which the weather station is located
        arcpy.AddMessage(f"Generating buffers over the weather stations...\nClipping weather station buffers to individual climate zones...\nThis process might take a few seconds...")
        with arcpy.da.SearchCursor(outClimateZones, ["GYGA_CZ"]) as cursor:
            # Use a set to store unique values
            listCZ = []
            for row in cursor:
                value = row[0]
                listCZ.append(value)
        for climateZone in list(set(listCZ)):
            ## Select individual Climate Zones
            indCZ = arcpy.management.SelectLayerByAttribute(outClimateZones, "NEW_SELECTION", "GYGA_CZ = {0}".format(climateZone))
            indWS = arcpy.management.SelectLayerByLocation(weatherStations, 'INTERSECT', indCZ, 0, 'NEW_SELECTION')
            ## Apply a 100 km buffer to each weather station and crip buffer to individual climate zone
            arcpy.analysis.Buffer(indWS, "tempBuffer", "100 Kilometers")
            arcpy.analysis.Clip("tempBuffer", indCZ, "tempBuffer_" + str(climateZone))
        arcpy.management.Merge(arcpy.ListFeatureClasses("tempBuffer_*"), "tempBufferedWS")
        ## Update the weather stations based on the intercepted buffer by the wheat planted area and save output
        selectedWS = arcpy.management.SelectLayerByLocation("tempBufferedWS", 'INTERSECT', outAreaPlanted, 0, 'NEW_SELECTION')
        arcpy.management.CopyFeatures(selectedWS, outBufferedWS)
        
        
        ## Step 7: Delete unnecesary temporary files
        for fc in arcpy.ListFeatureClasses("temp*"):
            arcpy.management.Delete(fc)
        arcpy.AddMessage("Success! Target weather stations identified")
        
    else:
        arcpy.AddMessage("ArcGIS for Desktop Advanced license not available")
        
except arcpy.ExecuteError:
    print(arcpy.GetMessages(2))

finally:
    arcpy.AddMessage("Script run to completion!")
        