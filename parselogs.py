'''CSV data log processing for ArduIMU (Python 2.7)
Takes in CSV files of format Datastring, Timestamp
and extracts roll, pitch, yaw and other values
then plots these as a time series.

Created by Ronnie Gane and Beth Collis
Last edit: 21/10/2015

TO DO:
- Encapsulate plotting into a function to reduce redundant code
- Calculate velocity
- Add table for Max/Min/Range/Average/Standard dev for various sensors
- Make "try/except" more sensible
- Filter GPS data: some points have latitude = longitude
- Math/physics magic to transform our X,Y,Z into the vehicle's coordinate system
- Math/physics magic to work out tyre forces
'''

# Library imports

import matplotlib.pyplot as plt         # more plotting
import csv                              # reading and writing CSV files
import re                               # regular expressions for searching strings
from datetime import datetime           # for dealing with time values
from numpy import mean
import numpy as np
from math import sin, cos

'''
currently unused imports
from scipy.misc import imread		# for importing and working with image files
import matplotlib.cbook as cbook	
'''

# Open file

# Hardcode filenames at first
myFile = 'MainTesting_BMW.csv'    # Change to desired input filename
outFile = open('cleaned data BMW session.csv', 'wb')   # Change to desired output filename

# Create CSV "reader" and "writer" files
inFile = open(myFile, 'rb')
reader = csv.reader(inFile)
writer = csv.writer(outFile)
writer.writerow(["Time", "Lat", "Long", "Pitch", "Yaw", "Roll", "AccX", "AccY", "AccZ", "GyroX", "GyroY", "GyroZ"]) # Headers

# Declaring variables
'''We will record all the data values as lists'''
pitchList = []
rollList = []
yawList = []
timeList = []
accXList = []
accYList = []
accZList = []
gyroXList = []
gyroYList = []
gyroZList = []
latList = []
longList = []

# Close any open plots
plt.close("all")

# Loop through lines
for row in reader:
    ''' each row will be list [timestamp, datastring, latitude, longitude]
    Datastring components:
    RLL: Roll, degrees
    PCH: Pitch, degrees
    YAW: Yaw, degrees
    IMUH: ???
    TOW: Time of Week (used for GPS stuff)
    (following according to decode.pde, no idea what units)
    AN0: Gyro X
    AN1: Gyro Y
    AN2: Gyro Z
    AN3: Accelerometer X
    AN4: Accelerometer Y
    AN5: Accelerometer Z
    (following only if GPS attached)
    LAT: Latitude, decimal degrees * 10e7
    LON: Longitude, decimal degrees * 10e7
    ALT: Altitude, metres above sea level * 10e1
    COG: Course over ground
    FIX: Binary indicator of GPS fix.
    SOG: Speed over ground
    SAT: Satellite count
    '''

    dataString = row[1]

    # Find start and end markers of string
    startIndex = dataString.find('!!!')
    endIndex = dataString.find('*')
    
    if (startIndex > -1 and endIndex > startIndex): # makes sure we are only checking complete logs
        
        '''Timestamp'''
        timeStamp = row[0]
        timeList.append(timeStamp)
        
        '''Pitch'''
        try:
            pitch  = re.search("PCH:(-?[0-9]+\.[0-9]+)", dataString).group(1)
        except:
            pitch = pitchList[-1]
            
        '''Roll'''
        try:
            roll  = re.search("RLL:(-?[0-9]+\.[0-9]+)", dataString).group(1)
        except:
            roll = rollList[-1]

        '''Yaw'''
        try:
            yaw  = re.search("YAW:(-?[0-9]+\.[0-9]+)", dataString).group(1)
        except:
            yaw = yawList[-1]

        '''AccX'''
        try:
            accX  = re.search("AN3:(-?[0-9]+\.[0-9]+)", dataString).group(1)            
        except:
            accX = accXList[-1]
        
        '''AccY'''
        try:
            accY  = re.search("AN4:(-?[0-9]+\.[0-9]+)", dataString).group(1)            
        except:
            accY = accYList[-1]        
        
        '''AccZ'''
        try:
            accZ  = re.search("AN5:(-?[0-9]+\.[0-9]+)", dataString).group(1)            
        except:
            accZ = accZList[-1]
        
        '''GyroX'''
        try:
            gyroX  = re.search("AN0:(-?[0-9]+\.[0-9]+)", dataString).group(1)            
        except:
            gyroX = gyroXList[-1]            
        
        '''GyroY'''
        try:
            gyroY  = re.search("AN1:(-?[0-9]+\.[0-9]+)", dataString).group(1)            
        except:
            gyroY = gyroYList[-1]        
        
        '''GyroZ'''
        try:
            gyroZ  = re.search("AN2:(-?[0-9]+\.[0-9]+)", dataString).group(1)            
        except:
            gyroZ = gyroZList[-1]
        
        
        # Transform coordinate system
        rotAng = 20.0   # Transforming by rotation of positive 30 degrees about X axis 
        tMatrix = np.array([[1.0, 0.0, 0.0], [0.0, cos(rotAng), -sin(rotAng)], [0.0, sin(rotAng), cos(rotAng)]])
        
        # Transform pitch(X)/roll(Y)/yaw(Z)
        [pitch, roll, yaw] = np.dot(tMatrix, [float(pitch), float(roll), float(yaw)])
        
        # Transform AccX/Y/Z
        [accX, accY, accZ] = np.dot(tMatrix, [float(accX), float(accY), float(accZ)])
        
        
        # Transform GyroX/Y/Z
        [gyroX, gyroY, gyroZ] = np.dot(tMatrix, [float(gyroX), float(gyroY), float(gyroZ)])
        
        # Add to lists
        pitchList.append(float(pitch))
        rollList.append(float(roll))
        yawList.append(float(yaw))
        accXList.append(float(accX))
        accYList.append(float(accY))
        accZList.append(float(accZ))
        gyroXList.append(float(gyroX))
        gyroYList.append(float(gyroY))
        gyroZList.append(float(gyroZ))
        

        '''GPS'''
        latitude = float(row[2])
        longitude = float(row[3])
        # Uncomment to check for sensible values
        #print("Lat: %s" % latitude)
        #print("Long: %s" % longitude)

        # Latitude should be between -35 and -50 for NZ
        if -50 < latitude <-35:
            latList.append(latitude)
        else:
            # Just copy previous value
            latList.append(latList[-1])
        
        # Longitude should be between +165 and +180 for NZ
        if 165 < longitude < 180:
            longList.append(longitude)
        else:
            longList.append(longList[-1])

        # Add to the cleaned up CSV file
        writer.writerow([timeStamp, latitude, longitude, pitch, yaw, roll, accX, accY, accZ, gyroX, gyroY, gyroZ])


