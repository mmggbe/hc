'''
HClog library.

version 1.0
March 2018

@author: G. De Vocht
'''
import logging
from logging.handlers import TimedRotatingFileHandler
from HCsettings import HcLog

class Log(object):
    '''
    Usage:
             srvName: (= Service Name) This is the name of the service indicated in the log TimedRotatingFileHandler
             level: if ='debug' all syslog level will be written to the file
                    else only level before info
    '''
    def __init__(self, srvName, level):
        
        logPath= HcLog.config("logPath")
        retentionTime = int(HcLog.config("retentionTime"))
        
        
        self.logger = logging.getLogger(srvName)
        
        self.logger.setLevel(self.get_logging_level(level))
        
        handler = TimedRotatingFileHandler(logPath + srvName + '.log',
                                        when='midnight',
                                        backupCount=retentionTime)
        #formatter = logging.Formatter('%(asctime)s %(name)s(%(process)d)[%(levelname)s]: %(message)s',datefmt='%b %d %H:%M:%S')
        formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s',datefmt='%b %d %H:%M:%S')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
    
    def get_logging_level(self, level):
        '''
        Get the logging levels specified on the command line.
        The level can only be set once.
        '''
        if level == 'debug':
            return logging.DEBUG
        else :
            return logging.INFO
        
   
        
    def get(srvName):
        return logging.getLogger(srvName)
        
    def getL(self, srvName):
            return logging.getLogger(srvName)
        
    def error(self, msg, ip=None):
        self.logger.error(self.__message(msg, ip))
        
    def debug(self, msg, ip=None):
        self.logger.debug(self.__message(msg, ip))
        
    def info(self, msg, ip=None):
        self.logger.info(self.__message(msg, ip))
          
    def __message(self, msg, ip):
        if ip is None :
            return msg
        else:
            return "[client " + ip + "] " + msg
        
if __name__ == '__main__':

    hclog = Log('testLog', 'debug')
    hclog.error ('this is a test error message without ip')
    hclog.debug('this  is a test debug message without ip')
    hclog.error ('this is a test error message with ip', '1.1.1.1')
    hclog.debug('this  is a test debug message with ip', '1.1.1.1')