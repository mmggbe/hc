#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""HClog library.

version 1.0
March 2013
G. De Vocht"""

import logging
from logging.handlers import TimedRotatingFileHandler


class Log:

            
    def __init__(self, srvName, debug):
        """Usage:
             srvName: (= Service Name) Thisis the name of the service indicated in the log TimedRotatingFileHandler
             debug: if true error and debug message will be logged, otherwise only error
           """
        
        logPath= ''
        retentionTime = 5
        
        self.logger = logging.getLogger(srvName)
        
        self.logger.setLevel(self.get_logging_level(debug))
        
        handler = TimedRotatingFileHandler(logPath + srvName + '.log',
                                        when='midnight',
                                        backupCount=retentionTime)
        formatter = logging.Formatter('%(asctime)s %(name)s[%(process)d]: %(message)s',datefmt='%b %d %H:%M:%S')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
    def get_logging_level(self, debug):
        if debug:
            return logging.DEBUG
        else:
            return logging.ERROR
        
    def error(self, msg):
        self.logger.error(msg)
        
    def debug(self, msg):
        self.logger.debug(msg)
        
    def info(self, msg):
        self.logger.info(msg)
          
    
if __name__ == '__main__':

    hclog = HcLog('testLog', True)
    hclog.error ('this is a test error message')
    hclog.debug('this  is a test debug message')
