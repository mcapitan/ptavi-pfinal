#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""
Programa cliente que abre un socket a un servidor
"""

import socket
import sys
import os
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

config = str(sys.argv[1])
metodo = str(sys.argv[2])
opcion = (sys.argv[3])


#Clase para manejar el xml
class ClientHandler(ContentHandler):

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


if __name__ == "__main__":
    parser = make_parser()
    cHandler = ClientHandler()
    parser.setContentHandler(cHandler)
    parser.parse(open(config))

if len(sys.argv) != 4:
    print('Usage: python uaclient.py config method option')
    sys.exit()
else:
    # Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    my_socket.connect((cHandler.ip_regproxy, int(cHandler.puerto_regproxy)))

    # Contenido que vamos a enviar
    try:
        if metodo == 'REGISTER':
            LINE = metodo + ' sip:' + cHandler.username + ":"
            LINE += cHandler.ip_uaserver + ' SIP/2.0\r\n'
            LINE += 'Expires: ' + sys.argv[3]
            #Envío el mensaje
            my_socket.send(LINE + '\r\n')
            print 'Enviando: ' + data
            #Recibo el mensaje
            data = my_socket.recv(1024)
            print 'Recibido: ' + data
        elif metodo == 'INVITE':
            LINE = metodo + ' sip:' + sys.argv[3] + ' SIP/2.0\r\n'
            LINE += 'Content-Type: application/sdp\r\n\r\n'
            LINE += 'v=0\r\n' + 'o=' + cHandler.username + ' '
            LINE += cHandler.ip_uaserver + '\r\n' + 's=misesion\r\n'
            LINE += 't=0\r\n' + 'm=audio ' + cHandler.puerto_rtpaudio + ' RTP'
            #Envío el mensaje
            my_socket.send(LINE + '\r\n')
            print 'Enviando: ' + data
            #Recibo el mensaje
            data = my_socket.recv(1024)
            print 'Recibido: ' + data
            #Envío el ACK
            LINE1 = 'ACK sip:' + sys.argv[3] + ' SIP/2.0'
            my_socket.send(LINE1 + '\r\n')
            print 'Enviando: ' + LINE1
            #data = my_socket.recv(1024)
            #print 'Recibido: ', data
        elif metodo == 'BYE':
            LINE = metodo + ' sip:' + sys.argv[3] + ' SIP/2.0\r\n'
            #Envío el mensaje
            my_socket.send(LINE + '\r\n')
            print 'Enviando: ' + data
            #Recibo el mensaje
            data = my_socket.recv(1024)
            print 'Recibido: ' + data
    #except socket.error:
        #print 'Error: No server listening at ' + IPreceptor + ' port ' + puertoSIP

    print "Terminando socket..."

    # Cerramos todo
    my_socket.close()
    print "Fin."
