#!/usr/bin/python3
# -*- coding: utf-8 -*-

import shutil
import sys, os
import logging
import time
import subprocess

LOG_FILE= "/home/ftp/cameraFTP.log"

def main(argv):


	global logger 
	global FTP_file_path

	logger = logging.getLogger(__name__)
	logger.setLevel(logging.INFO)

# create a file handler
	handler = logging.FileHandler(LOG_FILE)
	handler.setLevel(logging.INFO)

# create a logging format
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	handler.setFormatter(formatter)

# add the handlers to the logger
	logger.addHandler(handler)

	for arg in sys.argv:
		print( arg )

	logger.info("++++ {0} started with UID {1}, GID {2} ++++".format(argv[0],os.getuid(),os.getgid()))
	logger.info( ("Argument List: {}").format(str(sys.argv)))


if __name__ == "__main__":
   main(sys.argv)
