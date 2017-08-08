#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class Notifier:
    __conf = {
        "CLIENT_ID" : "tECLyAst04Lkfv5K_VgftPkc7Swa",
        "CLIENT_SECRET" : "Y4oy9qhXJs3BEDbcgVLyzoJ4DMwa"
    }
    @staticmethod
    def config(name):
        return Notifier.__conf[name]


class HcDB:
    __conf = {
        "host" :"localhost",
        "database" : "climax_gw",
        "user" : "gw",
        "password": "test"
    }

    @staticmethod
    def config():
        return HcDB.__conf  
    
    
class Rpt_svr:
    __conf = {
        "port" : "27017",
        "ip" : "192.168.157.4",
    }
    @staticmethod
    def config(name):
        return Rpt_svr.__conf[name]


"""
class HcDB:
    __conf = {
        "username": "",
        "password": "",
        "MYSQL_PORT": 3306,
        "MYSQL_DATABASE": 'mydb',
        "MYSQL_DATABASE_TABLES": ['tb_users', 'tb_groups']
    }

    __setters = ["username", "password"]

    @staticmethod
    def config(name):
        return HcDB.__conf[name]
    
    @staticmethod
    def set(name, value):
        if name in HcDB.__setters:
            HcDB.__conf[name] = value
        else:
            raise NameError("Name not accepted in set() method")


"""

"""
  And then usage is:

if __name__ == "__main__":
  # from config import HcDB
  App.config("MYSQL_PORT")     # return 3306
  App.set("username", "hi")    # set new username value
  App.config("username")       # return "hi"
  App.set("MYSQL_PORT", "abc") # this raises NameError

"""