'''In the future this section will expand to include calcs of normal force'''
print(timeList[:10])

# Close files
inFile.close()
outFile.close()

# Subtitle time
shortTime = re.search("[0-9]+-[0-9]+-[0-9]+ [0-9]+:[0-9]+",timeList[0]).group()

# Calculate time gaps
# Format from arduIMU is YYYY-MM-DD HH:MM:SS.ddd"
timeFormat = "%Y-%m-%d %H:%M:%S.%f"
startTime = timeList[0]
stripTime = datetime.strptime(startTime, timeFormat)
datetimeList = [(datetime.strptime(x, timeFormat) - stripTime) for x in timeList] # produce a list of timedeltas
deltaList = [x.seconds + x.microseconds/float(1000000) for x in datetimeList] # produce a list of gaps


# Adjust roll values to be centred around zero rather than +- 180deg
adjRollList = []
for rollVal in rollList:
    if rollVal < 0:
        adjRollList.append(180+rollVal)
    else:
        adjRollList.append(180-rollVal)
        
adjPitchList = []
for pitchVal in pitchList:
    if pitchVal < 0:
        adjPitchList.append(180+pitchVal)
    else:
        adjPitchList.append(180-pitchVal)        
        
adjYawList = []
for yawVal in yawList:
    if yawVal < 0:
        adjYawList.append(180+yawVal)
    else:
        adjYawList.append(180-yawVal)

        
# Calculate average, range of values for each variable
avgDict = {
            "Roll": mean(adjRollList),
            "Yaw": mean(yawList),
            "Pitch": mean(pitchList),
            "AccX": mean(accXList),
            "AccY": mean(accYList),
            "AccZ": mean(accZList),
            "GyroX": mean(gyroXList),
            "GyroY": mean(gyroYList),
            "GyroZ": mean(gyroZList)
}

maxDict = {
            "Roll": max(adjRollList),
            "Yaw": max(yawList),
            "Pitch": max(pitchList),
            "AccX": max(accXList),
            "AccY": max(accYList),
            "AccZ": max(accZList),
            "GyroX": max(gyroXList),
            "GyroY": max(gyroYList),
            "GyroZ": max(gyroZList)
}

minDict = {
            "Roll": min(adjRollList),
            "Yaw": min(yawList),
            "Pitch": min(pitchList),
            "AccX": min(accXList),
            "AccY": min(accYList),
            "AccZ": min(accZList),
            "GyroX": min(gyroXList),
            "GyroY": min(gyroYList),
            "GyroZ": min(gyroZList)
}

rangeDict = {}
for key in maxDict.keys():
    rangeDict[key] = maxDict[key] - minDict[key]

print("Raw average")
print(avgDict)

