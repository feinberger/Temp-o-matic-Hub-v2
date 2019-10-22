"""plotter.py: This is the python module for the plotting functions of the application

This python module is used to interface with the plot widget that plots the humidity
and temperature values located on the database. 

Helpful resource:
https://stackoverflow.com/questions/45872255/embed-a-pyqtgraph-plot-into-a-qt-ui
https://github.com/pyqtgraph/pyqtgraph/blob/develop/examples/MultiplePlotAxes.py
https://stackoverflow.com/questions/29473757/pyqtgraph-multiple-y-axis-on-left-side

"""

import pyqtgraph as pg
import pyqtgraph.exporters
import numpy as np
import datetime

from src.dht_22 import (
    DHT22_MAXIMUM_HUMIDITY,
    DHT22_MAXIMUM_TEMPERATURE,
    DHT22_MINIMUM_HUMIDITY,
    DHT22_MINIMUM_TEMPERATURE,
    celsius_to_fahrenheit,
    fahrenheit_to_celsius,
)

class PlotWidget(pg.GraphicsWindow):
    """ Pyqtgraph plot widget that contains functions to interface with the ui plot
    """

    # Configure color options as stock background, off-white text
    pg.setConfigOption('background', (34, 35, 37))
    pg.setConfigOption('foreground', (241, 241, 241))

    def __init__(self, parent=None, **kargs):
        pg.GraphicsWindow.__init__(self, **kargs)
        self.setParent(parent)

        # Add plot data
        self.setWindowTitle('Sensor Measurements')

        # Temperature plot is main plot item
        self.temp_plot = self.addPlot(labels={'left':'Temperature °C', 'right':'Humidity %', 'bottom':'Time'})

        # Create a humidity plot for the second axis and link with temperature plot
        self.humidity_plot = pg.ViewBox()
        self.temp_plot.scene().addItem(self.humidity_plot)
        self.temp_plot.getAxis('right').linkToView(self.humidity_plot)
        
        # Link x-axis of both plots
        self.humidity_plot.setXLink(self.temp_plot)

        # Set axis range to limit of sensor
        self.temp_plot.setYRange(DHT22_MINIMUM_TEMPERATURE, DHT22_MAXIMUM_TEMPERATURE)
        self.humidity_plot.setYRange(DHT22_MINIMUM_HUMIDITY, DHT22_MAXIMUM_HUMIDITY)

        # Plot data parameters/items
        self.time_values = None
        self.temp_values = None
        self.humidity_values = None
        self.temp_units = "Celsius"
        self.start_time = datetime.datetime.now()
        self.temp_curve = None
        self.humidity_curve = None
        self.plot_temp_flag = True
        self.plot_humidity_flag = True

        # Temperature plot signals changed 
        self.temp_plot.sigRangeChanged.connect(self.update_views)

    def update_views(self):
        self.humidity_plot.setGeometry(self.temp_plot.vb.sceneBoundingRect())
        self.humidity_plot.linkedViewChanged(self.temp_plot.vb, self.humidity_plot.XAxis)

    def convert_to_celsius(self):
        """ Converts the plot to celsius values
        """
        # Update system units
        self.temp_units = "Celsius"

        # Update temperature axis
        self.temp_plot.setLabel('left', text='Temperature °C')
        self.temp_plot.setYRange(DHT22_MINIMUM_TEMPERATURE, DHT22_MAXIMUM_TEMPERATURE)

        # Remove Old Plot
        self.temp_plot.removeItem(self.temp_curve)

        # Update temperature measurements if exisits
        if self.temp_values is not None:
            for idx, value in enumerate(self.temp_values):
                self.temp_values[idx] = fahrenheit_to_celsius(value)

            # Update plot
            self.plot_values()


    def convert_to_fahrenheit(self):
        """ Converts the plot to fahrenheit values
        """
        # Update system units
        self.temp_units = "Fahrenheit"

        # Update temperature axis
        self.temp_plot.setLabel('left', text='Temperature °F')
        self.temp_plot.setYRange(celsius_to_fahrenheit(DHT22_MINIMUM_TEMPERATURE), celsius_to_fahrenheit(DHT22_MAXIMUM_TEMPERATURE))

        # Remove Old Plot
        self.temp_plot.removeItem(self.temp_curve)

        # Update temperature measurements if exisits
        if self.temp_values is not None:
            for idx, value in enumerate(self.temp_values):
                self.temp_values[idx] = celsius_to_fahrenheit(value)

            # Update plot
            self.plot_values()


    def update_values(self, temp_list, humidity_list, time_list):
        """ Updates the plot with measurements given

        Args:
            temp_list: List of temperature readings
            humidity_list: List of humidity readings
            time_list: List of timestamps
        """

        # Set plot values and convert them to floats and adjust to Fahrenheit if needed
        # https://stackoverflow.com/questions/1614236/in-python-how-do-i-convert-all-of-the-items-in-a-list-to-floats
        if self.temp_units == "Fahrenheit":
            self.temp_values = [celsius_to_fahrenheit(float(temp)) for temp in temp_list]
        else:
            self.temp_values = [float(temp) for temp in temp_list]
        self.humidity_values = [float(humidity) for humidity in humidity_list]

        # Convert time into elapsed seconds from start
        self.time_values = []

        for time in time_list:
            timestamp = datetime.datetime.strptime(time, "%m/%d/%y %X")
            elapsed_time = (timestamp - self.start_time).total_seconds()
            self.time_values.append(elapsed_time)

        self.plot_values()

    def plot_values(self):
        """ Updates the plot with local measurements stored
        """

        # Set plot values
        print("Temperatures: {}".format(self.temp_values))
        print("Humidity: {}".format(self.humidity_values))
        print("Times: {}".format(self.time_values))

        # Remove old curves if required
        if self.temp_curve is not None:
            self.temp_plot.removeItem(self.temp_curve)
        if self.humidity_curve is not None:
            self.humidity_plot.removeItem(self.humidity_curve)

        self.temp_curve = pg.PlotDataItem(self.time_values, self.temp_values, pen=pg.mkPen(color=(170, 85, 255), width=3), symbolPen=pg.mkPen(color=(170, 85, 255), width=5), symbolSize=8)
        self.humidity_curve = pg.PlotDataItem(self.time_values, self.humidity_values, pen=pg.mkPen(color=(255, 170, 0), width=3), symbolPen=pg.mkPen(color=(255, 170, 0), width=5), symbolSize=8)
        
        # Plot values
        if self.plot_temp_flag:
            self.temp_plot.addItem(self.temp_curve)
        
        if self.plot_humidity_flag:
            self.humidity_plot.addItem(self.humidity_curve)
