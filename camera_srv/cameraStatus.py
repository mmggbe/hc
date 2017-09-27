#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Check Status of the camera and reset it if too old

version 1.0
June 2017
G. De Vocht"""

import mysql.connector
import sys

from HCsettings import HcDB
from GW_DB.Dj_Server_DB import DB_mngt

def main(argv):

#    db = mysql.connector.connect(host="localhost", user="hc", password="HCMGGDB9", database="hcdb_branch_cam")
    db_cursor= DB_mngt(HcDB.config()) 
    if db_cursor.echec:
        sys.exit(1)
        
#    cursor = db.cursor()
#    cursor.execute("""UPDATE camera_camera SET status = 0  where lastSeenTimestamp < now() - interval 1 minute and status = 1""")
    db_cursor.executerReq("""UPDATE camera_camera SET status = 0  where lastSeenTimestamp < now() - interval 1 minute and status = 1""")
#    db.commit()
    db_cursor.commit()
 #   db.close
    db_cursor.close()


if __name__ == "__main__":
   main(sys.argv)