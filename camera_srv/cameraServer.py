#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""HTTP camera server classes.
Based on Python library http.server

version 1.0
June 2017
G. De Vocht"""

__version__ = "0.6"

__all__ = [
    "HTTPServer", "BaseHTTPRequestHandler",
    "SimpleHTTPRequestHandler",
]


import http.client
import socket # For gethostbyaddr()
import socketserver
import sys
import argparse
import time
import datetime
from http import HTTPStatus
from socketserver import ThreadingMixIn
import mysql.connector
from HCsettings import HcDB, HcLog
from GW_DB.Dj_Server_DB import DB_mngt
import logging
from HcLog import Log


#debug = False 
debug = True


class HTTPServer(socketserver.TCPServer):

    allow_reuse_address = 1    # Seems to make sense in testing environment

    def server_bind(self):
        """Override server_bind to store the server name."""
        socketserver.TCPServer.server_bind(self)
        host, port = self.server_address[:2]
        self.server_name = socket.getfqdn(host)
        self.server_port = port


class BaseHTTPRequestHandler(socketserver.StreamRequestHandler):
   

    # The Python system version, truncated to its first component.
    sys_version = "Python/" + sys.version.split()[0]

    # The server software version.  You may want to override this.
    # The format is multiple whitespace-separated strings,
    # where each string is of the form name[/version].
    server_version = "BaseHTTP/" + __version__

    # The default request version.  This only affects responses up until
    # the point where the request line is parsed, so it mainly decides what
    # the client gets back when sending a malformed request line.
    # Most web servers default to HTTP 0.9, i.e. don't send a status line.
    default_request_version = "HTTP/0.9"

    def parse_request(self):
        """Parse a request (internal).

        The request should be stored in self.raw_requestline; the results
        are in self.command, self.path, self.request_version and
        self.headers.

        Return True for success, False for failure; on failure, an
        error is sent back.

        """
        self.command = None  # set in case of error on the first line
        self.request_version = version = self.default_request_version
        self.close_connection = True
        requestline = str(self.raw_requestline, 'iso-8859-1')
        requestline = requestline.rstrip('\r\n')
        self.requestline = requestline
        words = requestline.split()
        
        if len(words) == 3:
            hclog.debug("command search")
            command, path, version = words
            try:
                
                self.command = command
                
                #extra GDV =====================================================
                """Used to catch the 200ok send by the camera """
                if command[:5] == 'HTTP/' and path == '200' and version =='OK':
                    version = command
                    self.command = "200ok"
                    hclog.debug("it is a 200 ok")
                    """Because the 200 ok is not understood as a command, we need to flush the input file
                        Readnew line until OK message appears"""
                    while True:
                        raw_requestline = self.rfile.readline()
                        requestline = raw_requestline.decode()
                        requestline = requestline.rstrip('\r\n')
                        if requestline == 'OK':
                            break
                    self.close_connection = False
                    return True
                #===============================================================
            
                            
                if version[:5] != 'HTTP/':
                    raise ValueError
                base_version_number = version.split('/', 1)[1]
                version_number = base_version_number.split(".")
                if len(version_number) != 2:
                    raise ValueError
                version_number = int(version_number[0]), int(version_number[1])
                
            except (ValueError, IndexError):
                self.send_error()
                return False
             
            if version_number >= (1, 1) and self.protocol_version >= "HTTP/1.1":
                self.close_connection = False
            if version_number >= (2, 0):
                self.send_error()
                return False
        
            self.command, self.path, self.request_version = command, path, version

            # Examine the headers and look for a Connection directive.
            try:
                self.headers = http.client.parse_headers(self.rfile,
                                                         _class=self.MessageClass)
            except http.client.LineTooLong as err:
                self.send_error()
                return False
            except http.client.HTTPException as err:
                self.send_error()
                return False
            
            conntype = self.headers.get('Connection', "")
            if conntype.lower() == 'close':
                self.close_connection = True
            elif (conntype.lower() == 'keep-alive' and
                  self.protocol_version >= "HTTP/1.1"):
                self.close_connection = False
            # Examine the headers and look for an Expect directive
            expect = self.headers.get('Expect', "")
            if (expect.lower() == "100-continue" and
                    self.protocol_version >= "HTTP/1.1" and
                    self.request_version >= "HTTP/1.1"):
                if not self.handle_expect_100():
                    return False
            return True
        else:
            #Bad format
            self.send_error()


    def handle_one_request(self):
        """Handle a single HTTP request.
        """
        try:
            self.raw_requestline = self.rfile.readline(65537)
            if len(self.raw_requestline) > 65536:
                self.requestline = ''
                self.request_version = ''
                self.command = ''
                self.send_error()
                return
            if not self.raw_requestline:
                self.close_connection = True
                return
            if not self.parse_request():
                # An error code has been sent, just exit
                return
            mname = 'do_' + self.command
            if not hasattr(self, mname):
                self.send_error()
                return
            method = getattr(self, mname)
            method()
            self.wfile.flush() #actually send the response if not already done.
        except socket.timeout as e:
            #a read or a write timed out.  Discard this connection
            hclog.debug("Request timed out: {}".format(e))
            self.close_connection = True
            return

    def handle(self):
        """Handle multiple requests if necessary."""
        self.close_connection = True

        self.handle_one_request()
        while not self.close_connection:
            self.handle_one_request()

    def send_error(self):
        hclog.error("Bad message received",self.address_string() )
        self.send_header('Connection', 'close')
        self.end_headers()
        

    def send_header(self, keyword, value):
        """Send a MIME header to the headers buffer."""
        
        if not hasattr(self, '_headers_buffer'):
            self._headers_buffer = []
        self._headers_buffer.append(
            ("%s: %s\r\n" % (keyword, value)).encode('latin-1', 'strict'))

        if keyword.lower() == 'connection':
            if value.lower() == 'close':
                self.close_connection = True
            elif value.lower() == 'keep-alive':
                self.close_connection = False

    def end_headers(self):
        """Send the blank line ending the MIME headers."""
        
        self._headers_buffer.append(b"\r\n")
        self.flush_headers()

    def flush_headers(self):
        if hasattr(self, '_headers_buffer'):
            self.wfile.write(b"".join(self._headers_buffer))
            self._headers_buffer = []

    def version_string(self):
        """Return the server software version string."""
        return self.server_version + ' ' + self.sys_version

    def address_string(self):
        """Return the client address."""

        return self.client_address[0]

    # Essentially static class variables

    # The version of the HTTP protocol we support.
    # Set this to HTTP/1.1 to enable automatic keepalive
    protocol_version = "HTTP/1.0"

    # MessageClass used to parse headers
    MessageClass = http.client.HTTPMessage

    # hack to maintain backwards compatibility
    responses = {
        v: (v.phrase, v.description)
        for v in HTTPStatus.__members__.values()
    }


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    #extra GDV =====================================================
    """Simple HTTP request handler """

    server_version = "SimpleHTTP/" + __version__
    
    
    def do_200ok(self):
        """nothing to do"""
	
                
    def do_POST(self):
              
        hclog.debug("-------- Handle POST in CameraServer.py-----------")
        data = self.rfile.readline()
        mac = data.decode().split("|")[0]
        mac = mac.upper()
        hclog.debug("Poll Camera : {}".format(mac))
        
        cursor= DB_mngt(HcDB.config()) 
        
        if cursor.echec:
            sys.exit(1)
            hclog.debug ("cannot open db")

        cursor.executerReq("""SELECT id from camera_camera WHERE CameraMac=%s""", (mac,))
        idCam = cursor.resultatReqOneRec()
        hclog.debug ("camera id: {}".format(idCam[0]))
        
        if idCam:

            ts = time.time()
            timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            #Update the camer status
            cursor.executerReq("""UPDATE camera_camera SET status = 1, lastSeenTimestamp = %s WHERE CameraMac=%s""", (timestamp, mac,))
            cursor.commit()
            hclog.debug("Timestamp update done")
            #Lookup for camera action
            cursor.executerReq("""SELECT id, action FROM camera_action_list WHERE camera_id=%s LIMIT 0, 1""", idCam)
            resp = cursor.resultatReqOneRec()

            
            if resp:
                answer = resp[1].replace("\\r\\n", "\r\n")
                self.wfile.write(answer.encode())
                self.send_header('Host', self.client_address[0])
                self.send_header('Authorization', 'Basic c3VwZXJhZG1pbjpzdXBlcmFkbWlu')
                self.send_header('Connection', 'Keep-Alive')
                self.end_headers()
                self.wfile.write("?commandid=934723039".encode())
                
                cursor.executerReq("""DELETE FROM camera_action_list WHERE id=%s""", (resp[0],))
                cursor.commit()
                hclog.info("Action for camera id {}, mac {}".format(idCam[0], mac) )
            else:
                self.close_connection = False
                hclog.debug("No action for camera id {}".format(idCam[0]))
            
            
        else:
            hclog.error("Camera not registred",self.address_string())
            
        cursor.close()
        
        
		#=====================================================



    
   

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """ This class allows to handle requests in separated threads.
        No further content needed, don't touch this. """

