"""main.py: This is the main module to run the temp-o-matic application.

This python module is used to run the temp-o-matic application that displays
temperature and humidity and the corresponding plot. It also starts the two
servers that support the web client interface application.

"""
import sys
import os
import multiprocessing
import time
import subprocess

from PyQt5.QtWidgets import QApplication

from src.temp_o_matic import MainWindow
# from src.server import run_server

def run_tornado_server():
    print("Running Tornado Server!")
    run_server()

def run_nodejs_server():
    print("Running NodeJS Server!") 

    # Get current working directory
    current_directory = os.getcwd()
    
    # Add .bat file to path
    script_file = os.path.join(current_directory, "src/js_server.js")

    # Run bat file to compile .ui to .py
    subprocess.call(["node", script_file])

def run_application():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    # run_application()
    gui_process = multiprocessing.Process(target=run_application, args=())
    # tornado_process = multiprocessing.Process(target=run_tornado_server, args=())
    # nodejs_process = multiprocessing.Process(target=run_nodejs_server, args=())

    gui_process.start()

    time.sleep(10)

    # tornado_process.start()
    # nodejs_process.start()

    gui_process.join()

    print("GUI has completed")
    # tornado_process.join()
    # nodejs_process.join()

    print("Exiting Application")
