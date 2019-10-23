# Temp-o-Matic-Hub V2
This is an upgraded, upgraded version of the temp-o-matic application that includes web server abilities to allow for clients to connect to device besides the on-board application GUI. Temp-o-matic is a prototype application used to monitor and record humidity and temperature with a Raspberry Pi 3 B+ and a DHT22 temperature and humidity sensor as well as AWS features for SNS Alerts and Queuing. **This was developed by Glenn Feinberg** for ECEN 5783. Please use this application at your own risk.

## Installation
1. Get source code:
```sh
$ git clone https://github.com/feinberger/Temp-o-Matic-Hub-v2.git
```
2. Install pyqt requirements
```sh
$ sudo apt-get install qt5-default pyqt5-dev pyqt5-dev-tools
$ sudo apt-get install qttools5-dev-tools
```
3. Install python dependencies
```sh
$ python3 -m pip install -r requirements.txt
```
4. Install node dependencies
```sh
$ npm install mysql2 mysql async websocket
```
5. Navigate to local folder and run application. This starts both servers and the on-board GUI.
```sh
$ python3 main.py
```

## Project Work

### Local GUI (pyqt)
 - Sensor status - displays whether the sensor is ready, busy (2 second read time), or disconnected (3 failed readings in a row)
 - System Status - Displays Good, Over Temperature, Over Humidity, Over Temperature and Humidity warning errors
 - Allows user to set over temperature and over humidity alarms
 - Plots humidity and temperature (up to 10 values) on the plot image
 - Displays last read temperature and humidity values in monitor box and time read. 
 - Now button to get current readings
 - Ability to toggle degree C or degree F with toggle switch
 - Ability to toggle on and off logging with a single switch
 - Internal timer to read DHT22 sensor no fater then 2 seconds
 - One, dual y-axis plot for the temperature and humidity
 - Ability to enable/disable temperature and humidity curves
 - Pyqtgraph usage - this was given pre-approval by Professor Montogomery ahead of time

 ### Webclient GUI
 - Current readings monitor with humidity, temperature, and status via Python Webserver
 - Temperature conversion - converts current, previous, and plots to either C or F
 - Table view of up to 20 SQS Messages displaying Temp, Humidity, and Timestamp

 ## Additional Features
 - Web GUI is able to monitor the SQS Count

 ## Error Checks
 - Checks for the Tornado webservers are connected, otherwise alerts user
 - Verifies there is data in database before trying to access data
 - Checks sensor status and reports to user
 - Warns user plots are not available without any current data
 - Checks for empty SQS queue

## Project Issues
- AWS SQS and Javascript connectivity was a challenge (especially with Javascript)
- AWS has a very poor online editor, no revision control, etc. 
