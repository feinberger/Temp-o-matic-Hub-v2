// Javascript code for client site 
// Test

$(document).ready(function () {

  // python websocket host info
  var host = "192.168.1.214";
  var port_py = "8888";
  var uri_py = "/ws";

  // python websocket variable
  var ws;

  // System parameters
  var tempUnits = "C";
  var currentTemp = null;
  var currentHumidity = null;
  var sensorStatus = "";
  var time_list = null;
  var temperature_list = null;
  var humidity_list = null;
  var sqsData = [];

  // Initialize the Amazon Cognito credentials provider
  AWS.config.region = 'us-east-1'; 
  AWS.config.credentials = new AWS.CognitoIdentityCredentials({IdentityPoolId: 'us-east-1:c42135ba-597a-4297-bc59-4476a72e8a69'});

  // Create SQS Service
  var sqs = new AWS.SQS({apiVersion: '2012-11-05'});
  var queueURL = "https://sqs.us-east-1.amazonaws.com/723839298742/Tempomatic_Queue";

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

      // Update Temperature SQS Data
      if (sqsData.length > 0)
      {
        for(t = 0; t < sqsData.length; t++) {
          // Convert to float
          sqsData[t].Temperature = parseFloat(sqsData[t].Temperature);

          // Convert to fahrenheit from celsius: Temp * (9/5) + 32
          sqsData[t].Temperature  = (sqsData[t].Temperature  * 1.8) + 32.0;

          // Limit to 1 decimal point
          sqsData[t].Temperature = sqsData[t].Temperature.toFixed(1);
        }

        updateSQSTable()
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

      // Update Temperature SQS Data
      if (sqsData.length > 0)
      {
        for(t = 0; t < sqsData.length; t++) {
          // Convert to float
          sqsData[t].Temperature = parseFloat(sqsData[t].Temperature);

          // Convert to celsius from fahrenheit: (Temp - 32) * (5/9)
          sqsData[t].Temperature = (sqsData[t].Temperature - 32.0) / 1.8;

          // Limit to 1 decimal point
          sqsData[t].Temperature = sqsData[t].Temperature.toFixed(1);
        }

        updateSQSTable();
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

  // Handle single sqs request
  $("#singleDataButton").click(function(evt) {
    singleSQSRequest().then(value => {
      if (value.Messages.length > 0) {
        // Add value to dataset
        const sqsMsg = value.Messages[0].Body;
        const sqsObj = JSON.parse(sqsMsg);
        addSQSData(sqsObj);

        // Delete msg from SQS
        var deleteParams = {
          QueueUrl: queueURL,
          ReceiptHandle: value.Messages[0].ReceiptHandle
        };
        sqs.deleteMessage(deleteParams, function(err, data) {
          if (err) {
            alert("Issue deleting SQS Message!");
          }
        });
    
        // Update SQS Count
        updateSQSMessageCount();
      } else {
        alert("SQS is Empty!");
    
        // Update SQS Count
        updateSQSMessageCount();
      }
    });
  });

  // Handle All SQS Message Request
  $("#allDataButton").click(async function(evt) {
    // Request SQS Info
    const msg = await sqsInfoRequest();

    // Extract number of messages on sqs
    var numOfMessages = msg.Attributes.ApproximateNumberOfMessages;

    // Update sqs count
    document.getElementById("sqsMessageCount").innerHTML = numOfMessages;

    // Calculate remaining messages
    var remainingMessages = parseInt(numOfMessages);

    while (remainingMessages > 0) {
      // Request SQS Info
      const newData = await singleSQSRequest();

      if (newData.Messages.length > 0) {
        // Add value to dataset
        const sqsMsg = newData.Messages[0].Body;
        const sqsObj = JSON.parse(sqsMsg);
        addSQSData(sqsObj);

        // Delete msg from SQS
        var deleteParams = {
          QueueUrl: queueURL,
          ReceiptHandle: newData.Messages[0].ReceiptHandle
        };
        
        sqs.deleteMessage(deleteParams, function(err, data) {
          if (err) {
            alert("Issue deleting SQS Message!");
          }
        });

        // Reduce remaining message
        remainingMessages = remainingMessages - 1;

        // Update sqs count
        document.getElementById("sqsMessageCount").innerHTML = remainingMessages.toString();

      } else {
        remainingMessages = 0;

        // Update sqs count
        document.getElementById("sqsMessageCount").innerHTML = remainingMessages.toString();
      }
    };
    
    // Update sqs count
    document.getElementById("sqsMessageCount").innerHTML = remainingMessages.toString();
  });

  // Handle SQS Message Count Button
  $("#sqsInfoButton").click(function(evt) {
    // Get total number of messages
    sqsInfoRequest().then(value => {
      var totalMessages = value.Attributes.ApproximateNumberOfMessages;
      document.getElementById("sqsMessageCount").innerHTML = totalMessages;
    });
  });

  // Update SQS Message Count
  function updateSQSMessageCount() {
    sqsInfoRequest().then(value => {
      var numOfMessages = value.Attributes.ApproximateNumberOfMessages;
      document.getElementById("sqsMessageCount").innerHTML = numOfMessages;
    });
  }

  // Add received data to sqs dataset
  function addSQSData(value) {
    const newData = value;
    
    // Add to latest dataset if length less then 20
    if (sqsData.length < 20) {
      sqsData.push(newData);
    }
    // Greater then 20, remove oldest item
    else {
      sqsData.shift();
      sqsData.push(newData);
    }

    updateSQSTable();
  };

  function updateSQSTable() {
    var i;
    // Update Datasets
    for (i=1; i < (sqsData.length + 1); i++) {
      // Update Temperature
      if (tempUnits == "F") {
        document.getElementById("temp"+i.toString()).innerHTML = sqsData[i-1].Temperature + " °F";
      }
      else if (tempUnits == "C") {
        document.getElementById("temp"+i.toString()).innerHTML = sqsData[i-1].Temperature + " °C";
      }

      // Update Humidity
      document.getElementById("humidity"+i.toString()).innerHTML = sqsData[i-1].Humidity + "%";

      // Update Timestamp
      document.getElementById("timestamp"+i.toString()).innerHTML = sqsData[i-1].Timestamp;
    };
  };

  // Single SQS Request
  async function singleSQSRequest() {
    // Set up parameters with Max Msg of 1
    const params = {
      MessageAttributeNames: [
         "All"
      ],
      QueueUrl: queueURL, 
      MaxNumberOfMessages: 1,
      VisibilityTimeout: 0,
      WaitTimeSeconds: 0
    };

    const msg = sqs.receiveMessage(params).promise();

    return msg;
  };

  // Max Number SQS Request
  async function maxSQSRequest() {
    // Set up parameters with Max Msg of 10
    const params = {
      MessageAttributeNames: [
         "All"
      ],
      QueueUrl: queueURL, 
      MaxNumberOfMessages: 10,
      VisibilityTimeout: 0,
      WaitTimeSeconds: 0
    };

    const msg = sqs.receiveMessage(params).promise();

    return msg; 
  };

  // SQS Attribute Info Request
  async function sqsInfoRequest() {
    // Set up parameters 
    const params = {
      AttributeNames: [
         "All"
      ],
      QueueUrl: queueURL
    };

    const msg = await sqs.getQueueAttributes(params).promise();

    return msg;
  };

  // Get All SQS Requests
  function getAllSQSRequests() {
    var finishedFlag = 0;
    maxSQSRequest.then(value => {
      if (value.Messages.length > 0) {
        finishedFlag = 0;
      }
      else {
        finishedFlag = 1;
      }
    });

    return finishedFlag;
  }

});