# Re-centre data around mean value
# This fixes the weird offset values of some sensors
# But assumes the mean acceleration will be zero - which 
# should be true if we start and end at rest.
accXList = accXList - avgDict["AccX"]
accYList = accYList - avgDict["AccY"]
accZList = accZList - avgDict["AccZ"]

gyroXList = gyroXList - avgDict["GyroX"]
gyroYList = gyroYList - avgDict["GyroY"]
gyroZList = gyroZList - avgDict["GyroZ"]

# Modify pitch data
#pitchList = [x-17.4 for x in pitchList]

# Plotting
print("Plotting %s data points" % len(timeList))

# Line plot of roll/pitch/yaw
plt.plot(deltaList, pitchList, label='Pitch')
plt.plot(deltaList, adjRollList, label='Roll')
plt.plot(deltaList, adjYawList, label='Yaw')
plt.title("Pitch / Roll / Yaw", fontsize = 18) #  + "\n" + shortTime
plt.legend(loc=2)
plt.grid()
plt.xlabel("Time (seconds from start)")
plt.ylabel("Degrees")
plt.xlim(0,deltaList[-1])

# Line plot of linear accelerations
plt.figure()
plt.plot(deltaList, accZList, label='Z-Accel', alpha = 0.7)
plt.plot(deltaList, accYList, label='Y-Accel', alpha = 0.7)
plt.plot(deltaList, accXList, label='X-Accel', alpha = 0.7)
plt.title("Linear accelerations", fontsize = 18) #  + "\n" + shortTime
plt.legend(loc=2)
plt.grid()
plt.xlabel("Time (seconds from start)")
plt.ylabel("Acceleration")
plt.xlim(0,deltaList[-1])

# Line plot of rotational accelerations
plt.figure()
plt.plot(deltaList, gyroXList, label='X-Gyro', alpha = 0.7)
plt.plot(deltaList, gyroYList, label='Y-Gyro', alpha = 0.7)
plt.plot(deltaList, gyroZList, label='Z-Gyro', alpha = 0.7)
plt.title("Rotational accelerations", fontsize = 18) #  + "\n" + shortTime
plt.legend(loc=2)
plt.grid()
plt.xlabel("Time (seconds from start)")
plt.ylabel("Angular Acceleration")
plt.xlim(0,deltaList[-1])

'''
#import image as background for scatter plots
datafile = cbook.get_sample_data('trackmap.jpg')
img = imread(datafile)
'''

# GPS 2D scatter plot
# Coloured by the relevant variable

# EULER ANGLES
# Colouring by Pitch
plt.figure()
plt.scatter(longList, latList, s=100, c=pitchList, cmap="RdYlBu")
#plt.imshow(img, zorder=1) # Set background as a satellite image of track
plt.clim(-30,30)
plt.xlim(min(longList)-.001, max(longList)+.001)
plt.ylim(min(latList)-.001, max(latList)+.001)
ax = plt.gca()
ax.get_xaxis().get_major_formatter().set_useOffset(False)  # This stops the tick marks of the axes going to "relative offset" scaling
ax.get_yaxis().get_major_formatter().set_useOffset(False)
for tick in ax.get_xticklabels():
    tick.set_rotation(90)                 #turns the x-axis labels vertically
plt.title("Pitch variance", fontsize = 18) #  + "\n" + shortTime
plt.colorbar(label = "Pitch")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.grid()
plt.gcf().subplots_adjust(bottom=0.3)

# Colouring by Yaw
plt.figure()
plt.scatter(longList, latList, s=100, c=adjYawList, cmap="RdYlBu")
plt.clim(-100,100)
plt.xlim(min(longList)-.001, max(longList)+.001)
plt.ylim(min(latList)-.001, max(latList)+.001)
ax = plt.gca()
ax.get_xaxis().get_major_formatter().set_useOffset(False)  # This stops the tick marks of the axes going to "relative offset" scaling
ax.get_yaxis().get_major_formatter().set_useOffset(False)
for tick in ax.get_xticklabels():
    tick.set_rotation(90)                 #turns the x-axis labels vertically
plt.title("Yaw variance", fontsize = 18) #  + "\n" + shortTime
plt.colorbar(label = "Yaw")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.grid()
plt.gcf().subplots_adjust(bottom=0.3)

# Colouring by Roll
plt.figure()
plt.scatter(longList, latList, s=100, c=adjRollList, cmap="RdYlBu")
plt.clim(-90,90)
plt.xlim(min(longList)-.001, max(longList)+.001)
plt.ylim(min(latList)-.001, max(latList)+.001)
ax = plt.gca()
ax.get_xaxis().get_major_formatter().set_useOffset(False)  # This stops the tick marks of the axes going to "relative offset" scaling
ax.get_yaxis().get_major_formatter().set_useOffset(False)
for tick in ax.get_xticklabels():
    tick.set_rotation(90)                 #turns the x-axis labels vertically
