/*

Resources: 
-https://www.w3schools.com/nodejs/nodejs_mysql.asp
-https://www.pubnub.com/blog/nodejs-websocket-programming-examples/
*/

console.log("Starting Node JS Server...");

// HTTP Server Requirements
const http = require('http');
const WebSocketServer = require('websocket').server;

// Create HTTP Server on Port 8989
const server = http.createServer();
server.listen(8989);

// Create websocket on http server
const wsServer = new WebSocketServer({
    httpServer: server
});

// Mysql requirements
var mysql = require('mysql2/promise');

// Promise Handler utility
const util = require( 'util' );

// Asynchronous function handler
const async = require('async');

// Variables
var lastTemperature = 9;
var lastHumidity = 9;
var dbError = null;

// Mysql database
database = mysql.createPool({
    host: "localhost",
    user: "TEMP_MONITOR",
    password: "PASSWORD",
    database: "TEST_DATABASE",
    waitForConnections: true,
    connectionLimit: 10,
    queueLimit: 0
});

// Handle websocket requests
wsServer.on('request', function(request) {
    const connection = request.accept(null, request.origin);

    // Message handling
    connection.on('message', function(message) {
      console.log('Received Message:', message.utf8Data);
      
      // Handle message actions
      decodeMessage(message.utf8Data);
    });
    
    // On Close Request
    connection.on('close', function(reasonCode, description) {
        console.log('Client has disconnected.');
    });

    var decodeMessage = function(msg) {
        console.log(msg);
    
        // Handle Previous Readings Request
        if (msg == "PR") {
            console.log("Sending Previous Readings...");

            // Get last measurement from database
            // https://stackoverflow.com/questions/48908930/function-returns-promise-object-instead-of-value-async-await
            lastMeasurement().then(value => sendPrevReadings(value));
        }
        // Handle network activity request
        if (msg == "NA") {
            console.log("Querying Last 10 Values")

            // Get start time
            var startTime = new Date();

            // Get last measurements from database
            networkTest().then(value => sendNetworkResults(startTime, value));
        }
    };

    var sendPrevReadings = function(prevReadings) {
        connection.sendUTF(JSON.stringify(prevReadings))
    };

    var sendNetworkResults = function(networkStartTime, readings) {
        // Network Results
        networkResults = {};

        // Add Network Activity Command
        networkResults["command"] = "NodeJSNetwork";

        // End Time
        var endTime = new Date();

        // readings are return 1 - 10 (unless theres not 10)
        for (i = 0; i < readings.length; i++) {
            datasetKey = "dataset" + (i + 1).toString();
            networkResults[datasetKey] = readings[i].humidity;
        }

        // Get duration
        networkResults["duration"] = endTime.getTime() - networkStartTime.getTime();

        // Start and End times
        networkResults["starttime"] = networkStartTime.getHours() + ":" + networkStartTime.getMinutes() + ":" + networkStartTime.getSeconds() + ":" + networkStartTime.getMilliseconds();
        networkResults["endtime"] = endTime.getHours() + ":" + endTime.getMinutes() + ":" + endTime.getSeconds() + ":" + endTime.getMilliseconds();

        connection.sendUTF(JSON.stringify(networkResults));
    };
});

// Open Database Function
function openDatabase() {
    // Mysql connection
    const connection = mysql.createConnection({
        host: "localhost",
        user: "TEMP_MONITOR",
        password: "PASSWORD",
        database: "TEST_DATABASE"
    });

    return {
        query( sql, args ) {
            return util.promisify(connection.query).call(connection, sql, args);
        },
        close() {
            return util.promisify(connection.end).call(connection);
        }
    };
};

// Get last measurement function
async function lastMeasurement() {
    const result = await database.execute("SELECT * FROM SensorData ORDER BY id DESC LIMIT 0, 1");

    // Result is the second item in a tuple
    const reading = result[0][0]
    
    // Return result in proper json format
    return {prevTemperature:reading.temperature, prevHumidity:reading.humidity, timestamp:reading.timestamp};
};

// Network activity test function
async function networkTest() {
    const rows = await database.execute("SELECT * FROM SensorData ORDER BY id ASC LIMIT 0, 10");
    
    // return result list
    return rows[0];
};
