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

  // create websocket instant for node.js
  ws_js = new WebSocket("ws://" + host + ":" + port_js + uri_js);
    
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

    // New Python Network Response
    if (incomingMsg.command == "PythonNetwork") {
      if(incomingMsg.status == "Success") {
        // Pass entire incoming msg to function for parsing
        updatePythonNetworkActivity(incomingMsg);
      }
      else{
        alert("Database is empty!")
      }
    }
    
    // New Plot Data Received
    if (incomingMsg.command == "plotData") {
      if(incomingMsg.status == "Success") {
        // Clear lists
        temperature_list = [];
        humidity_list = [];
        time_list = [];

        // Get Temperatures
        for (t = 0; t < incomingMsg.temperatures.length; t++)
        {
          if (tempUnits == "F") {
            temperature_list.push((parseFloat(incomingMsg.temperature[t]) * (9/5) + 32.0).toFixed(1));
          }
          else if (tempUnits == "C") {
            temperature_list.push(parseFloat(incomingMsg.temperatures[t]).toFixed(1));
          }
        }

        // Get Humidities
        for (h = 0; h < incomingMsg.humidities.length; h++)
        {
          humidity_list.push(parseFloat(incomingMsg.humidities[h]).toFixed(1));
        }
        
        // Get times
        time_list = incomingMsg.times;

        // Pass data to plot function
        createPlot(time_list, temperature_list, humidity_list);
      }
      else {
        alert("No data to generate plots!")
      }
    }
  };

  // Handle incoming websocket message callback for node js
  ws_js.onmessage = function(evt) {
    // De-serialize data
    var incomingMsg = JSON.parse(evt.data);

    // New Current Temperature Received
    if (incomingMsg.prevTemperature) {
      if (tempUnits == "F") {
        prevTemp = parseFloat(incomingMsg.prevTemperature) * (9/5) + 32.0;

        // Limit to 1 decimal point
        prevTemp = prevTemp.toFixed(1);
      }
      else if (tempUnits == "C") {
        prevTemp = parseFloat(incomingMsg.prevTemperature);

        // Limit to 1 decimal point
        prevTemp = prevTemp.toFixed(1);
      }
      updatePreviousTemperature();
    }
    
    // New Current Humidity Received
    if (incomingMsg.prevHumidity) {
      prevHumidity = parseFloat(incomingMsg.prevHumidity);

      // Limit to 1 decimal point
      prevHumidity = prevHumidity.toFixed(1);

      updatePreviousHumidity();
    }
    
    // New Timestamp Received
    if (incomingMsg.timestamp) {
      timeStr = (incomingMsg.timestamp).split(" ");
      prevTimestamp = timeStr[1];

      updatePreviousTimestamp();
    }

    // New NodeJS Network Response
    if (incomingMsg.command == "NodeJSNetwork") {
      // Pass entire incoming msg to function for parsing
      updateNodeJSNetworkActivity(incomingMsg);
    }
  };

  // Close Websocket callback
  ws.onclose = function(evt) {
    alert("Python Tornado Connection Closed");
  };

  // Open Websocket callback for python
  ws.onopen = function(evt) {
  };

  // Open Websocket callback for node.js
  ws_js.onopen = function(evt) {
  };

  // Close Nodejs Websocket callback
  ws_js.onclose = function(evt) {
    alert("NodeJS Connection Closed");
  };

  // Send current reading request to python server
  $("#currentReadingButton").click(function(evt) {
    ws.send("CR");
  });

  // Send previous reading request to node js server
  $("#prevReadingButton").click(function(evt) {
    ws_js.send("PR");
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
  
  // Get Network activity from node js and python servers
  $("#networkButton").click(function(evt) {
    ws.send("NA")
    ws_js.send("NA");
  });

  $("#plotButton").click(function(evt) {
    ws.send("PD");
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

  // Update Previous Temperature
  var updatePreviousTemperature = function() {
    if (tempUnits == "F") {
      document.getElementById("prevTemp").innerHTML = prevTemp.toString() + " °F";
    }
    else if (tempUnits == "C") {
      document.getElementById("prevTemp").innerHTML = prevTemp.toString() + " °C";
    }
  };

  // Update Previous Humidity
  var updatePreviousHumidity = function() {
    document.getElementById("prevHumidity").innerHTML = prevHumidity.toString() + " %";
  };

  // Update Previous Timestamp
  var updatePreviousTimestamp = function() {
    document.getElementById("timestamp").innerHTML = prevTimestamp;
  };

  // Update NodeJS Network Activity
  var updateNodeJSNetworkActivity = function(msg) {
    if (msg.starttime) {
      document.getElementById("nodeStartTime").innerHTML = msg.starttime;
    }
    if (msg.endtime) {
      document.getElementById("nodeEndTime").innerHTML = msg.endtime;
    }
    if (msg.duration) {
      document.getElementById("nodeDuration").innerHTML = msg.duration + "ms";
    }
    if (msg.dataset1) {
      document.getElementById("nodeData1").innerHTML = msg.dataset1 + " %";
    }
    if (msg.dataset2) {
      document.getElementById("nodeData2").innerHTML = msg.dataset2 + " %";
    }
    if (msg.dataset3) {
      document.getElementById("nodeData3").innerHTML = msg.dataset3 + " %";
    }
    if (msg.dataset4) {
      document.getElementById("nodeData4").innerHTML = msg.dataset4 + " %";
    }
    if (msg.dataset5) {
      document.getElementById("nodeData5").innerHTML = msg.dataset5 + " %";
    }
    if (msg.dataset6) {
      document.getElementById("nodeData6").innerHTML = msg.dataset6 + " %";
    }
    if (msg.dataset7) {
      document.getElementById("nodeData7").innerHTML = msg.dataset7 + " %";
    }
    if (msg.dataset8) {
      document.getElementById("nodeData8").innerHTML = msg.dataset8 + " %";
    }
    if (msg.dataset9) {
      document.getElementById("nodeData9").innerHTML = msg.dataset9 + " %";
    }
    if (msg.dataset10) {
      document.getElementById("nodeData10").innerHTML = msg.dataset10 + " %";
    }
  };

  // Update Python Network Activity
  var updatePythonNetworkActivity = function(msg) {
    if (msg.starttime) {
      document.getElementById("pyStartTime").innerHTML = msg.starttime;
    }
    if (msg.endtime) {
      document.getElementById("pyEndTime").innerHTML = msg.endtime;
    }
    if (msg.duration) {
      document.getElementById("pyDuration").innerHTML = msg.duration + "ms";
    }
    if (msg.dataset1) {
      document.getElementById("pyData1").innerHTML = msg.dataset1 + " %";
    }
    if (msg.dataset2) {
      document.getElementById("pyData2").innerHTML = msg.dataset2 + " %";
    }
    if (msg.dataset3) {
      document.getElementById("pyData3").innerHTML = msg.dataset3 + " %";
    }
    if (msg.dataset4) {
      document.getElementById("pyData4").innerHTML = msg.dataset4 + " %";
    }
    if (msg.dataset5) {
      document.getElementById("pyData5").innerHTML = msg.dataset5 + " %";
    }
    if (msg.dataset6) {
      document.getElementById("pyData6").innerHTML = msg.dataset6 + " %";
    }
    if (msg.dataset7) {
      document.getElementById("pyData7").innerHTML = msg.dataset7 + " %";
    }
    if (msg.dataset8) {
      document.getElementById("pyData8").innerHTML = msg.dataset8 + " %";
    }
    if (msg.dataset9) {
      document.getElementById("pyData9").innerHTML = msg.dataset9 + " %";
    }
    if (msg.dataset10) {
      document.getElementById("pyData10").innerHTML = msg.dataset10 + " %";
    }
  };

  // Create plot
  var createPlot = function(times, temperatures, humidities) {

    // plot parameters
    var temp_axis_title = "";

    if (tempUnits == "F") {
      temp_axis_title = "Temperature °F";
      temp_range = [-40, 176];
    }
    else if (tempUnits == "C") {
      temp_axis_title = "Temperature °C";
      temp_range = [-40, 80];
    } 

    var temperature_data = {
      x: times,
      y: temperatures,
      type: 'scatter',
    };
    
    var humidity_data = {
      x: times,
      y: humidities,
      type: 'scatter'
    };

    var temp_layout = {
      title: "Temp vs Time",
      titlefont: {
        color: '#f1f1f1'
      },
      autosize: false,
      width: 600,
      height: 350,
      margin: {
        l: 50,
        r: 50,
        b: 100,
        t: 100,
        pad: 4
      },
      yaxis: {
        title: temp_axis_title,
        titlefont: {
          color: '#f1f1f1'
        },
        range: temp_range
      },
      
      paper_bgcolor: '#222325',
      plot_bgcolor: '#222325'
    };

    var humidity_layout = {
      title: "Humidity vs Time",
      titlefont: {
        color: '#f1f1f1'
      },
      autosize: false,
      width: 600,
      height: 350,
      margin: {
        l: 50,
        r: 50,
        b: 100,
        t: 100,
        pad: 4
      },
      yaxis: {
        title: "Humidity %",
        titlefont: {
          color: '#f1f1f1'
        },
        range: [0, 100]
      },
      
      paper_bgcolor: '#222325',
      plot_bgcolor: '#222325'
    };

    Plotly.newPlot('tempPlot', [temperature_data], temp_layout);
    Plotly.newPlot('humidityPlot', [humidity_data], humidity_layout);
  };

});
