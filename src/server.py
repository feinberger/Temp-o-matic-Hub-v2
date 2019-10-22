"""server.py: This is the module to handle the python webserver functions

This python module is used to run the server side interactions and functions
that handle the websockets websever to interact with the client

Based off tutorial https://os.mbed.com/cookbook/Websockets-Server

Other Resources:
https://www.apptic.me/blog/getting-started-with-websockets-in-tornado.php
http://fabacademy.org/archives/2015/doc/WebSocketConsole.html

"""
import json
import datetime
import os

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler
from tornado.websocket import WebSocketHandler

from PyQt5.QtCore import QObject, QProcess

from src.dht_22 import DHT22Sensor
from src.database import TemperatureDatabase


class TempomaticWebServer:
    """ Class that handles the webserver functions and setup
    """

    def __init__(self):
        """ initializes the instance of the webserver class
        """
        # Create application
        self.application = Application([
            (r"/", MainHandler),
            (r"/(.*.css)", WebServerFileHandler),
            (r"/(.*.js)", WebServerFileHandler),
            (r'/ws', TempomaticHandler,)])

        # Create http server
        self.http_server = HTTPServer(self.application)

        # Server parameters
        self.port = 8888    # The port number http should listen on

        # System DHT22 Sensor
        self.temperature_sensor = DHT22Sensor(4)

    def start_server(self):
        """ Starts the http server for websockets
        """
        # Set server to listen to port 8888
        self.http_server.listen(self.port)

        # Start IO Loop
        IOLoop.instance().start()


class MainHandler(RequestHandler):
    """ Main handler for server html """

    def get(self):
        self.render("client/index.html")


class WebServerFileHandler(RequestHandler):
    """ Static file handler for web code in server """

    def get(self, static_file):        
        # Create url for static file
        static_url = "client/" + static_file
        self.render(static_url)


