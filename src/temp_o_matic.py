"""temp_o_matic.py: This is the python module for functions relating to the UI for temp-o-matic.

This python module is used to interface with the python converted code from the .ui file designed in
QT Designer. This contains the objects and functions required to interface with the GUI that
displays the temperature and humidity and the corresponding plots and settings to go with the
application.

"""
import sys

from PyQt5.QtWidgets import QMainWindow, QPushButton, QApplication
from PyQt5.QtCore import QTimer

from src.database import TemperatureDatabase
from src.dht_22 import (
    DHT22_MAXIMUM_HUMIDITY,
    DHT22_MAXIMUM_TEMPERATURE,
    DHT22_MINIMUM_HUMIDITY,
    DHT22_MINIMUM_TEMPERATURE,
    DHT22Sensor,
    celsius_to_fahrenheit,
    fahrenheit_to_celsius,
)
from src.ui.tempomatic import Ui_MainWindow


class MainWindow(QMainWindow):
    """MainWindow: a class that is the main object for main screen ui"""

    def __init__(self, sensor_type="DHT_22"):
        """Returns a the main window of the temp-o-matic application.

        Args:
            sensor (str): Temperature/Humidity Sensor Type
        """
        super(MainWindow, self).__init__()

        # Initialize and Setup UI from converted .ui
        self.screen_ui = Ui_MainWindow()
        self.screen_ui.setupUi(self)

        # System Parameters
        self.system_temp_setting = "Celsius"  # System units for temperature
        self.temp_unit = "°C"  # Temperature Unit String
        self.humidity_unit = "%"  # Humidity in percentage
        self.logging_status = False
        self.sensor_type = sensor_type  # Type of humidity/temp sensor
        self.maximum_temperature = None  # Maximum temperature of sensor
        self.minimum_temperature = None  # Minimum temperature of sensor
        self.maximum_humidity = None  # Maximum humidity of sensor
        self.minimum_humidity = None  # Minimum humidity of sensor
        self.alarm_temperature_high = 28  # Alarm over-temperature
        self.alarm_temperature_low = 0  # Alarm under-temperature
        self.alarm_humidity_high = 80  # Alarm humidity max limit
        self.alarm_humidity_low = 15  # Alarm humidity min limit
        self.converting_flag = False  # Flag indicating conversion in place
        self.plot_temp_flag = True   # Flag indicating plot state of temperature
        self.plot_humidity_flag = True  # Flag indicating plot state of humidity

        # Logging Timer Parameters
        self.logging_timer = None  # logging timer object
        self.logging_interval_ms = 15000  # 15 second logging intervals in ms
        self.logging_count = 0  # Current running tally of logged measurements
        self.max_logging_count = 30  # Max number of current logs before stopping

        # System DHT22 Sensor
        self.temperature_sensor = DHT22Sensor(4)

        # System database
        self.sys_db = TemperatureDatabase("TEST_DATABASE", "TEMP_MONITOR", "PASSWORD")
        self.sys_db.create_table()

        # System plot
        self.plot = self.screen_ui.plot

        # System display
        self.temperature_display = "-"
        self.humidity_display = "-"
        self.last_time_read = "-"

        # Initialize screen to start up settings
        self.initialize_screen()

        # Configure signal events
        # Temperature alarm changed
        self.screen_ui.temp_alarm.valueChanged.connect(self.update_temperature_alarm)

        # Humidity alarm changed
        self.screen_ui.humidity_alarm.valueChanged.connect(self.update_humidity_alarm)

        # Temperature units change
        self.screen_ui.temp_units.toggled.connect(self.update_temperature_units)

        # Logging switch toggled
        self.screen_ui.logging_switch.toggled.connect(self.configure_logging)

        # Plot Button Pressed
        self.screen_ui.plot_button.pressed.connect(self.update_plot)

        # Read Button Pressed
        self.screen_ui.current_reading_button.pressed.connect(self.get_reading)

        # Temperature Plot Option Toggled
        self.screen_ui.temp_plot_switch.toggled.connect(self.update_temp_curve)

        # Humidity Plot Option Toggled
        self.screen_ui.humid_plot_switch.toggled.connect(self.update_humidity_curve)

    def initialize_screen(self):
        """Initializes the screen widgets to start-up values and settings
        """
        # Initialize initial readings and timestamp
        self.screen_ui.temp_reading.setText("-" + self.temp_unit)
        self.screen_ui.humidity_reading.setText("-%")
        self.screen_ui.timestamp.setText("-")

        # Initialize system max/min settings
        if self.sensor_type == "DHT_22":
            self.maximum_temperature = DHT22_MAXIMUM_TEMPERATURE
            self.minimum_temperature = DHT22_MINIMUM_TEMPERATURE
            self.maximum_humidity = DHT22_MAXIMUM_HUMIDITY
            self.minimum_humidity = DHT22_MINIMUM_HUMIDITY

        # Initialize Alarm settings (assumes celsisus at start)
        self.set_alarm_settings()

        # Set system statuses
        self.screen_ui.system_status.setText("<font color='forestgreen'>Good</font>")
        self.screen_ui.sensor_status.setText("<font color='goldenrod'>Loading</font>")

        # Initialize both plot curves to on
        self.screen_ui.temp_plot_switch.setChecked(True)
        self.screen_ui.humid_plot_switch.setChecked(True)

        # Wait for sensor to load
        # TODO: Fix this so the GUI doesn't lock while waiting for sensor
        while not self.temperature_sensor.sensor_initialized:
            self.temperature_sensor.initialize_sensor()
        self.screen_ui.sensor_status.setText("<font color='forestgreen'>Ready</font>")

    def update_temperature_alarm(self):
        """ Updates the temperature alarm setting
        """
        if not self.converting_flag:
            self.alarm_temperature_high = self.screen_ui.temp_alarm.value()
            temperature_text = "{0:.1f}{1}".format(
                self.alarm_temperature_high, self.temp_unit
            )
            self.screen_ui.temp_alarm_setting.setText(temperature_text)
            self.check_alarms()

    def update_humidity_alarm(self):
        """ Updates the temperature alarm setting
        """
        self.alarm_humidity_high = self.screen_ui.humidity_alarm.value()
        self.screen_ui.humidity_alarm_setting.setText(
            str(self.alarm_humidity_high) + self.humidity_unit
        )
        self.check_alarms()

    def update_temperature_units(self):
        """ Determines/toggles the system temperature units
        """
        if self.system_temp_setting == "Celsius":
            self.system_temp_setting = "Fahrenheit"
            self.convert_to_fahrenheit()
        elif self.system_temp_setting == "Fahrenheit":
            self.system_temp_setting = "Celsius"
            self.convert_to_celsius()
        else:
            print("Bad Temperature Unit")

    def convert_to_fahrenheit(self):
        """ Converts the system ui and settings to degrees fahrenheit
        """
        # Set converting flag
        self.converting_flag = True

        # Update system units
        self.temp_unit = "°F"

        # Update temperature readings
        if self.temperature_display == "-":
            # Only update units if system isn't running
            self.screen_ui.temp_reading.setText("-" + self.temp_unit)
        else:
            self.temperature_display = "{:.1f}".format(
                celsius_to_fahrenheit(float(self.temperature_display))
            )
            self.set_temperature_display()

        # Update temperature alarm and settings
        self.alarm_temperature_high = celsius_to_fahrenheit(self.alarm_temperature_high)
        self.maximum_temperature = celsius_to_fahrenheit(self.maximum_temperature)
        self.minimum_temperature = celsius_to_fahrenheit(self.minimum_temperature)
        self.set_alarm_settings()
        self.check_alarms()

        # Update plot
        self.plot.convert_to_fahrenheit()

        # Reset converting flag
        self.converting_flag = False

    def convert_to_celsius(self):
        """ Converts the system ui and settings to degrees celsius
        """
        # Set converting flag
        self.converting_flag = True

        # Update system units
        self.temp_unit = "°C"

        # Update temperature readings
        if self.temperature_display == "-":
            # Only update units if system isn't running
            self.screen_ui.temp_reading.setText("-" + self.temp_unit)
        else:
            self.temperature_display = "{:.1f}".format(
                fahrenheit_to_celsius(float(self.temperature_display))
            )
            self.set_temperature_display()

        # Update temperature alarm and settings
        self.alarm_temperature_high = fahrenheit_to_celsius(self.alarm_temperature_high)
        self.maximum_temperature = fahrenheit_to_celsius(self.maximum_temperature)
        self.minimum_temperature = fahrenheit_to_celsius(self.minimum_temperature)
        self.set_alarm_settings()
        self.check_alarms()

        # Update plot
        self.plot.convert_to_celsius()

        # Reset converting flag
        self.converting_flag = False

    def set_alarm_settings(self):
        """Configures the alarm slider settings and current value
        """
        self.screen_ui.temp_alarm.setMaximum(self.maximum_temperature)
        self.screen_ui.temp_alarm.setMinimum(self.minimum_temperature)
        self.screen_ui.humidity_alarm.setMaximum(self.maximum_humidity)
        self.screen_ui.humidity_alarm.setMinimum(self.minimum_humidity)

        # Set initial alarm to reasonable standard settings
        temperature_text = "{0:.1f}{1}".format(
            self.alarm_temperature_high, self.temp_unit
        )
        self.screen_ui.temp_alarm_setting.setText(temperature_text)
        self.screen_ui.temp_alarm.setValue(self.alarm_temperature_high)
        self.screen_ui.humidity_alarm_setting.setText(
            str(self.alarm_humidity_high) + self.humidity_unit
        )
        self.screen_ui.humidity_alarm.setValue(self.alarm_humidity_high)

    def get_reading(self):
        """ Get current temperature and humidity reading and update sensor status

        Returns: 
            bool: If reading was successfully captured
        """
        # Reading Status
        reading_status = False

        # Get reading
        result = self.temperature_sensor.get_current_reading()

        # Only update values if sensor is not busy
        if result["status"] == "Busy":
            self.screen_ui.sensor_status.setText("<font color='goldenrod'>Busy</font>")
        elif result["status"] == "Unavailable":
            self.screen_ui.sensor_status.setText("<font color='red'>Read Error</font>")
        elif result["status"] == "Offline":
            self.screen_ui.sensor_status.setText("<font color='red'>Offline</font>")
        else:
            self.screen_ui.sensor_status.setText("<font color='green'>Ready</font>")
            if self.system_temp_setting == "Celsius":
                self.temperature_display = "{:.1f}".format(result["temperature"])
            else:
                # Convert reading to fahrenehit because celsius by default
                self.temperature_display = "{:.1f}".format(
                    celsius_to_fahrenheit(result["temperature"])
                )
            self.humidity_display = "{:.1f}".format(result["humidity"])
            self.last_time_read = "{}".format(result["timestamp"])

            # Check for alarm warnings
            self.check_alarms()

            self.set_temperature_display()

            # Successful read
            reading_status = True

        return reading_status

    def check_alarms(self):
        """ Checks alarm statuses and updates system status
        """
        # Check for alarm warnings, ignore if no readings
        if self.temperature_display == "-" or self.humidity_display == "-":
            pass
        else:
            if float(self.temperature_display) > self.alarm_temperature_high:
                # Over temperature warning
                if float(self.humidity_display) > self.alarm_humidity_high:
                    # Over humidity warning
                    self.screen_ui.system_status.setText(
                        "<font color='red'>Temp and Humidity Err</font>"
                    )
                else:
                    self.screen_ui.system_status.setText(
                        "<font color='red'>Temp Err</font>"
                    )
            else:
                if float(self.humidity_display) > self.alarm_humidity_high:
                    # Over humidity warning
                    self.screen_ui.system_status.setText(
                        "<font color='red'>Humidity Err</font>"
                    )
                else:
                    self.screen_ui.system_status.setText(
                        "<font color='forestgreen'>Good</font>"
                    )

    def set_temperature_display(self):
        """Function to update the temperature monitor display
        """
        self.screen_ui.temp_reading.setText(self.temperature_display + self.temp_unit)
        self.screen_ui.humidity_reading.setText(
            self.humidity_display + self.humidity_unit
        )
        self.screen_ui.timestamp.setText(self.last_time_read)

    def update_plot(self):
        """ Initiaze plotting function for the temperature and humidity
        """
        # Get last 10 measurements
        values = self.sys_db.get_last_measurements(10)
        
        # Measurement groups
        temperatures = []
        humidities = []
        timestamps = []

        # Group measurement data to pass to plot
        if values is not None:
            for reading in values:
                # Convert tuple reading to list
                reading_list = list(reading)

                # Add each item to corresponding group
                # id - item 0, temp - item 1, humidity - item 2, time = item 3
                temperatures.append(reading_list[1])
                humidities.append(reading_list[2])
                timestamps.append(reading_list[3])

            # Send data to plot function
            self.plot.update_values(temperatures, humidities, timestamps)


    def configure_logging(self):
        """Toggles the logging functionality of the application
        """
        if self.logging_status:
            # Stop and delete logging timer
            if self.logging_timer:
                self.logging_timer.stop()

            # Set logging switch off
            self.screen_ui.logging_switch.setChecked(False)
            self.screen_ui.logging_switch.set_switch_off()

            # Clear logging count to 0
            self.logging_count = 0

            # Set logging status to false
            self.logging_status = False

        else:
            self.logging_status = True

            # Start logging
            self.start_logging_timer()

    def start_logging_timer(self):
        """ Function to start logging timer
        """
        # if timer exists stop and delete timer
        if self.logging_timer:
            self.logging_timer.stop()

        # Create QTimer for logging interval
        self.logging_timer = QTimer()
        self.logging_timer.timeout.connect(self.log_measurement)
        self.logging_timer.setSingleShot(True)

        # Shorter delay for initial log
        if self.logging_count == 0:
            self.logging_timer.start(2000)
        else:
            self.logging_timer.start(self.logging_interval_ms)

    def log_measurement(self):
        """ logs measurement from DHT22
        """
        # Disable now button
        self.screen_ui.current_reading_button.setDisabled(True)

        print("Logging Measurement!")

        # Set sensor status to busy
        if self.get_reading():
            # Store measurement always as celsius for consistency
            if self.system_temp_setting == "Celsius":
                temp_reading = self.temperature_display
            else:
                temp_reading = "{:.1f}".format(fahrenheit_to_celsius(float(self.temperature_display)))
            self.sys_db.store_measurement(
                temp_reading, self.humidity_display, self.last_time_read
            )

            # Increment logging count
            self.logging_count += 1

        # Stop logging if count reaches max number of logs
        if self.logging_count >= self.max_logging_count:
            self.configure_logging()

        # Restart timer if logging enabled
        if self.logging_status:
            self.start_logging_timer()

        # Enable now button
        self.screen_ui.current_reading_button.setEnabled(True)

    def update_temp_curve(self):
        # Hide plot if when false
        if self.screen_ui.temp_plot_switch.isChecked():
            self.plot.plot_temp_flag = True
            # Plot to be shown
            if self.plot.temp_curve is not None:
                self.plot.temp_curve.show()
        else:
            self.plot.plot_temp_flag = False
            # Plot to be hidden
            if self.plot.temp_curve is not None:
                self.plot.temp_curve.hide()

    def update_humidity_curve(self):
        # Hide plot if when false
        if self.screen_ui.humid_plot_switch.isChecked():
            self.plot.plot_humidity_flag = True
            # Plot to be shown
            if self.plot.humidity_curve is not None:
                self.plot.humidity_curve.show()
        else:
            self.plot.plot_humidity_flag = False
            # Plot to be hidden
            if self.plot.humidity_curve is not None:
                self.plot.humidity_curve.hide()

    def closeEvent(self, event):
        """ Adds additional close events to application
        """
        # Close database before closing application
        self.sys_db.close_connection()

        print("Closing Application")


def run_gui():
    print("Starting GUI!")
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    run_gui()