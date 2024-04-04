"""
This module is responsible for setting up the logging for thei buggd application.

On startup, setup_logging() is called to configure the logging to both stdout and a file.
The current time and CPU serial number are used to create a unique log file name.

This means that each boot of the device will create a new log file.
"""

import logging
from logging.handlers import WatchedFileHandler
import os
import time
import sys
from .utils import discover_serial


# The log_dir can't be included in config because we're
# not loading config until after logging has started.
LOG_DIR = '/home/buggd/logs/'

# This establishes the lowest level of logging that will be output in each handler.
# to the console and file. This can be changed to higher levels on a per-module basis.
STDOUT_DEFAULT_LOG_LEVEL = logging.DEBUG
FILE_DEFAULT_LOG_LEVEL = logging.DEBUG

class Log:
    """
    Setup logging for the application

    Called once at the start of the application to setup logging to both stdout and a file
    """
    def __init__(self, log_dir=LOG_DIR):
        self.log_dir = log_dir
        self.current_logfile_name = None
        self.cpu_serial = discover_serial()

        # Create log directory if it doesn't exist
        os.makedirs(self.log_dir, exist_ok=True)

        # Create a logger
        self.logger = logging.getLogger(__name__)

        # This is the lowest level of logging that will be output
        self.logger.setLevel(logging.DEBUG)

        # Create a formatter
        self.formatter = logging.Formatter(f'{self.cpu_serial} - %(message)s')

        # Handler for stdout
        self.stdout_handler = logging.StreamHandler(sys.stdout)
        self.stdout_handler.setLevel(STDOUT_DEFAULT_LOG_LEVEL)
        self.stdout_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.stdout_handler)

        # Create a log file and handler with our rotation mechanism
        self.file_handler = None
        self.rotate_log()

    def get_current_logfile(self):
        """
        Return the full path of the current log file that is being written to
        We use this in in the uploading thread to avoid moving the open file
        """
        return self.current_logfile_name

    def generate_new_logfile_name(self):
        """ Generate a new log file name based on the current time and CPU serial number """
        # Get the current time - this is the time buggd was started
        start_time = time.strftime('%Y%m%d_%H%M')

        fn = f'rpi_eco_{self.cpu_serial}_{start_time}.log'
        return os.path.join(self.log_dir, fn)

    def rotate_log(self):
        """
        Rotate the log file by closing the current one and creating a new one
        """
        if self.file_handler:
            self.logger.removeHandler(self.file_handler)
        
        fn = self.generate_new_logfile_name()
        new_handler = WatchedFileHandler(filename=fn)
        new_handler.setLevel(FILE_DEFAULT_LOG_LEVEL)
        new_handler.setFormatter(self.formatter)
        self.logger.addHandler(new_handler)

        self.logger.info('Rotated log file to %s', fn)