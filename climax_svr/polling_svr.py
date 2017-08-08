#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Simple web server that demonstrates how browser/server interactions
work for GET and POST requests. Use it as a starting point to create a
custom web server for handling specific requests but don't try to use
it for any production work.

You start by creating a simple index.html file in web directory
somewhere like you home directory: ~/www.

You then add an HTML file: ~/www/index.html. It can be very
simple. Something like this will do nicely:

   <!DOCTYPE html>
   <html>
     <head>
       <meta charset="utf-8">
       <title>WebServer Test</title>
     </head>
     <body>
       <p>Hello, world!</p>
     </body>
   </html>

At this point you have a basic web infrastructure with a single file
so you start the server and point to the ~/www root directory:

   $ webserver.py -r ~/www

This will start the web server listening on your localhost on port
8080. You can change both the host name and the port using the --host
and --port options. See the on-line help for more information (-h,
--help).

If you do not specify a root directory, it will use the directory that
you started the server from.

Now go to your browser and enter http://0.0.0.0:8080 on the command
line and you will see your page.

Try entering http://0.0.0.0:8080/info to see some server information.

You can also use http://127.0.0.1.

By default the server allows you to see directory listings if there is
no index.html or index.htm file. You can disable this by specifying
the --no-dirlist option.

If you want to see a directory listing of a directory that contains a
index.html or index.htm directory, type three trailing backslashes in
the URL like this: http://foo/bar/spam///. This will not work if the
--no-dirlist option is specified.

The default logging level is "info". You can change it using the
"--level" option.

The example below shows how to use a number of the switches to run a
server for host foobar on port 8080 with no directory listing
capability and very little output serving files from ~/www:

  $ hostname
  foobar
  $ webserver --host foobar --port 8080 --level warning --no-dirlist --rootdir ~/www

To daemonize a process, specify the -d or --daemonize option with a
process directory. That directory will contain the log (stdout), err
(stderr) and pid (process id) files for the daemon process. Here is an
example:

  $ hostname
  foobar
  $ webserver --host foobar --port 8080 --level warning --no-dirlist --rootdir ~/www --daemonize ~/www/logs
  $ ls ~/www/logs
  webserver-foobar-8080.err webserver-foobar-8080.log webserver-foobar-8080.pid
  
  To install configparser:   
      pip3 install Parser


