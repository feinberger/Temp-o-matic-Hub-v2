"""dht_22.py: This is the python module for functions relating to the DHT22 Sensor

This python module is used to interface with the DHT22 sensor from Adafruit. It contains
the necessary functions to read the temperature, intialize the sensor, check the status of
the sensor, and temperature conversion functions

"""

import datetime

import Adafruit_DHT

# Temperature/Humidity Min/Max (in celsius) from https://www.sparkfun.com/datasheets/Sensors/Temperature/DHT22.pdf
DHT22_MAXIMUM_TEMPERATURE = 80
DHT22_MINIMUM_TEMPERATURE = -40
DHT22_MAXIMUM_HUMIDITY = 100
DHT22_MINIMUM_HUMIDITY = 0


class DHT22Sensor:
    """ DHT22_Sensor: a class built for the DHT22 Temperature Sensor
    """

    def __init__(self, pin, sensor=Adafruit_DHT.DHT22):
        """Returns a the main window of the temp-o-matic application.

        Args:
            pin (int): GPIO Pin on the Raspberry Pi
            sensor(str): DHT22 Sensor Type
        """
        self.pin_number = pin
        self.sensor = sensor
        self.last_reading_time = datetime.datetime.now()
        self.sensor_initialized = False

        # Sensor Status (Warming up, Offline, Ready, Busy)
        self.sensor_status = "Warming Up"

        # Offline count - sensor deemed offline when 3 consecutive failed reads occur
        self.offline_count = 0

    def initialize_sensor(self):
        """Initializes sensor by checking 2 seconds has passed before creation of class
        """
        # Get elapsed time
        current_time = datetime.datetime.now()
        elapsed_time = (current_time - self.last_reading_time).total_seconds()

        # Sensor is initialized after 2 seconds of class creation
        if elapsed_time > 2:
            self.sensor_initialized = True

    def get_current_reading(self):
        """ Function to get the current reading of the dht22 sensor

        Returns:
            dict: dictionary with keys ('status', 'timestamp', 'temperature', 'humidity') that
            are the results of the current read

            status - status of the sensor device
            timestamp - timestamp of the measurement
            temperature - temperature reading in celsius
            humidity - humidity percentage
        """

        # Results dictionary (status, humidity, temperature)
        results = {
            "status": None,
            "timestamp": None,
            "temperature": None,
            "humidity": None,
        }

        # Get elapsed time
        current_time = datetime.datetime.now()
        elapsed_time = (current_time - self.last_reading_time).total_seconds()

        # Only get new data if 2 seconds has passed
        if elapsed_time > 2:
            # Get reading from sensor
            humidity, temperature = Adafruit_DHT.read(self.sensor, self.pin_number)

            # Return results if available (occurs somewhat randomly when data not available)
            if (humidity is not None) and (temperature is not None):
                # Set last reading time
                self.last_reading_time = datetime.datetime.now()

                # Store results
                results["status"] = "New"
                results["timestamp"] = self.last_reading_time.strftime("%m/%d/%y %X")
                results["temperature"] = temperature
                results["humidity"] = humidity

                # Set device status
                self.sensor_status = "Ready"

                # Clear offline count
                self.offline_count = 0
            else:
                # Try once more for a successful read
                humidity, temperature = Adafruit_DHT.read(self.sensor, self.pin_number)

                # Return results if available (occurs somewhat randomly when data not available)
                if (humidity is not None) and (temperature is not None):
                    # Set last reading time
                    self.last_reading_time = datetime.datetime.now()

                    # Store results
                    results["status"] = "New"
                    results["timestamp"] = self.last_reading_time.strftime("%m/%d/%y %X")
                    results["temperature"] = temperature
                    results["humidity"] = humidity

                    # Set device status
                    self.sensor_status = "Ready"

                    # Clear offline count
                    self.offline_count = 0
                else:
                    # Offline count reaches 3, sensor is offline
                    if self.offline_count >= 3:
                        self.sensor_status = "Offline"
                        results["status"] = "Offline"
                    else:
                        self.offline_count += 1
                        results["status"] = "Unavailable"
        else:
            if self.sensor_status == "Warming Up":
                results["status"] = "Warming Up"
            else:
                self.sensor_status = "Busy"
                results["status"] = "Busy"

        return results


def celsius_to_fahrenheit(temperature):
    """ Converts celsius temperature to fahrenheit temperature
    Args:
        temperature (float): temperature in degrees celsius

    Returns:
        float: Temperature in degrees fahrenheit
    """
    return temperature * (9.0 / 5.0) + 32


def fahrenheit_to_celsius(temperature):
    """ Converts fahrenheit temperature to celsius temperature
    Args:
        temperature (float): temperature in degrees fahrenheit

    Returns:
        float: Temperature in degrees celsius
    """
    return (temperature - 32) * (5.0 / 9.0)
