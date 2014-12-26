#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""
Clase (y programa principal) para un servidor de eco en UDP simple
"""

import SocketServer
import sys
import os
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

config = sys.argv[2]


#Clase para manejar el xml
class ServerHandler(ContentHandler):

    def __init__(self):
        self.username = ''
        self.passwd = ''
        self.ip_uaserver = ''
        self.puerto_uaserver = 0
        self.puerto_rtpaudio = 0
        self.ip_regproxy = ''
        self.puerto_regproxy = 0
        self.path_log = ''
        self.path_audio = ''

    def startElement(self, name, attrs):

        if name == 'account':
            self.username = str(attrs.get('username', ""))
            self.passwd = str(attrs.get('passwd', ""))
        elif name == 'uaserver':
            self.ip_uaserver = str(attrs.get('ip', ""))
            self.puerto_uaserver = int(attrs.get('puerto', ""))
        elif name == 'rtpaudio':
            self.puerto_rtpaudio = int(attrs.get('puerto', ""))
        elif name == 'regproxy':
            self.ip_regproxy = str(attrs.get('ip', ""))
            self.puerto_regproxy = int(attrs.get('puerto', ""))
        elif name == 'log':
            self.path_log = str(attrs.get('path', ""))
        elif name == 'audio':
            self.path_audio = str(attrs.get('path', ""))


class EchoHandler(SocketServer.DatagramRequestHandler):
    """
    Echo server class
    """

    def handle(self):
        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            line = self.rfile.read()
            if not line:
                break
            else:
                if line.split(' ')[0] == 'INVITE':
                    reply = 'SIP/2.0 100 Trying\r\n\r\n'
                    reply += 'SIP/2.0 180 Ringing\r\n\r\n'
                    reply += 'SIP/2.0 200 OK\r\n\r\n'
                    reply += metodo + ' sip:' + sys.argv[3] + ' SIP/2.0\r\n'
                    reply += 'Content-Type: application/sdp\r\n\r\n'
                    reply += 'v=0\r\n' + 'o=' + cHandler.username + ' '
                    reply += cHandler.ip_uaserver + '\r\n' + 's=misesion\r\n'
                    reply += 't=0\r\n' + 'm=audio ' + cHandler.puerto_rtpaudio
                    reply +=' RTP'
                    self.wfile.write(reply)
                    print reply
                elif line.split(' ')[0] == 'BYE':
                    reply = 'SIP/2.0 200 OK\r\n\r\n'
                    reply += metodo + ' sip:' + sys.argv[3] + ' SIP/2.0\r\n'
                    reply += 'Content-Type: application/sdp\r\n\r\n'
                    reply += 'v=0\r\n' + 'o=' + cHandler.username + ' '
                    reply += cHandler.ip_uaserver + '\r\n' + 's=misesion\r\n'
                    reply += 't=0\r\n' + 'm=audio ' + cHandler.puerto_rtpaudio
                    reply +=' RTP'
                    self.wfile.write(reply)
                    print reply
                elif line.split(' ')[0] == 'ACK':
                    aEjecutar = './mp32rtp -i ' + IP + ' -p 23032 < '
                    aEjecutar += cHandler.audio
                    print "Vamos a ejecutar", aEjecutar
                    os.system(aEjecutar)
                    print "Ha terminado\r\n"
                else:
                    reply = 'SIP/2.0 405 Method Not Allowed'
                    self.wfile.write(reply)
                    print reply

if __name__ == "__main__":
    parser = make_parser()
    cHandler = ServerHandler()
    parser.setContentHandler(cHandler)
    parser.parse(open(config))
    # Creamos servidor de eco y escuchamos
    serv = SocketServer.UDPServer((IP, puerto), EchoHandler)
    print "Listening...\r\n"
    serv.serve_forever()
