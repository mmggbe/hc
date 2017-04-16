#!/usr/bin/env python
"""
Very simple HTTP server in python.

Usage::
    ./dummy-web-server.py [<port>]

Send a GET request::
    curl http://localhost

Send a HEAD request::
    curl -I http://localhost

Send a POST request::
    curl -d "foo=bar&bin=baz" http://localhost

"""
from BaseHTTPServerV2 import BaseHTTPRequestHandler, HTTPServer
import SocketServer
import mysql.connector
import time

from SocketServer import ThreadingMixIn
import threading

class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        self.wfile.write("<html><body><h1>hi!</h1></body></html>")
		
	#extra GDV =====================================================
    def do_200ok(self):
        print '200 ok'
	#=====================================================
	
    def do_HEAD(self):
        self._set_headers()
        
    def do_POST(self):
              
        #extra GDV =====================================================
        self.log_error("code %s, message %s", "gdv:", "Handle POST in server.py")
        data = self.rfile.readline()
        mac = data.split("|")[0]
        mac = mac.upper()
        self.log_error("code %s, message %s", "gdv:", mac)
        
        db = mysql.connector.connect(host="localhost", user="dbuser", password="00Proximus", database="HOMEAUTO")
        cursor = db.cursor()
        cursor.execute("""SELECT id from camera_camera WHERE CameraMac=%s""", (mac,))
        idCam = cursor.fetchone()
        if idCam:
            print idCam
            now = time.strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""UPDATE camera_camera SET status=1, lastSeenTimestamp=%s WHERE CameraMac=%s""", (now,mac,))
            db.commit()
            cursor.execute("""SELECT id, action FROM camera_action_list WHERE cameraID_id=%s LIMIT 0, 1""", idCam)
            resp = cursor.fetchone()
            if resp:
                print "Resp[0]:" + str(resp[0])
                print "Resp[1]:" + resp[1]
                answer = resp[1].replace("\\r\\n", "\r\n")
                self.wfile.write(answer)
                print "DELETE FROM camera_action_list WHERE id=" + str(resp[0])
                cursor.execute("""DELETE FROM camera_action_list WHERE id=%s""", (resp[0],))
                db.commit()
            else:
                #self.wfile.write("GET /adm/retrieve_start.cgi?pre_second=1&post_second=0 HTTP/1.1\r\n")
                print 'No action for the camera'
            
            
        else:
            print ('no record')
        db.close
        
        #self.send_response_cam(200)
        #self.wfile.write("GET /adm/retrieve_start.cgi?pre_second=1&post_second=0 HTTP/1.1\r\n")
        self.send_header('Host', self.client_address[0])
        self.send_header('Authorization', 'Basic c3VwZXJhZG1pbjpzdXBlcmFkbWlu')
        self.send_header('connection', 'keep-alive')
        self.end_headers()
        self.wfile.write("?commandid=934723039")
		#=====================================================


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """ This class allows to handle requests in separated threads.
        No further content needed, don't touch this. """
        
def run(server_class=HTTPServer, handler_class=S, port=80):
    server_address = ('', port)
    httpd = ThreadedHTTPServer(server_address, handler_class)
    print 'Starting httpd...'
    httpd.serve_forever()

if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()

