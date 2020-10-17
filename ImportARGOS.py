##---------------------------------------------------------------------
## ImportARGOS.py
##
## Description: Read in ARGOS formatted tracking data and create a line
##    feature class from the [filtered] tracking points
##
## Usage: ImportArgos <ARGOS folder> <Output feature class> 
##
## Created: Fall 2020
## Author: John.Fay@duke.edu (for ENV859)
##---------------------------------------------------------------------

# Import modules
import sys, os, arcpy

# Allow arcpy to overwrite outputs
arcpy.env.overwriteOutput = True

# Set input variables (Hard-wired)
#inputFile = 'V:\\ARGOSTracking\\Data\\ARGOSData\\1997dg.txt'
inputFolder = "V:/ARGOSTracking/data/ARGOSdata"
outputFC = "V:/ARGOSTracking/Scratch/ARGOStrack.shp"
outputSR = arcpy.SpatialReference(54002)

# Create an empty feature class to which we'll add features
outPath,outName = os.path.split(outputFC)
arcpy.CreateFeatureclass_management(outPath,outName,"POINT","","","",outputSR)

# Add TagID, LC, IQ, and Date fields to the output feature class
arcpy.AddField_management(outputFC,"TagID","LONG")
arcpy.AddField_management(outputFC,"LC","TEXT")
arcpy.AddField_management(outputFC,"Date","TEXT")

# Create an insert cursor
cur = arcpy.da.InsertCursor(outputFC,['Shape@','TagID','LC','Date'])

#Iterate through each ARGOS file in the user-supplied folder
inputFiles = os.listdir(inputFolder)
for inputFile in inputFiles:
    #Don't process README.txt file
    if inputFile == 'README.txt':
        continue
    
    # Add full path to inputFile name
    inputFile_Full = os.path.join(inputFolder,inputFile)
    print(f"Processing {inputFile}")
 
    # Open the ARGOS data file for reading
    inputFileObj = open(inputFile_Full,'r')
    
    # Get the first line of data, so we can use the while loop
    lineString = inputFileObj.readline()
    
    #Start the while loop
    while lineString: 
        
        # Set code to run only if the line contains the string "Date: "
        if ("Date :" in lineString):
            
            # Parse the line into a list
            lineData = lineString.split()
            
            # Extract attributes from the datum header line
            tagID = lineData[0]
            obsDate= lineData[3]
            obsTime = lineData[4]
            obsLC = lineData[7]
            
            # Extract location info from the next line
            line2String = inputFileObj.readline()
            
            # Parse the line into a list
            line2Data = line2String.split()
            
            # Extract the date we need to variables
            obsLat = line2Data[2]
            obsLon= line2Data[5]
       
            try: 
       
                # Convert raw coordinate strings to numbers
                if obsLat[-1] == 'N':
                    obsLat = float(obsLat[:-1])
                else:
                    obsLat = float(obsLat[:-1]) * -1
                if obsLon[-1] == 'E':
                    obsLon = float(obsLon[:-1])
                else:
                    obsLon = float(obsLon[:-1]) * -1
        
                # Create a point object
                obsPoint = arcpy.Point()
                obsPoint.X = obsLon
                obsPoint.Y = obsLat
    
            except Exception as e:
                pass
                # print(f"Error adding record {tagID} to the output")
           
            # Convert the point to a point geometry object with spatial reference
            inputSR = arcpy.SpatialReference(4326)
            obsPointGeom = arcpy.PointGeometry(obsPoint,inputSR)
    
            # Add a feature using our insert cursor
            feature = cur.insertRow((obsPointGeom,tagID,obsLC,obsDate.replace(".","/") + " " + obsTime))
            
        # Move to the next line so the while loop progresses
        lineString = inputFileObj.readline()
        
    #Close the file object
    inputFileObj.close()

#Delete the cursor object
del cur