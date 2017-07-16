#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Check Status of the camera and reset it if too old

version 1.0
June 2017
G. De Vocht"""

import mysql.connector
import sys


def main(argv):

    db = mysql.connector.connect(host="localhost", user="hc", password="HCMGGDB9", database="hcdb_branch_cam")
    cursor = db.cursor()
    cursor.execute("""UPDATE camera_camera SET status = 0  where lastSeenTimestamp < now() - interval 1 minute and status = 1""")
    db.commit()
    db.close



if __name__ == "__main__":
   main(sys.argv)