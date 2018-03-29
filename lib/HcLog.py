'''
HClog library.

version 1.0
March 2013

@author: G. De Vocht
'''
import logging
from logging.handlers import TimedRotatingFileHandler
from HCsettings import HcLog

class Log(object):
    '''
    Usage:
             srvName: (= Service Name) Thisis the name of the service indicated in the log TimedRotatingFileHandler
             debug: if true error and debug message will be logged, otherwise only error
    '''
    def __init__(self, srvName, debug):
        
        logPath= HcLog.config("logPath")
        retentionTime = int(HcLog.config("retentionTime"))
        
        self.logger = logging.getLogger(srvName)
        
        self.logger.setLevel(self.get_logging_level(debug))
        
        handler = TimedRotatingFileHandler(logPath + srvName + '.log',
                                        when='midnight',
                                        backupCount=retentionTime)
        formatter = logging.Formatter('%(asctime)s %(name)s(%(process)d)[%(levelname)s]: %(message)s',datefmt='%b %d %H:%M:%S')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
    def get_logging_level(self, debug):
        if debug:
            return logging.DEBUG
        else:
            return logging.ERROR
        
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
            return msg + " From " + ip
        
if __name__ == '__main__':

    hclog = Log('testLog', True)
    hclog.error ('this is a test error message without ip')
    hclog.debug('this  is a test debug message without ip')
    hclog.error ('this is a test error message with ip', '1.1.1.1')
    hclog.debug('this  is a test debug message with ip', '1.1.1.1')