def get_logging_level():
    if debug:
        return logging.DEBUG
    else:
        return logging.ERROR

def run(HandlerClass=BaseHTTPRequestHandler,
         ServerClass=HTTPServer, protocol="HTTP/1.0", port=8000, bind=""):
    """Test the HTTP request handler class.

    This runs an HTTP server on port 8000 (or the port argument).

    """
    server_address = (bind, port)

    HandlerClass.protocol_version = protocol
    httpd = ThreadedHTTPServer(server_address, HandlerClass)
    sa = httpd.socket.getsockname()
    serve_message = "Serving HTTP on {host} port {port} (http://{host}:{port}/) ..."
    hclog.info(serve_message.format(host=sa[0], port=sa[1]))
    
    try:
            httpd.serve_forever()
    except KeyboardInterrupt:
            print("\nKeyboard interrupt received, exiting.")
            sys.exit(0)
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--bind', '-b', default='', metavar='ADDRESS',
                        help='Specify alternate bind address '
                             '[default: all interfaces]')
    parser.add_argument('port', action='store',
                        default=8000, type=int,
                        nargs='?',
                        help='Specify alternate port [default: 8000]')
    args = parser.parse_args()
    
        
    hclog = Log("camera_srv", debug)
    
    
    handler_class = SimpleHTTPRequestHandler
    run(HandlerClass=handler_class, port=args.port, bind=args.bind)
    
    
    
