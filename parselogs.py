'''CSV data log processing for ArduIMU (Python 2.7)
Takes in CSV files of format Datastring, Timestamp
and extracts roll, pitch, yaw and other values
then plots these as a time series.'''

''' TO DO:
- Adjust to suit newer CSV format with GPU logs etc
'''

# Library imports
import matplotlib as mp # for plotting
import matplotlib.pyplot as plt 
import csv # reading and writing CSV files
import re # regular expressions


# Open file

# Hardcode filenames at first
myFile = 'Data for Session 1 - 1444208156913.csv'    # Change to desired input filename
outFile = open('cleaned data.csv', 'wb')             # Change to desired output filename

inFile = open(myFile, 'rb')
reader = csv.reader(inFile)


writer = csv.writer(outFile)
writer.writerow(["Time", "Pitch", "Yaw", "Roll", "AccX", "AccY", "AccZ", "GyroX", "GyroY", "GyroZ"]) # Headers

# Declaring variables
pitchList = []
rollList = []
yawList = []
countList = []
count = 0
timeList = []
accXList = []
accYList = []
accZList = []
gyroXList = []
gyroYList = []
gyroZList = []

# Close any open plots
plt.close("all")

# Loop through lines
for row in reader:
    ''' each row will be list [Datastring, timestamp]
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
    # print(row) # for testing
    # Record values to lists
    # Find index of the keyword
    startIndex = row[0].find('!!!')
    endIndex = row[0].find('***')
    if (startIndex > -1 and endIndex > startIndex): # makes sure we are only checking complete logs

        dataString = row[0]
        '''Timestamp'''
        timeStamp = row[1]
        timeList.append(row[1])
        
        '''Pitch'''
        pitch  = re.search("PCH:(-?[0-9]+.[0-9]+)", dataString).group(1)
        pitchList.append(float(pitch))

        '''Roll'''
        roll  = re.search("RLL:(-?[0-9]+.[0-9]+)", dataString).group(1)
        rollList.append(float(roll))

        '''Yaw'''
        yaw  = re.search("YAW:(-?[0-9]+.[0-9]+)", dataString).group(1)
        yawList.append(float(yaw))

        '''AccX'''
        accX  = re.search("AN3:(-?[0-9]+.[0-9]+)", dataString).group(1)
        accXList.append(float(accX))
        
        '''AccY'''
        accY  = re.search("AN4:(-?[0-9]+.[0-9]+)", dataString).group(1)
        accYList.append(float(accY))
        
        '''AccZ'''
        accZ  = re.search("AN5:(-?[0-9]+.[0-9]+)", dataString).group(1)
        accZList.append(float(accZ))   
        
        '''GyroX'''
        gyroX  = re.search("AN0:(-?[0-9]+.[0-9]+)", dataString).group(1)
        gyroXList.append(float(gyroX))
        
        '''GyroY'''
        gyroY  = re.search("AN1:(-?[0-9]+.[0-9]+)", dataString).group(1)
        gyroYList.append(float(gyroY))
        
        '''GyroZ'''
        gyroZ  = re.search("AN2:(-?[0-9]+.[0-9]+)", dataString).group(1)
        gyroZList.append(float(gyroZ))

        

        # Count of datapoints
        countList.append(count)
        count += 1

        # Add to the cleaned up CSV file
        writer.writerow([timeStamp, pitch, yaw, roll, accX, accY, accZ, gyroX, gyroY, gyroZ])

print(pitchList)
# Do magic to acceleration values to produce tyre forces

# Close files
inFile.close()
outFile.close()

# Plotting
print("Plotting %s data points" % len(countList))

# Line plot of roll/pitch/yaw
plt.plot(pitchList, label='Pitch')
plt.plot(rollList, label='Roll')
plt.plot(yawList, label='Yaw')
plt.title("Pitch / Roll / Yaw")
plt.legend(loc=2)
plt.ylabel("Degrees")
#plt.show()

# Line plot of linear accelerations
plt.figure()
plt.plot(accXList, label='X-Accel')
plt.plot(accYList, label='Y-Accel')
plt.plot(accZList, label='Z-Accel')
plt.title("Linear accelerations")
plt.legend(loc=2)
plt.ylabel("Units?")

# Line plot of rotational accelerations
plt.figure()
plt.plot(gyroXList, label='X-Gyro')
plt.plot(gyroYList, label='Y-Gyro')
plt.plot(gyroZList, label='Z-Gyro')
plt.title("Rotational accelerations")
plt.legend(loc=2)
plt.ylabel("Units?")

plt.show()

print(accYList[24:27])
# Line plot of velocity



# GPS 2D data plot, lat and long
# Maybe colour by velocity?


# Save plots and data as output file
