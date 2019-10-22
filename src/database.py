"""database.py: This is the python module for the database functions of the application

This python module is used to interface with the mysql database storing the
temperature and humidity readings. This contains a class to provide a list of
useful functionsthat the main application can use to manipulate and interface
with the database

"""
import pymysql


class TemperatureDatabase:
    """ Class that interfaces with the mysql database for the sensor data
    """

    def __init__(self, database_name, user, password, host="localhost"):
        """Initializes the mysql database

        Args:
            database_name: database name on machine
            user: user/login id to access database
            password: password to identify user
            host: where the database server is
        """
        # Database Parameters
        self.host = host
        self.database_name = database_name
        self.user = user
        self.password = password
        self.db_connection = None
        self.cursor = None

        # Open connection to database
        self.connect_to_database()

    def connect_to_database(self):
        """ Function to connect to database

        Returns:
            bool: True if the database was connected, False if failed
        """
        self.db_connection = pymysql.connect(
            self.host, self.user, self.password, self.database_name
        )
        print("Opening Database")

        return True

    def create_table(self):
        """ Creates temperature table if it does not exist
        """
        try:
            cursor = self.db_connection.cursor()
            sql = "CREATE TABLE SensorData(id INT NOT NULL AUTO_INCREMENT, temperature VARCHAR(5), humidity VARCHAR(5), timestamp VARCHAR(50), PRIMARY KEY (id))"
            cursor.execute(sql)
        except pymysql.InternalError:
            # Delete table if already exists and retry
            self.delete_table()
            cursor = self.db_connection.cursor()
            sql = "CREATE TABLE SensorData(id INT NOT NULL AUTO_INCREMENT, temperature VARCHAR(5), humidity VARCHAR(5), timestamp VARCHAR(50), PRIMARY KEY (id))"
            cursor.execute(sql)

        return True

    def delete_table(self):
        """ Deletes temperature table to reset or clear all values
        """
        with self.db_connection.cursor() as cursor:
            sql = "DROP TABLE SensorData"
            cursor.execute(sql)

    def store_measurement(self, temperature, humidity, timestamp):
        """ Stores sensor reading into database
        """
        with self.db_connection.cursor() as cursor:
            sql = "INSERT INTO SensorData (temperature, humidity, timestamp) VALUES (%s, %s, %s)"
            cursor.execute(sql, (temperature, humidity, timestamp))

        self.db_connection.commit()

    def get_measurement(self, id_number):
        """ Gets measurement from database
        """
        with self.db_connection.cursor() as cursor:
            sql = "SELECT * FROM SensorData WHERE id=%s"
            cursor.execute(sql, (id_number,))
            result = cursor.fetchone()

        return result

    def get_last_measurement_id(self):
        """ Gets the id of the latest measurement stored in the database
        https://stackoverflow.com/questions/10503195/get-last-entry-in-a-mysql-table
        """
        with self.db_connection.cursor() as cursor:
            sql = "SELECT MAX(id) FROM SensorData"
            cursor.execute(sql)
            result = cursor.fetchone()
        
        return result[0]

    def get_last_measurements(self, num_of_measurements):
        """ Gets the last X number of measurements

        Args:
            num_of_measurements: number of recent measurements to get

        Returns:
            list: last number of measurements asked for unless there is not
            enough; which then just returns all measurements
        """

        # Get last measurement id
        last_measurement_id = self.get_last_measurement_id()

        # Empty measurement list
        measurements = []

        # Return all ids if not enough measurements
        if last_measurement_id is None:
            pass
        elif last_measurement_id < num_of_measurements:
            return list(self.get_all_measurements())
        else:
            # Count down number of measurements
            for meas in range(
                last_measurement_id, (last_measurement_id - num_of_measurements), -1
            ):
                measurements.append(self.get_measurement(meas))

            return measurements

    def get_all_measurements(self):
        """ Gets measurement from database
        """
        with self.db_connection.cursor() as cursor:
            sql = "SELECT * FROM SensorData"
            cursor.execute(sql)
            result = cursor.fetchall()

        return result

    def close_connection(self):
        """ Closes connection to database
        """
        print("Closing Database")
        self.db_connection.close()


def test_code():
    """Test code for database module
    """
    # Create database object
    new_db = TemperatureDatabase("TEST_DATABASE", "TEMP_MONITOR", "PASSWORD")

    # Store test measurement
    new_db.store_measurement(55.1, 22.3, "09/15/2019 11:11:52")

    # Get measurement
    result = new_db.get_measurement(1)
    print(result)
    result = new_db.get_all_measurements()
    print(result)

    # Get last measurement id
    result = new_db.get_last_measurement_id()
    print(result)

    # Get last 10 measurements
    result = new_db.get_last_measurements(10)
    print(result)

    # Close connection
    new_db.close_connection()


if __name__ == "__main__":
    print("Database Test")

    # Run Test Code
    test_code()
