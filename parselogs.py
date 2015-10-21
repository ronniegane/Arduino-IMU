'''CSV data log processing for ArduIMU (Python 2.7)
Takes in CSV files of format Datastring, Timestamp
and extracts roll, pitch, yaw and other values
then plots these as a time series.'''

''' TO DO:
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
        # Check for sensible values
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


# Do magic to acceleration values to produce tyre forces

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
        
# Calculate average, range of values for various 
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

rangeDict = {}
for key in maxDict.keys():
    rangeDict[key] = maxDict[key] - minDict[key]

print("Raw average")
print(avgDict)

# Adjust data by mean value
accXList = accXList - avgDict["AccX"]
accYList = accYList - avgDict["AccY"]
accZList = accZList - avgDict["AccZ"]

gyroXList = gyroXList - avgDict["GyroX"]
gyroYList = gyroYList - avgDict["GyroY"]
gyroZList = gyroZList - avgDict["GyroZ"]


# Filter GPS data



# Plotting
print("Plotting %s data points" % len(timeList))

# Line plot of roll/pitch/yaw
plt.plot(deltaList, pitchList, label='Pitch')
plt.plot(deltaList, adjRollList, label='Roll')
plt.plot(deltaList, yawList, label='Yaw')
plt.title("Pitch / Roll / Yaw" + "\n" + shortTime, fontsize = 18)
plt.legend(loc=2)
plt.grid()
plt.xlabel("Time (seconds from start)")
plt.ylabel("Degrees")


# Line plot of linear accelerations
plt.figure()
plt.plot(deltaList, accZList, label='Z-Accel', alpha = 0.7)
plt.plot(deltaList, accYList, label='Y-Accel', alpha = 0.7)
plt.plot(deltaList, accXList, label='X-Accel', alpha = 0.7)
plt.title("Linear accelerations" + "\n" + shortTime, fontsize = 18)
plt.legend(loc=2)
plt.grid()
plt.xlabel("Time (seconds from start)")
plt.ylabel("Units?")

# Line plot of rotational accelerations
plt.figure()
plt.plot(deltaList, gyroXList, label='X-Gyro', alpha = 0.7)
plt.plot(deltaList, gyroYList, label='Y-Gyro', alpha = 0.7)
plt.plot(deltaList, gyroZList, label='Z-Gyro', alpha = 0.7)
plt.title("Rotational accelerations" + "\n" + shortTime, fontsize = 18)
plt.legend(loc=2)
plt.grid()
plt.xlabel("Time (seconds from start)")
plt.ylabel("Units?")




# Possible other plots:

# Line plot of velocity




# GPS 2D data plot, lat and long
# Colouring by other data
plt.figure()
plt.scatter(longList, latList, s=100, c=pitchList)
plt.clim(-20,50)
plt.xlim(min(longList)-.001, max(longList)+.001)
plt.ylim(min(latList)-.001, max(latList)+.001)
ax = plt.gca()
ax.get_xaxis().get_major_formatter().set_useOffset(False)  # This stops the tick marks of the axes going to "relative offset" scaling
ax.get_yaxis().get_major_formatter().set_useOffset(False)
plt.colorbar(label = "Pitch")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.grid()


plt.figure()
plt.scatter(longList, latList, s=100, c=yawList)

plt.xlim(min(longList)-.001, max(longList)+.001)
plt.ylim(min(latList)-.001, max(latList)+.001)
ax = plt.gca()
ax.get_xaxis().get_major_formatter().set_useOffset(False)  # This stops the tick marks of the axes going to "relative offset" scaling
ax.get_yaxis().get_major_formatter().set_useOffset(False)
plt.colorbar(label = "Yaw")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.grid()


plt.figure()
plt.scatter(longList, latList, s=100, c=adjRollList)
plt.clim(-20,50)
plt.xlim(min(longList)-.001, max(longList)+.001)
plt.ylim(min(latList)-.001, max(latList)+.001)
ax = plt.gca()
ax.get_xaxis().get_major_formatter().set_useOffset(False)  # This stops the tick marks of the axes going to "relative offset" scaling
ax.get_yaxis().get_major_formatter().set_useOffset(False)
plt.colorbar(label = "Roll")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.grid()

# Colouring by other data
plt.figure()
plt.scatter(longList, latList, s=100, c=accXList)
plt.clim(-2000,2000)
plt.xlim(min(longList)-.001, max(longList)+.001)
plt.ylim(min(latList)-.001, max(latList)+.001)
ax = plt.gca()
ax.get_xaxis().get_major_formatter().set_useOffset(False)  # This stops the tick marks of the axes going to "relative offset" scaling
ax.get_yaxis().get_major_formatter().set_useOffset(False)
plt.colorbar(label = "AccX")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.grid()


plt.figure()
plt.scatter(longList, latList, s=100, c=accYList)
plt.clim(-4000,4000)
plt.xlim(min(longList)-.001, max(longList)+.001)
plt.ylim(min(latList)-.001, max(latList)+.001)
ax = plt.gca()
ax.get_xaxis().get_major_formatter().set_useOffset(False)  # This stops the tick marks of the axes going to "relative offset" scaling
ax.get_yaxis().get_major_formatter().set_useOffset(False)
plt.colorbar(label = "accY")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.grid()


plt.figure()
plt.scatter(longList, latList, s=100, c=accZList)
plt.clim(-5000,5000)
plt.xlim(min(longList)-.001, max(longList)+.001)
plt.ylim(min(latList)-.001, max(latList)+.001)
ax = plt.gca()
ax.get_xaxis().get_major_formatter().set_useOffset(False)  # This stops the tick marks of the axes going to "relative offset" scaling
ax.get_yaxis().get_major_formatter().set_useOffset(False)
plt.colorbar(label = "AccZ")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.grid()

# Colouring by other data
plt.figure()
plt.scatter(longList, latList, s=100, c=gyroXList)
plt.clim(-200,200)
plt.xlim(min(longList)-.001, max(longList)+.001)
plt.ylim(min(latList)-.001, max(latList)+.001)
ax = plt.gca()
ax.get_xaxis().get_major_formatter().set_useOffset(False)  # This stops the tick marks of the axes going to "relative offset" scaling
ax.get_yaxis().get_major_formatter().set_useOffset(False)
plt.colorbar(label = "GyroX")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.grid()


plt.figure()
plt.scatter(longList, latList, s=100, c=gyroYList)
plt.clim(-200,200)
plt.xlim(min(longList)-.001, max(longList)+.001)
plt.ylim(min(latList)-.001, max(latList)+.001)
ax = plt.gca()
ax.get_xaxis().get_major_formatter().set_useOffset(False)  # This stops the tick marks of the axes going to "relative offset" scaling
ax.get_yaxis().get_major_formatter().set_useOffset(False)
plt.colorbar(label = "GyroY")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.grid()


plt.figure()
plt.scatter(longList, latList, s=100, c=gyroZList)
plt.clim(-200,200)
plt.xlim(min(longList)-.001, max(longList)+.001)
plt.ylim(min(latList)-.001, max(latList)+.001)
ax = plt.gca()
ax.get_xaxis().get_major_formatter().set_useOffset(False)  # This stops the tick marks of the axes going to "relative offset" scaling
ax.get_yaxis().get_major_formatter().set_useOffset(False)
plt.colorbar(label = "gyroZ")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.grid()

# Maybe colour by velocity? Where would we calculate velocity from?


plt.show()
