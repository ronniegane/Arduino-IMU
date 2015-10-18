'''CSV data log processing for ArduIMU (Python 2.7)
Takes in CSV files of format Datastring, Timestamp
and extracts roll, pitch, yaw and other values
then plots these as a time series.'''

''' TO DO:
- Add table for Max/Min/Range/Average/Standard dev for various sensors
- Make try/except more sensible
- Filter GPS data: some points have latitude = longitude
- Math/physics magic to transform our X,Y,Z into the vehicle's coordinate system
- Math/physics magic to work out tyre forces
'''

# Library imports
import matplotlib as mp                 # for plotting
import matplotlib.pyplot as plt         # more plotting
import csv                              # reading and writing CSV files
import re                               # regular expressions for searching strings
from datetime import datetime           # for dealing with time values


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
            pitch  = re.search("PCH:(-?[0-9]+.[0-9]+)", dataString).group(1)
            pitchList.append(float(pitch))
        except:
            pitchList.append(pitchList[-1])

        '''Roll'''
        try:
            roll  = re.search("RLL:(-?[0-9]+.[0-9]+)", dataString).group(1)
            rollList.append(float(roll))
        except:
            rollList.append(rollList[-1])

        '''Yaw'''
        try:
            yaw  = re.search("YAW:(-?[0-9]+.[0-9]+)", dataString).group(1)
            yawList.append(float(yaw))
        except:
            yawList.append(yawList[-1])        

        '''AccX'''
        try:
            accX  = re.search("AN3:(-?[0-9]+.[0-9]+)", dataString).group(1)
            accXList.append(float(accX))
        except:
            accXList.append(accXList[-1])        
        
        '''AccY'''
        try:
            accY  = re.search("AN4:(-?[0-9]+.[0-9]+)", dataString).group(1)
            accYList.append(float(accY))
        except:
            accYList.append(accYList[-1])        
        
        '''AccZ'''
        try:
            accZ  = re.search("AN5:(-?[0-9]+.[0-9]+)", dataString).group(1)
            accZList.append(float(accZ))
        except:
            accZList.append(accZList[-1])        
        
        '''GyroX'''
        try:
            gyroX  = re.search("AN0:(-?[0-9]+.[0-9]+)", dataString).group(1)
            gyroXList.append(float(gyroX))
        except:
            gyroXList.append(gyroXList[-1])            
        
        '''GyroY'''
        try:
            gyroY  = re.search("AN1:(-?[0-9]+.[0-9]+)", dataString).group(1)
            gyroYList.append(float(gyroY))
        except:
            gyroYList.append(gyroYList[-1])        
        
        '''GyroZ'''
        try:
            gyroZ  = re.search("AN2:(-?[0-9]+.[0-9]+)", dataString).group(1)
            gyroZList.append(float(gyroZ))
        except:
            gyroZList.append(gyroZList[-1])
            
            

        '''GPS'''
        latitude = row[2]
        longitude = row[3]
        latList.append(latitude)
        longList.append(longitude)

        # Add to the cleaned up CSV file
        writer.writerow([timeStamp, latitude, longitude, pitch, yaw, roll, accX, accY, accZ, gyroX, gyroY, gyroZ])


# Do magic to acceleration values to produce tyre forces

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


print(deltaList[:30])


# Plotting
print("Plotting %s data points" % len(timeList))

# Line plot of roll/pitch/yaw
plt.plot(deltaList, pitchList, label='Pitch')
plt.plot(deltaList, rollList, label='Roll')
plt.plot(deltaList, yawList, label='Yaw')
plt.title("Pitch / Roll / Yaw" + "\n" + shortTime, fontsize = 18)
plt.legend(loc=2)
plt.grid()
plt.xlabel("Time (seconds from start)")
plt.ylabel("Degrees")


# Line plot of linear accelerations
plt.figure()
plt.plot(deltaList, accXList, label='X-Accel')
plt.plot(deltaList, accYList, label='Y-Accel')
plt.plot(deltaList, accZList, label='Z-Accel')
plt.title("Linear accelerations" + "\n" + shortTime, fontsize = 18)
plt.legend(loc=2)
plt.grid()
plt.xlabel("Time (seconds from start)")
plt.ylabel("Units?")

# Line plot of rotational accelerations
plt.figure()
plt.plot(deltaList, gyroXList, label='X-Gyro')
plt.plot(deltaList, gyroYList, label='Y-Gyro')
plt.plot(deltaList, gyroZList, label='Z-Gyro')
plt.title("Rotational accelerations" + "\n" + shortTime, fontsize = 18)
plt.legend(loc=2)
plt.grid()
plt.xlabel("Time (seconds from start)")
plt.ylabel("Units?")




# Possible other plots:

# Line plot of velocity


# GPS 2D data plot, lat and long
## plt.figure()
## plt.scatter(latList,longList)


# Maybe colour by velocity?


plt.show()