'''
from pyasn1.compat.octets import null
import urllib
#import GW_DB

# LICENSE
#   Copyright (c) 2015 Joe Linoff
#   
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#   of this software and associated documentation files (the "Software"), to deal
#   in the Software without restriction, including without limitation the rights
#   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#   copies of the Software, and to permit persons to whom the Software is
#   furnished to do so, subject to the following conditions:
#   
#   The above copyright notice and this permission notice shall be included in
#   all copies or substantial portions of the Software.
#   
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#   THE SOFTWARE.

# VERSIONS
#   1.0  initial release
#   1.1  replace req with self in request handler, add favicon
#   1.2  added directory listings, added --no-dirlist, fixed plain text displays, logging level control, daemonize
VERSION = '1.3'

import argparse
#import BaseHTTPServer
import http.server
import socketserver
from urllib.parse import urlparse
import cgi
import logging
import os
import sys
#import parser
import configparser

from lxml import etree

from GW_DB.Dj_Server_DB import DB_mngt, DB_gw
from GW_Crypto.cryptoAES import AESCipher
from GW_CMD.GW_cmd import cmdTo_climax
from GW_answer.GW_answer import answerFrom_climax
from HCsettings import HcDB


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

        def do_HEAD(self):
            '''
            Handle a HEAD request.
            '''
            logging.debug('HEADER %s' % (self.path))
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
            logging.info('GET %s' % (self.path))

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
                logging.debug('TYPE %s' % (ctype))

            logging.debug('PATH %s' % (rpath))
            logging.debug('ARGS %d' % (len(args)))
            if len(args):
                i = 0
                for key in sorted(args):
                    logging.debug('ARG[%d] %s=%s' % (i, key, args[key]))
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
            logging.debug('POST received %s' % (self.path))

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

# init AES encryption vectors
            MAC= postvars["id".encode('iso-8859-1')]               
            AES= AESCipher(MAC[0])
# get xml frame 
            command_enc= postvars["strRecXML".encode('iso-8859-1')]
            
# decryt xml frame            
            command_xml = AES.decrypt(command_enc[0])
            logging.info("POST decrypted: MAC = {}".format(MAC) )    # remove trailling zeros
            logging.debug("{}\n".format(command_xml.replace('\x00',"")) )    # remove trailling zeros
     
# check if MAC is defined in DB_GW
            climax_xml= etree.fromstring(command_xml.encode('iso-8859-1'))

            elt=climax_xml.find("mac")
            MAC_xml = elt.get ("value", "0")
            
            if MAC_xml != "" :
            
                db_cur= DB_mngt(HcDB.config()) 
            
                if db_cur.echec:
                    sys.exit()
            
                gw=DB_gw(db_cur)
                gw_params = gw.search_gw(MAC_xml)
             
            
                if (gw_params):
                    logging.debug( "MAC {} found in Climax_DB".format(MAC_xml) )
                    mac_gwParams = gw_params[0]
                    acct2_gwParams = gw_params[1]
                    gw_ID_gwParams = gw_params[2]
                    user_ID_gwParams = gw_params[3]
                    rptip_ID_gwParams = gw_params[4]
                    
                    elt=climax_xml.find("rptipid")
                    rptipid_xml= elt.get ("value", "0")
                    
                    if rptipid_xml == "" or rptip_ID_gwParams == "":
                        logging.info("Register GW MAC : {}".format(MAC_xml))
   
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


                        logging.info("POST: Register sent to GW= {0}".format(server_resp) )
                    
                        
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
                                          
                        logging.debug("POST: Polling sent to GW= {0}\n".format(server_resp) )


                       
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
                    logging.info("Polling : MAC not found in DB {}".format(MAC_xml) )
                
                
                db_cur.close()
            
            logging.debug("POST: exit POST function\n\n\n" )
   
    return MyRequestHandler


def err(msg):
    '''
    Report an error message and exit.
    '''
    logging.debug('ERROR: %s' % (msg))
    sys.exit(1)


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

    parser.add_argument('-d', '--daemonize',
                        action='store',
                        type=str,
                        default='FALSE',
                        metavar='DIR',
                        help='daemonize this process, store the 3 run files (.log, .err, .pid) in DIR (default "%(default)s")')

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

    parser.add_argument('--no-dirlist',
                        action='store_true',
                        help='disable directory listings')

    parser.add_argument('-p', '--port',
                        action='store',
                        type=int,
                        default=8080,
                        help='port, default=%(default)s')

    parser.add_argument('-r', '--rootdir',
                        action='store',
                        type=str,
                        default=os.path.abspath('.'),
                        help='web directory root that contains the HTML/CSS/JS files %(default)s')

    parser.add_argument('-v', '--verbose',
                        action='count',
                        help='level of verbosity')

    parser.add_argument('-V', '--version',
                        action='version',
                        version='%(prog)s - v' + VERSION)

    opts = parser.parse_args()
    opts.rootdir = os.path.abspath(opts.rootdir)
    if not os.path.isdir(opts.rootdir):
        err('Root directory does not exist: ' + opts.rootdir)
    if opts.port < 1 or opts.port > 65535:
        err('Port is out of range [1..65535]: %d' % (opts.port))
    return opts


def httpd(opts):
    '''
    HTTP server
    '''
    RequestHandlerClass = make_request_handler_class(opts)
    server = http.server.HTTPServer((opts.host, opts.port), RequestHandlerClass)
    logging.info('Server starting %s:%s (level=%s)' % (opts.host, opts.port, opts.level))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
    logging.info('Server stopping %s:%s' % (opts.host, opts.port))


def get_logging_level(opts):
    '''
    Get the logging levels specified on the command line.
    The level can only be set once.
    '''
    if opts.level == 'notset':
        return logging.NOTSET
    elif opts.level == 'debug':
        return logging.DEBUG
    elif opts.level == 'info':
        return logging.INFO
    elif opts.level == 'warning':
        return logging.WARNING
    elif opts.level == 'error':
        return logging.ERROR
    elif opts.level == 'critical':
        return logging.CRITICAL


def daemonize(opts):
    '''
    Daemonize this process.

    CITATION: http://stackoverflow.com/questions/115974/what-would-be-the-simplest-way-to-daemonize-a-python-script-in-linux
    '''
    if os.path.exists(opts.daemonize) is False:
        err('directory does not exist: ' + opts.daemonize)

    if os.path.isdir(opts.daemonize) is False:
        err('not a directory: ' + opts.daemonize)

    bname = 'webserver-%s-%d' % (opts.host, opts.port)
    outfile = os.path.abspath(os.path.join(opts.daemonize, bname + '.log'))
    errfile = os.path.abspath(os.path.join(opts.daemonize, bname + '.err'))
    pidfile = os.path.abspath(os.path.join(opts.daemonize, bname + '.pid'))

    if os.path.exists(pidfile):
        err('pid file exists, cannot continue: ' + pidfile)
    if os.path.exists(outfile):
        os.unlink(outfile)
    if os.path.exists(errfile):
        os.unlink(errfile)

    if os.fork():
        sys.exit(0)  # exit the parent

    os.umask(0)
    os.setsid()
    if os.fork():
        sys.exit(0)  # exit the parent

    logging.debug('daemon pid %d' % (os.getpid()))

    sys.stdout.flush()
    sys.stderr.flush()

    stdin = file('/dev/null', 'r')
    stdout = file(outfile, 'a+')
    stderr = file(errfile, 'a+', 0)

    os.dup2(stdin.fileno(), sys.stdin.fileno())
    os.dup2(stdout.fileno(), sys.stdout.fileno())
    os.dup2(stderr.fileno(), sys.stderr.fileno())

    with open(pidfile, 'w') as ofp:
        ofp.write('%i' % (os.getpid()))

def main():
    ''' main entry '''
    opts = getopts()  
    
    if opts.daemonize != 'FALSE':
        daemonize(opts)
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=get_logging_level(opts))
    httpd(opts)


if __name__ == '__main__':
    main()  # this allows library functionality
