#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Simple web server fro Climax GW
'''

VERSION = '2.0'

from pyasn1.compat.octets import null
import urllib


import http.server
import socket
import socketserver
from socketserver import ThreadingMixIn

import argparse
import configparser
from urllib.parse import urlparse
from lxml import etree

import cgi
import logging
from logging.handlers import TimedRotatingFileHandler

import os
import sys

from GW_DB.Dj_Server_DB import DB_mngt, DB_gw
from GW_Crypto.cryptoAES import AESCipher
from GW_CMD.GW_cmd import cmdTo_climax
from GW_answer.GW_answer import answerFrom_climax
#from HcLog import Log

from HCsettings import HcDB, HcLog



def make_request_handler_class(opts):
    '''
    Factory to make the request handler and add arguments to it.

    It exists to allow the handler to access the opts.path variable
    locally.
    '''
    class MyRequestHandler(http.server.BaseHTTPRequestHandler):
        '''
        Factory generated request handler class that contain
        additional class variables.
        '''
        m_opts = opts
        
        def setup(self):
            http.server.BaseHTTPRequestHandler.setup(self)
            self.request.settimeout(60)

        def do_HEAD(self):
            '''
            Handle a HEAD request.
            '''
            hclog.info("HEADER {} {}".format(self.path, self.client_address[0]))
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()


        def info(self):
            '''
            Display some useful server information.

            http://127.0.0.1:8080/info
            '''
            self.wfile.write(b'<html>')
            self.wfile.write(b'  <head>')
            self.wfile.write(b'    <title>Server Info</title>')
            self.wfile.write(b'  </head>')
            self.wfile.write(b'  <body>')
            self.wfile.write(b'    <table>')
            self.wfile.write(b'      <tbody>')
            self.wfile.write(b'        <tr>')
            self.wfile.write(b'          <td>client_address</td>')
            self.wfile.write(b'          <td>%r</td>' % (repr(self.client_address)))
            self.wfile.write(b'        </tr>')
            self.wfile.write(b'        <tr>')
            self.wfile.write(b'          <td>command</td>')
            self.wfile.write(b'          <td>%r</td>' % (repr(self.command)))
            self.wfile.write(b'        </tr>')
            self.wfile.write(b'        <tr>')
            self.wfile.write(b'          <td>headers</td>')
            self.wfile.write(b'          <td>%r</td>' % (repr(self.headers)))
            self.wfile.write(b'        </tr>')
            self.wfile.write(b'        <tr>')
            self.wfile.write(b'          <td>path</td>')
            self.wfile.write(b'          <td>%r</td>' % (repr(self.path)))
            self.wfile.write(b'        </tr>')
            self.wfile.write(b'        <tr>')
            self.wfile.write(b'          <td>server_version</td>')
            self.wfile.write(b'          <td>%r</td>' % (repr(self.server_version)))
            self.wfile.write(b'        </tr>')
            self.wfile.write(b'        <tr>')
            self.wfile.write(b'          <td>sys_version</td>')
            self.wfile.write(b'          <td>%r</td>' % (repr(self.sys_version)))
            self.wfile.write(b'        </tr>')
            self.wfile.write(b'      </tbody>')
            self.wfile.write(b'    </table>')
            self.wfile.write(b'  </body>')
            self.wfile.write(b'</html>')

        def do_GET(self):
            '''
            Handle a GET request.
            '''
            hclog.info("GET {} {}".format(self.path, self.client_address[0]))

            # Parse out the arguments.
            # The arguments follow a '?' in the URL. Here is an example:
            #   http://example.com?arg1=val1
            args = {}
            idx = self.path.find('?')
            if idx >= 0:
                rpath = self.path[:idx]
                args = cgi.parse_qs(self.path[idx+1:])
            else:
                rpath = self.path

            # Print out logging information about the path and args.
            if 'content-type' in self.headers:
                ctype, _ = cgi.parse_header(self.headers['content-type'])
                hclog.debug('TYPE %s' % (ctype))

            hclog.debug('PATH %s' % (rpath))
            hclog.debug('ARGS %d' % (len(args)))
            if len(args):
                i = 0
                for key in sorted(args):
                    hclog.debug('ARG[%d] %s=%s' % (i, key, args[key]))
                    i += 1

            # Check to see whether the file is stored locally,
            # if it is, display it.
            # There is special handling for http://127.0.0.1/info. That URL
            # displays some internal information.
            if self.path == '/info' or self.path == '/info/':
                self.send_response(200)  # OK
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.info()
            

       
        def do_POST(self):
            '''
            Handle POST requests.
            '''
            hclog.info("POST {} [client {}]".format( self.path, self.client_address[0]) )

            # CITATION: http://stackoverflow.com/questions/4233218/python-basehttprequesthandler-post-variables
            ctype, pdict = cgi.parse_header(self.headers['content-type'])
            if ctype == 'multipart/form-data':
                postvars = cgi.parse_multipart(self.rfile, pdict)
            elif ctype == 'application/x-www-form-urlencoded':
                length = int(self.headers['content-length'])
                raw_cmd=self.rfile.read(length)
                postvars =  urllib.parse.parse_qs(raw_cmd, encoding='iso-8859-1', keep_blank_values=1)

            else:
                postvars = {}

            try:
# init AES encryption vectors
                MAC= postvars["id".encode('iso-8859-1')]               
                AES= AESCipher(MAC[0])
# get xml frame 
                command_enc= postvars["strRecXML".encode('iso-8859-1')]
                
# decrypt xml frame            
                command_xml = AES.decrypt(command_enc[0])
                hclog.info("POST decrypted: MAC = {}".format(MAC) )    # remove trailling zeros
                hclog.debug("{}\n".format(command_xml.replace('\x00',"")) )    # remove trailling zeros
         
                try:
# check if MAC is defined in DB_GW
                    climax_xml= etree.fromstring(command_xml.encode('iso-8859-1').replace(b'&', b''))  # remove "&" Ampersand
         
                    elt=climax_xml.find("mac")
                    MAC_xml = elt.get ("value", "0")
                    
                    if MAC_xml != "" :
                    
    
                        db_cur= DB_mngt(HcDB.config()) 
                    
                        if db_cur.echec:
                            hclog.info("Unable to open DB" )
                            sys.exit()
                    
                        gw=DB_gw(db_cur)
                        gw_params = gw.search_gw(MAC_xml)
                     
                    
                        if (gw_params):
                            hclog.debug( "MAC {} found in Climax_DB".format(MAC_xml) )
                            mac_gwParams = gw_params[0]
                            acct2_gwParams = gw_params[1]
                            gw_ID_gwParams = gw_params[2]
                            user_ID_gwParams = gw_params[3]
                            rptip_ID_gwParams = gw_params[4]
                            
                            elt=climax_xml.find("rptipid")
                            rptipid_xml= elt.get ("value", "0")
                            
                            if rptipid_xml == "" or rptip_ID_gwParams == "":
                                hclog.info("Register GW MAC : {}".format(MAC_xml))
           
                                # get acct2 number in config file					
                                config = configparser.ConfigParser()
                                config.read("config.ini")
                                last_acct2_created=config.get('other', 'last_acct2_created')
                                acct2= int(last_acct2_created)+1
                                last_acct2_created=str(acct2)	
                                # update incremented acct2 number in config for next time...
                                config.set('other','last_acct2_created',last_acct2_created)
                             
                                # get rptipid (Internet reporting ID) to provision the gw
                                rptipid_xml=config.get('other', 'rptipid')
                                
                                # save the updated values                      							
                                cfgfile = open("config.ini",'w')
                                
                                config.write(cfgfile)
                                cfgfile.close()
        
                                cmd=cmdTo_climax(db_cur, MAC_xml, user_ID_gwParams, gw_ID_gwParams,rptipid_xml)
                                
                                server_resp=cmd.autoRegister(rptipid_xml,last_acct2_created)
                                gw.upd_account_gw(MAC_xml, rptipid_xml,last_acct2_created)
        
        
                                hclog.info("POST: Register sent to GW= {0}".format(server_resp) )
                            
                                
                            else:       # GW is registered, analyse GW answer                        
                                answer_gw = answerFrom_climax(db_cur, MAC_xml, user_ID_gwParams, gw_ID_gwParams) 
                                cmdTo_gw = cmdTo_climax(db_cur, MAC_xml, user_ID_gwParams, gw_ID_gwParams,rptip_ID_gwParams)                                              
        
                                elt=climax_xml.find("commands")                       
                                if elt != None:                     # received cmd to process
                                    answer_gw.parsing(elt)
                                                                    # get from the queue the commands to be sent 
                                server_resp = cmdTo_gw.server_cmd()
                                if server_resp == None:
                                    server_resp=cmdTo_gw.polling(rptip_ID_gwParams)
                                                  
                                hclog.debug("POST: Polling sent to GW= {0}\n".format(server_resp) )
        
        
                               
                            AES= AESCipher(MAC[0]) 
                            server_xml_resp = server_resp.encode('iso-8859-1') 
                            command = AES.encrypt(server_xml_resp)  
                            
                            self.send_response(200)  # OK # bud display IP address of the GW , Why???  
                                                    # according to doc : text/xml , but according to trace text/html              
                            self.send_header('Content-type', 'text/xml; charset=utf-8')
                            self.send_header('Content-Length', "{0}".format(len(command)) )
                            self.send_header('Set-Cookies', 'path=/')
                            self.end_headers()
                            self.wfile.write(command)
        
        
                         
                        else:
                            hclog.info("Polling : MAC not found in DB {}".format(MAC_xml) )
        
                        db_cur.close()
                
                except:
                    hclog.info("ERROR : unexpected error in parsing GW answer")   
                    
            except:
                hclog.info("ERROR : unexpected error in GW answer : bad field or encryption")   
 
            
            hclog.debug("POST: exit POST function\n\n\n" )
   
    return MyRequestHandler

def err(msg):
    '''
    Report an error message and exit.
    '''
    hclog.debug('ERROR: %s' % (msg))
    sys.exit(1)
    

class HTTPServer(socketserver.TCPServer):

    allow_reuse_address = 1    # Seems to make sense in testing environment
    

    def server_bind(self):
        """Override server_bind to store the server name."""
        socketserver.TCPServer.server_bind(self)
        host, port = self.server_address[:2]
        self.server_name = socket.getfqdn(host)
        self.server_port = port

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """ This class allows to handle requests in separated threads.
        No further content needed, don't touch this. """
    pass

def httpd(opts):
    '''
    HTTP server
    '''
    RequestHandlerClass = make_request_handler_class(opts)
#    server = http.server.HTTPServer((opts.host, opts.port), RequestHandlerClass)
    server= ThreadedHTTPServer((opts.host, opts.port), RequestHandlerClass)  
    print('Server starting %s:%s (level=%s)' % (opts.host, opts.port, opts.level))
    hclog.info('Server starting %s:%s (level=%s)' % (opts.host, opts.port, opts.level))
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
    hclog.info('Server stopping %s:%s' % (opts.host, opts.port))


def getopts():
    '''
    Get the command line options.
    '''

    # Get the help from the module documentation.
    this = os.path.basename(sys.argv[0])
    description = ('description:%s' % '\n  '.join(__doc__.split('\n')))
    epilog = ' '
    rawd = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(formatter_class=rawd,
                                     description=description,
                                     epilog=epilog)

    parser.add_argument('-H', '--host',
                        action='store',
                        type=str,
                        default='localhost',
                        help='hostname, default=%(default)s')

    parser.add_argument('-l', '--level',
                        action='store',
                        type=str,
                        default='info',
                        choices=['notset', 'debug', 'info', 'warning', 'error', 'critical',],
                        help='define the logging level, the default is %(default)s')

    parser.add_argument('-p', '--port',
                        action='store',
                        type=int,
                        default=8080,
                        help='port, default=%(default)s')

    parser.add_argument('-V', '--version',
                        action='version',
                        version='%(prog)s - v' + VERSION)

    opts = parser.parse_args()

    if opts.port < 1 or opts.port > 65535:
        err('Port is out of range [1..65535]: %d' % (opts.port))
    return opts





def main():
    ''' main entry '''
    
    opts = getopts() 
     
    logPath= HcLog.config("logPath")
    retentionTime = int(HcLog.config("retentionTime"))
    moduleName = "polling_svr"
    
    global hclog
    hclog = logging.getLogger()   # must be the rotlogger, otherwise sub-modules will not benefit from the config.
     
    handler = TimedRotatingFileHandler(logPath + moduleName + '.log',
                                  when='midnight',
                                  backupCount=retentionTime)   
    if opts.level == 'debug':
        hclog.setLevel(logging.DEBUG) 
        handler.setLevel(logging.DEBUG) 
    else:
        hclog.setLevel(logging.INFO)
        handler.setLevel(logging.INFO)      
        
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s',datefmt='%b %d %H:%M:%S')
    handler.setFormatter(formatter)

    hclog.addHandler(handler)     
 
    httpd(opts)


if __name__ == '__main__':
    main()  # this allows library functionality
