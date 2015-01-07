#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""
Clase (y programa principal) para un servidor de eco
en UDP simple
"""

import SocketServer
import sys
import os
import time
import socket
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

config = sys.argv[1]


class ProxyHandler(ContentHandler):
    """
    Clase para manejar xml
    """

    def __init__(self):
        """
        Constructor. Inicializamos las variables
        """
        self.name_server = ''
        self.ip_server = ''
        self.puerto_server = 0
        self.path_database = ''
        self.passwdpath_database = ''
        self.path_log = ''

    def startElement(self, name, attrs):

        if name == 'server':
            self.name_server = attrs.get('name', "")
            self.ip_server = attrs.get('ip', "")
            self.puerto_server = attrs.get('puerto', "")
        elif name == 'database':
            self.path_database = attrs.get('path', "")
            self.passwdpath_database = attrs.get('passwdpath', "")
        elif name == 'log':
            self.path_log = attrs.get('path', "")



class SIPRegisterHandler(SocketServer.DatagramRequestHandler):
    """
    Echo server class
    """
    dict = {}
    direccion = ''
    ip = ''
    puerto = 0

    def register2file(self):
        fichero1 = open(cHandler.path_database, 'a')
        #fichero1.write("DIRECCIÓN\tIP\tPUERTO\tFECHA\tEXPIRES\r\n")
        fichero1.write(str(self.direccion) + '\t')
        fichero1.write(str(self.ip) + '\t')
        fichero1.write(str(self.puerto) + '\t')
        fichero1.write(time.strftime("%Y%m%d%H%M%S", time.localtime()))
        fichero1.write(str(self.exp) + '\r\n')
        fichero1.close()

    def handle(self):
        # Escribe dirección y puerto del cliente (de tupla client_address)
        #IP = self.client_address[0]
        #PUERTO = str(self.client_address[1])
        #print "IP: " + IP + " PUERTO: " + PUERTO
        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            line = self.rfile.read()
            lista = line.split()

            #Guarda la información registrada y la IP en un diccionario
            if lista[0] == "REGISTER":
                self.direccion = lista[1].split(':')[1]
                self.puerto = lista[1].split(':')[2]
                expires = int(lista[4])
                self.exp = expires
                self.ip = self.client_address[0]
                #puerto = str(self.client_address[1])
                #Escribo en el log
                fichero.write(str(time1) + ' Starting...\r\n')
                fichero.write(str(time1) + ' Receive from ' + self.ip + ':'
                + self.puerto + ': ' + line)
                if expires == 0:
                    if dict.has_keys(self.direccion):
                        del dict[self.direccion]
                        reply = 'SIP/2.0 200 OK\r\n\r\n'
                        print 'Enviando: ' + reply
                        #Escribo en el log
                        fichero.write(str(time1) + ' Send to ' + self.ip + ":"
                        + self.puerto + ": " + reply)
                    else:
                        reply = 'SIP/2.0 404 User Not Found\r\n'
                        print 'Enviando: ' + reply
                        #Escribo en el log
                        fichero.write(str(time1) + ' Send to ' + self.ip + ":"
                        + self.puerto + ": " + reply)
                else:
                    self.register2file()
                    reply = 'SIP/2.0 200 OK\r\n\r\n'
                    print 'Enviando: ' + reply
                    #Escribo en el log
                    fichero.write(str(time1) + ' Send to ' + self.ip + ":"
                    + self.puerto + ": " + reply)
                print "Enviado: " + reply
                my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                my_socket.connect(self.ip, int(self.puerto))
                my_socket.send(reply)
            #if lista[0] == "INVITE":


if __name__ == "__main__":
    parser = make_parser()
    cHandler = ProxyHandler()
    parser.setContentHandler(cHandler)
    parser.parse(open(config))

    #Fichero de log
    time1 = time.strftime("%Y%m%d%H%M%S", time.localtime())
    fichero = open(cHandler.path_log, "a")

if len(sys.argv) != 2 and sys.argv[1] != config:
    print('Usage: python uaserver.py config')
    print('SIP/2.0 400 Bad Request')
    sys.exit()
else:
    # Creamos servidor de eco y escuchamos
    serv = SocketServer.UDPServer((cHandler.ip_server,
    int(cHandler.puerto_server)), SIPRegisterHandler)
    print "Listening...\r\n"
    serv.serve_forever()
