// Last edit Ronnie 18-10-15
// Commented out splitting into floats; just records raw datastream. IMU always powered on.
/*
 * TO DO: 
 * -Set titles for Logger.add() lines
 * -Fix ParseFloat not seeming to work. May need to be Serial.parseFloat() and may be designed to work with
 *    serial streams rather than strings
 * -Change all record values to floats, not ints
 * -Check that logger loop can access the Roll, Pitch etc variable after they're changed in decode()
 */


#define CUSTOM_SETTINGS
#define INCLUDE_TERMINAL_SHIELD
#define INCLUDE_DATA_LOGGER_SHIELD
#define INCLUDE_GPS_SHIELD

#include <OneSheeld.h>
#include <SoftwareSerial.h>


/*
 * Pin Mapping for ArduIMU directly connected:
 * BLK = Pin 2
 * GND = Pin 3
 * 5V = Pin 4
 * RX = Pin 5
 * TX = Pin 6
 * GRN = Pin 7
 */

// declaring variables
String nextLine;
SoftwareSerial mySerial(6,5);                   // RX, TX pins
String titleBase = "Data for Session ";
int sessionNo = 1;
String title;
bool startFlag = false;
int gndPin = 3;                                   // IMU ground
int pwrPin = 4;                                   // IMU power
int pwrButton = 10;                               // Set OneSheeld Toggle Button to pin 10 (assign in app also)
float latitude;
float longitude;
//int Roll;
//int Pitch;
//int Yaw;
//int GyrX;
//int GyrY;
//int GyrZ;
//int AccX;
//int AccY;
//int AccZ;


void setup() {
  OneSheeld.begin();
  pinMode(pwrButton, INPUT);
  pinMode(gndPin, OUTPUT);
  pinMode(pwrPin, OUTPUT);
  sessionNo = 1;
  // ground the IMU
  digitalWrite(gndPin, LOW);
  digitalWrite(pwrPin, HIGH);
  
  mySerial.begin(38400);                          // Set data rate for software serial port
  Terminal.println("Serial connected.");
  Terminal.println("To start, press the power button (pin 10)");
//Logger.stop();                                  // Stops the logger if it was previously running, and saves any old values
}

void loop() {


  if(digitalRead(pwrButton)==HIGH){
    
    //digitalWrite(pwrPin, HIGH);                   // Power on IMU
    //Terminal.println("IMU on");                   // Print 'ON' notification
    
    title = titleBase + sessionNo;                // Assign a new title for this session
    Terminal.println(title);                      // Check the title by printing it to terminal
    Logger.start(title);                          // Open new CSV file with this title
//    Logger.add(title, "Roll");                    // Assign column headings to file:
//    Logger.add(title, "Pitch");
//    Logger.add(title, "Yaw");
//    Logger.add(title, "GyrX");
//    Logger.add(title, "GyrY");
//    Logger.add(title, "GyrZ");
//    Logger.add(title, "AccX");
//    Logger.add(title, "AccY");
//    Logger.add(title, "AccZ");
    //Logger.add(title, "GPS Lat");
    //Logger.add(title, "GPS Long");
    
    Logger.log();
    
    startFlag = true;                             // Set flag to start logging
  }
 
  while(startFlag){
    
    if (mySerial.available()>0){                  // Get data stream from IMU.
      latitude = GPS.getLatitude();
      longitude = GPS.getLongitude();
      nextLine = mySerial.readStringUntil('\n');  // Save the current line (up until line end marker of '/n' to the vairable 'nextLine'
//      decode(nextLine);                         // Call 'decode' function to parse the data into variables (defined below)
//      Logger.add(title, Roll);                  // Add data variables to log file
//      Logger.add(title, Pitch);
//      Logger.add(title, Yaw);
//      Logger.add(title, GyrX);
//      Logger.add(title, GyrY);
//      Logger.add(title, GyrZ);
//      Logger.add(title, AccX);
//      Logger.add(title, AccY);
//      Logger.add(title, AccZ);
      Logger.add("Data", nextLine);
      Logger.add("Latitude", latitude);           //Add GPS coordinates to file
      Logger.add("Longitude", longitude);
      Logger.log();                               // Save current line, move to next
      //OneSheeld.delay(100);                     // Delay for 100ms - can adjust if nec.
    }

    if(digitalRead(pwrButton)==LOW){
      //digitalWrite(pwrPin, LOW);                  // Power down IMU
      Terminal.println("Logging ended.");
      Logger.stop();
      sessionNo += 1;
      startFlag = false;
    }
  }
  
  
  
}

//String decode(String DataString) 
//{
//  float tmpFloat=-9999;
//  int tmpInt=-9999;
//  int StartIdx = DataString.indexOf("!!!");
//  int EndIdx = DataString.indexOf("***");
//  if(StartIdx>-1 && EndIdx>StartIdx)
//  {
//    tmpFloat = Find_Float(DataString,"RLL:"); 
//    if (tmpFloat!=-9999) Roll=tmpFloat;           //Do we need to put an 'else = 0' in these? 
//
//    tmpFloat = Find_Float(DataString,"PCH:"); 
//    if (tmpFloat!=-9999) Pitch=tmpFloat;
//
//    tmpFloat = Find_Float(DataString,"YAW:"); 
//    if (tmpFloat!=-9999) Yaw=tmpFloat;
//
//    tmpFloat = Find_Float(DataString,"AN1:"); 
//    if (tmpFloat!=-9999) GyrX=tmpFloat;
//
//    tmpFloat = Find_Float(DataString,"AN2:"); 
//    if (tmpFloat!=-9999) GyrY=tmpFloat;
//
//    tmpFloat = Find_Float(DataString,"AN3:"); 
//    if (tmpFloat!=-9999) GyrZ=tmpFloat;
//
//    tmpFloat = Find_Float(DataString,"AN3:"); 
//    if (tmpFloat!=-9999) AccX=tmpFloat;
//
//    tmpFloat = Find_Float(DataString,"AN4:"); 
//    if (tmpFloat!=-9999) AccY=tmpFloat;
//
//    tmpFloat = Find_Float(DataString,"AN5:"); 
//    if (tmpFloat!=-9999) AccZ=tmpFloat;
//
//    return("");
//  }
//  return("");
//}
//
//float Find_Float(String theString,String theTarget)
//{
//  int targetIdx = theString.indexOf(theTarget)+theTarget.length();
//  int CommaIdx = theString.indexOf(",",targetIdx);
//  if (CommaIdx <0) CommaIdx = theString.indexOf("*",targetIdx);
//  if(targetIdx>-1 && CommaIdx>targetIdx)
//    return (parseFloat(theString.substring(targetIdx,CommaIdx)));
//  else
//    return(-9999);
//}


