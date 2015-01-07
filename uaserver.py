#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""
Clase (y programa principal) para un servidor de eco en UDP simple
"""

import SocketServer
import sys
import os
import time
from xml.sax import make_parser
from xml.sax.handler import ContentHandler


class ServerHandler(ContentHandler):
    """
    Clase para manejar xml
    """

    def __init__(self):
        """
        Constructor. Inicializamos las variables
        """
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
            lista = line.split()
            if not line:
                break
            else:
                if lista[0] == 'INVITE':
                    #Puerto adicional para recibir MP3
                    puerto_rtp = lista[11]
                    reply = 'SIP/2.0 100 Trying\r\n\r\n'
                    reply += 'SIP/2.0 180 Ringing\r\n\r\n'
                    reply += 'SIP/2.0 200 OK\r\n\r\n'
                    reply += 'Content-Type: application/sdp\r\n\r\n'
                    reply += 'v=0\r\n' + 'o=' + cHandler.username + ' '
                    reply += cHandler.ip_uaserver + '\r\n' + 's=misesion\r\n'
                    reply += 't=0\r\n' + 'm=audio ' + cHandler.puerto_rtpaudio
                    reply +=' RTP'
                    #Escribo en el log
                    fichero.write(str(time) + ' Received from '
                    + cHandler.ip_regproxy + ":"
                    + str(cHandler.puerto_regproxy) + ": " + line)
                    # Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
                    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    my_socket.connect((cHandler.ip_regproxy, int(cHandler.puerto_regproxy)))
                    #Envío el mensaje
                    my_socket.send(reply + '\r\n')
                    print 'Enviando: ' + reply
                    #Escribo en el log
                    fichero.write(str(time) + ' Send to '
                    + cHandler.ip_regproxy + ":"
                    + str(cHandler.puerto_regproxy) + ": " + reply)
                elif lista[0] == 'BYE':
                    reply = 'SIP/2.0 200 OK\r\n\r\n'
                    reply += 'Content-Type: application/sdp\r\n\r\n'
                    reply += 'v=0\r\n' + 'o=' + cHandler.username + ' '
                    reply += cHandler.ip_uaserver + '\r\n' + 's=misesion\r\n'
                    reply += 't=0\r\n' + 'm=audio ' + cHandler.puerto_rtpaudio
                    reply +=' RTP'
                    #Escribo en el log
                    fichero.write(str(time) + ' Received from '
                    + cHandler.ip_regproxy + ":"
                    + str(cHandler.puerto_regproxy) + ": " + line)
                    # Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
                    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    my_socket.connect((cHandler.ip_regproxy, int(cHandler.puerto_regproxy)))
                    #Envío el mensaje
                    my_socket.send(reply + '\r\n')
                    print 'Enviando: ' + reply
                    #Escribo en el log
                    fichero.write(str(time) + ' Send to '
                    + cHandler.ip_regproxy + ":"
                    + str(cHandler.puerto_regproxy) + ": " + reply)
                elif lista[0] == 'ACK':
                    aEjecutar = './mp32rtp -i ' + cHandler.ip_uaserver + ' -p '
                    aEjecutar += puerto_rtp + ' < '
                    aEjecutar += cHandler.audio
                    print "Vamos a ejecutar", aEjecutar
                    os.system(aEjecutar)
                    print "Ha terminado\r\n"
                else:
                    reply = 'SIP/2.0 405 Method Not Allowed'
                    #Escribo en el log
                    fichero.write(str(time) + ' Received from '
                    + cHandler.ip_regproxy + ":"
                    + str(cHandler.puerto_regproxy) + ": " + line)
                    # Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
                    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    my_socket.connect((cHandler.ip_regproxy, int(cHandler.puerto_regproxy)))
                    #Envío el mensaje
                    my_socket.send(reply + '\r\n')
                    print 'Enviando: ' + reply
                    #Escribo en el log
                    fichero.write(str(time) + ' Send to '
                    + cHandler.ip_regproxy + ":"
                    + str(cHandler.puerto_regproxy) + ": " + reply)


if __name__ == "__main__":
    parser = make_parser()
    cHandler = ServerHandler()
    parser.setContentHandler(cHandler)
    config = str(sys.argv[1])
    parser.parse(open(config))

    if len(sys.argv) != 2:
        print('Usage: python uaserver.py config')
    else:
        print "Listening...\r\n"

    #Fichero de log
    time = time.strftime("%Y%m%d%H%M%S", time.localtime())
    fichero = open(cHandler.path_log, "a")

    # Creamos servidor de eco y escuchamos
    serv = SocketServer.UDPServer((cHandler.ip_uaserver,
    int(cHandler.puerto_uaserver)), EchoHandler)
    serv.serve_forever()