plt.title("Roll variance", fontsize = 18) #  + "\n" + shortTime
plt.colorbar(label = "Roll")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.grid()
plt.gcf().subplots_adjust(bottom=0.3)

# LINEAR ACCELERATIONS
# Colouring by x-accel
plt.figure()
plt.scatter(longList, latList, s=100, c=accXList, cmap="RdYlBu")
plt.clim(-2000,2000)
plt.xlim(min(longList)-.001, max(longList)+.001)
plt.ylim(min(latList)-.001, max(latList)+.001)
ax = plt.gca()
ax.get_xaxis().get_major_formatter().set_useOffset(False)  # This stops the tick marks of the axes going to "relative offset" scaling
ax.get_yaxis().get_major_formatter().set_useOffset(False)
for tick in ax.get_xticklabels():
    tick.set_rotation(90)                 #turns the x-axis labels vertically
plt.colorbar(label = "AccX")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.grid()
plt.gcf().subplots_adjust(bottom=0.3)

# Colouring by y-accel
plt.figure()
plt.scatter(longList, latList, s=100, c=accYList, cmap="RdYlBu")
plt.clim(-4000,4000)
plt.xlim(min(longList)-.001, max(longList)+.001)
plt.ylim(min(latList)-.001, max(latList)+.001)
ax = plt.gca()
ax.get_xaxis().get_major_formatter().set_useOffset(False)  # This stops the tick marks of the axes going to "relative offset" scaling
ax.get_yaxis().get_major_formatter().set_useOffset(False)
for tick in ax.get_xticklabels():
    tick.set_rotation(90)                 #turns the x-axis labels vertically
plt.colorbar(label = "accY")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.grid()
plt.gcf().subplots_adjust(bottom=0.3)

# Colouring by z-accel
plt.figure()
plt.scatter(longList, latList, s=100, c=accZList, cmap="RdYlBu")
plt.clim(-5000,5000)
plt.xlim(min(longList)-.001, max(longList)+.001)
plt.ylim(min(latList)-.001, max(latList)+.001)
ax = plt.gca()
ax.get_xaxis().get_major_formatter().set_useOffset(False)  # This stops the tick marks of the axes going to "relative offset" scaling
ax.get_yaxis().get_major_formatter().set_useOffset(False)
for tick in ax.get_xticklabels():
    tick.set_rotation(90)                 #turns the x-axis labels vertically
plt.colorbar(label = "AccZ")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.grid()
plt.gcf().subplots_adjust(bottom=0.3)

# ROTATIONAL ACCELERATIONS
# Colouring by x-rot
plt.figure()
plt.scatter(longList, latList, s=100, c=gyroXList, cmap="RdYlBu")
plt.clim(-200,200)
plt.xlim(min(longList)-.001, max(longList)+.001)
plt.ylim(min(latList)-.001, max(latList)+.001)
ax = plt.gca()
ax.get_xaxis().get_major_formatter().set_useOffset(False)  # This stops the tick marks of the axes going to "relative offset" scaling
ax.get_yaxis().get_major_formatter().set_useOffset(False)
for tick in ax.get_xticklabels():
    tick.set_rotation(90)                 #turns the x-axis labels vertically
plt.colorbar(label = "GyroX")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.grid()
plt.gcf().subplots_adjust(bottom=0.3)

# Colouring by y-rot
plt.figure()
plt.scatter(longList, latList, s=100, c=gyroYList, cmap="RdYlBu")
plt.clim(-200,200)
plt.xlim(min(longList)-.001, max(longList)+.001)
plt.ylim(min(latList)-.001, max(latList)+.001)
ax = plt.gca()
ax.get_xaxis().get_major_formatter().set_useOffset(False)  # This stops the tick marks of the axes going to "relative offset" scaling
ax.get_yaxis().get_major_formatter().set_useOffset(False)
for tick in ax.get_xticklabels():
    tick.set_rotation(90)                 #turns the x-axis labels vertically
plt.colorbar(label = "GyroY")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.grid()
plt.gcf().subplots_adjust(bottom=0.3)

# Colouring by z-rot
plt.figure()
plt.scatter(longList, latList, s=100, c=gyroZList, cmap="RdYlBu")
plt.clim(-200,200)
plt.xlim(min(longList)-.001, max(longList)+.001)
plt.ylim(min(latList)-.001, max(latList)+.001)
ax = plt.gca()
ax.get_xaxis().get_major_formatter().set_useOffset(False)  # This stops the tick marks of the axes going to "relative offset" scaling
ax.get_yaxis().get_major_formatter().set_useOffset(False)
for tick in ax.get_xticklabels():
    tick.set_rotation(90)                 #turns the x-axis labels vertically
plt.colorbar(label = "gyroZ")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.grid()
plt.gcf().subplots_adjust(bottom=0.3)

# Display plots
plt.show()