class TempomaticHandler(WebSocketHandler):
    """ Class that overrides the standard ws handler """

    def __init__(self, application, request, **kwargs):
        """ Overriding init method to add additional class elements """
        super().__init__(application, request, **kwargs)

        # Temperature sensor
        self.temperature_sensor = DHT22Sensor(4)

        # Parameters
        self.current_temperature = None
        self.current_humidity = None
        
        # System Database
        self.sys_db = TemperatureDatabase("TEST_DATABASE", "TEMP_MONITOR", "PASSWORD")

        # Get current start time for time elapsed
        self.start_time = datetime.datetime.now()

        # Wait for sensor to load
        # TODO: Fix this so the GUI doesn't lock while waiting for sensor
        while not self.temperature_sensor.sensor_initialized:
            self.temperature_sensor.initialize_sensor()

    def open(self):
        print("New Connection!")

    def on_message(self, message):
        # Debug message output
        print("New Message Received: {}".format(message))

        # Determine action from received message
        self.decode_message(message)

    def on_close(self):
        print("Closed Connection!")

    def check_origin(self, origin):
        print("Origin: {}".format(origin))
        return True

    def decode_message(self, message):
        """ Determines what action is required from the server """
        # Current readings request
        if message == "CR":
            print("Send Current Readings")
            current_reading = self.get_reading()
            if current_reading:
                self.send_current_readings(current_reading)
        # Previous stored readings request
        elif message == "NA":
            print("Get Network Activity")
            activity = self.get_network_activity()
            if activity:
                self.send_network_activity(activity)
        # Plot data request
        elif message == "PD":
            print("Send Plot Data")
            plot_data = self.get_plot_data()
            if plot_data:
                self.send_plot_data(plot_data)
        # Unknown request
        else:
            print("Unsupported message, nothing to do!")

    def get_reading(self):
        """ Get current temperature and humidity reading and update sensor status

        Returns: 
            dict: reading dict with temperature, humidity, and sensor status
        """
        # Reading Status
        current_reading = {}

        # Get reading
        result = self.temperature_sensor.get_current_reading()

        # Only update values if sensor is not busy
        if result["status"] == "Busy":
            current_reading['sensorStatus'] = "Busy"
        elif result["status"] == "Unavailable":
            current_reading['sensorStatus'] = "Read Error"
        elif result["status"] == "Offline":
            current_reading['sensorStatus'] = "Offline"
        else:
            current_reading['currentTemperature'] = "{:.1f}".format(result["temperature"])
            current_reading['currentHumidity'] = "{:.1f}".format(result["humidity"])
            current_reading['sensorStatus'] = "Ready"

        return current_reading

    def send_current_readings(self, msg):
        """ Sends serialized current temperature message to client """        

        # Send current data
        self.write_message(json.dumps(msg))

    def get_network_activity(self):
        """ Gets network activity status """
        # System Database
        self.sys_db = TemperatureDatabase("TEST_DATABASE", "TEMP_MONITOR", "PASSWORD")

        # Network Results JSON Obj (Dict)
        network_results = {}

        # Get Start Time
        start_time = datetime.datetime.now()

        # https://stackoverflow.com/questions/7588511/format-a-datetime-into-a-string-with-milliseconds
        network_results['starttime'] = start_time.strftime("%H:%M:%S.%f")[:-3]

        # Get Last 10 Humidity Readings
        last_readings = self.sys_db.get_last_measurements(10)

        if last_readings is not None:
            for idx, reading in enumerate(last_readings):
                dataset_key = "dataset{}".format(idx + 1)
                network_results[dataset_key] = reading[2]

            network_results["status"] = "Success"
        else:
            network_results["status"] = "Failure"


        # Get End Time
        end_time = datetime.datetime.now()

        # https://stackoverflow.com/questions/7588511/format-a-datetime-into-a-string-with-milliseconds
        network_results['endtime'] = end_time.strftime("%H:%M:%S.%f")[:-3]

        # Get Duration
        duration = end_time - start_time
        network_results["duration"] = "{:.1f}".format(duration.total_seconds() * 1000)
        
        # Add command
        network_results["command"] = "PythonNetwork"

        return network_results


    def send_network_activity(self, status):
        """ Sends network activity status """
        # Send network data
        self.write_message(json.dumps(status))

    def get_plot_data(self):
        """ Gets plot data for server """
        # System Database
        self.sys_db = TemperatureDatabase("TEST_DATABASE", "TEMP_MONITOR", "PASSWORD")

        # Plot Results JSON Obj (Dict)
        plot_data = {}

        # Get Last 10 Humidity Readings
        last_readings = self.sys_db.get_last_measurements(10)

        # Empty data list
        temperature_list = []
        humidity_list = []
        time_list = []

        if last_readings is not None:
            start_time = datetime.datetime.strptime(last_readings[0][3], "%m/%d/%y %X %p")
            
            for reading in last_readings:
                # Get elapsed time
                timestamp = datetime.datetime.strptime(reading[3], "%m/%d/%y %X %p")
                elapsed_time = (timestamp - start_time).total_seconds()
                time_list.append(elapsed_time)

                # Get temperature
                temperature_list.append(reading[1])

                # Get humidity
                humidity_list.append(reading[2])

                # Add status
                plot_data["status"] = "Success"
        else:
            # Add status
            plot_data["status"] = "Failure"
        
        # Add data
        plot_data["temperatures"] = temperature_list
        plot_data["times"] = time_list
        plot_data["humidities"] = humidity_list

        # Add command
        plot_data["command"] = "plotData"

        return plot_data

    def send_plot_data(self, outgoing_plot_data):
        """ Sends plot data to client """
        print(outgoing_plot_data)
        # Send plot data
        self.write_message(json.dumps(outgoing_plot_data))
        

def run_server():
    """ This is the test function to test functionality of the
    server class
    """
    print("Web Service!")

    # Create websockets server instance
    my_server = TempomaticWebServer()

    # Start server
    my_server.start_server()


if __name__ == "__main__":
    run_server()
