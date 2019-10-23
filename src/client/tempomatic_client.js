// Javascript code for client site 
// Test

$(document).ready(function () {

  // python websocket host info
  var host = "192.168.1.214";
  var port_py = "8888";
  var uri_py = "/ws";

  // node.js websocket host info
  var port_js = "8989";
  var uri_js = "/";

  // python websocket variable
  var ws;

  // node.js websocket variable
  var ws_js;

  // System parameters
  var tempUnits = "C";
  var currentTemp = null;
  var currentHumidity = null;
  var sensorStatus = "";
  var prevTemp = null;
  var prevHumidity = null;
  var prevTimestamp = "";
  var time_list = null;
  var temperature_list = null;
  var humidity_list = null;

  // create websocket instance for python
  ws = new WebSocket("ws://" + host + ":" + port_py + uri_py);
    
  // Handle incoming websocket message callback for python
  ws.onmessage = function(evt) {
    // De-serialize data
    var incomingMsg = JSON.parse(evt.data)

    // Determine action

    // New Current Temperature Received
    if (incomingMsg.currentTemperature) {
      if (tempUnits == "F") {
        currentTemp = parseFloat(incomingMsg.currentTemperature) * (9/5) + 32.0;

        // Limit to 1 decimal point
        currentTemp = currentTemp.toFixed(1);
      }
      else if (tempUnits == "C") {
        currentTemp = parseFloat(incomingMsg.currentTemperature)
      }
      updateCurrentTemperature();
    }
    
    // New Current Humidity Received
    if (incomingMsg.currentHumidity) {
      currentHumidity = parseFloat(incomingMsg.currentHumidity);

      // Limit to 1 decimal point
      currentHumidity = currentHumidity.toFixed(1);

      updateCurrentHumidity();
    }
    
    // New Sensor Status Received
    if (incomingMsg.sensorStatus) {
      sensorStatus = incomingMsg.sensorStatus;

      updateSensorStatus();
    }
  };

  // Close Websocket callback
  ws.onclose = function(evt) {
    alert("Python Tornado Connection Closed");
  };

  // Open Websocket callback for python
  ws.onopen = function(evt) {
  };

  // Send current reading request to python server
  $("#currentReadingButton").click(function(evt) {
    ws.send("CR");
  });

  // Convert Units
  $("#convertButton").click(function(evt) {
    if (tempUnits == "C") {
      // Update units
      tempUnits = "F";

      // Update button text
      document.getElementById("convertButton").innerHTML = "Convert to Celsius";

      // Update Current Temperature
      if (currentTemp != null) {
        // Convert to fahrenheit from celsius: Temp * (9/5) + 32
        currentTemp = (currentTemp * 1.8) + 32.0;

        // Limit to 1 decimal point
        currentTemp = currentTemp.toFixed(1);

        // Update Temperature Text
        updateCurrentTemperature();
      }
      else {
        document.getElementById("currentTemp").innerHTML = "- °F";
      }

      // Update Previous Temperature
      if (prevTemp != null) {
        // Convert to fahrenheit from celsius: Temp * (9/5) + 32
        prevTemp = (prevTemp * 1.8) + 32.0;

        // Limit to 1 decimal point
        prevTemp = prevTemp.toFixed(1);

        // Update Temperature Text
        updatePreviousTemperature();
      }
      else {
        document.getElementById("prevTemp").innerHTML = "- °F";
      }

      // Update Temperature Plots
      if (temperature_list != null)
      {
        for(t = 0; t < temperature_list.length; t++) {
          // Convert to fahrenheit from celsius: Temp * (9/5) + 32
          temperature_list[t] = (temperature_list[t] * 1.8) + 32.0;

          // Limit to 1 decimal point
          temperature_list[t] = temperature_list[t].toFixed(1);
        }
        
        // Update plot
        createPlot(time_list, temperature_list, humidity_list);
      }      
    }
    else if (tempUnits == "F") {
      // Update units
      tempUnits = "C";

      // Update button text
      document.getElementById("convertButton").innerHTML = "Convert to Fahrenheit";

      // Update Current Temperature
      if (currentTemp != null) {
        // Convert to celsius from fahrenheit: (Temp - 32) * (5/9)
        currentTemp = (currentTemp - 32.0) / 1.8;

        // Limit to 1 decimal point
        currentTemp = currentTemp.toFixed(1);

        // Update Temperature Text
        updateCurrentTemperature();
      }
      else {
        document.getElementById("currentTemp").innerHTML = "- °C";
      }

      // Update Previous Temperature
      if (prevTemp != null) {
        // Convert to celsius from fahrenheit: (Temp - 32) * (5/9)
        prevTemp = (prevTemp - 32.0) / 1.8;

        // Limit to 1 decimal point
        prevTemp = prevTemp.toFixed(1);

        // Update Temperature Text
        updatePreviousTemperature();
      }
      else {
        document.getElementById("prevTemp").innerHTML = "- °C";
      }

      // Update Temperature Plots
      if (temperature_list != null)
      {
        for(t = 0; t < temperature_list.length; t++) {
          // Convert to celsius from fahrenheit: (Temp - 32) * (5/9)
          temperature_list[t] = (temperature_list[t] - 32.0) / 1.8;

          // Limit to 1 decimal point
          temperature_list[t] = temperature_list[t].toFixed(1);
        }

        // Update plot
        createPlot(time_list, temperature_list, humidity_list);
      }
    }
  });

  // Update Current Temperature
  var updateCurrentTemperature = function() {
    if (tempUnits == "F") {
      document.getElementById("currentTemp").innerHTML = currentTemp.toString() + " °F";
    }
    else if (tempUnits == "C") {
      document.getElementById("currentTemp").innerHTML = currentTemp.toString() + " °C";
    }
  };

  // Update Current Humidity
  var updateCurrentHumidity = function() {
    document.getElementById("currentHumidity").innerHTML = currentHumidity.toString() + " %";
  };

  // Update Sensor Status
  var updateSensorStatus = function() {
    document.getElementById("sensorStatus").innerHTML = sensorStatus;
  };
});
