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


class EchoHandler(SocketServer.DatagramRequestHandler):
    """
    Echo server class
    """
    global Not_Found
    Not_Found = "SIP/2.0 404 User Not Found\r\n"
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def handle(self):
        #ip = self.client_address[0]
        #puerto = str(self.client_address[1])
        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            LINE = self.rfile.read()
            lista = LINE.split(' ')
            if LINE:
		        #Guarda la información registrada y la IP en un diccionario
		        if lista[0] == "REGISTER":
		            direccion = lista[1].split(':')[1]
		            puerto = lista[1].split(':')[2]
		            expires = int(lista[3])
		            ip_puerto = (self.client_address[0], puerto)
		            USUARIOS[direccion] = ip_puerto
		            if expires != 0:
		                #Escribo en el log
		                fichero.write(str(time1) + ' Starting...\r\n')
		                fichero.write(str(time1) + ' Receive from ' + ip_puerto[0]
		                + ':' + ip_puerto[1] + ': ' + LINE)
		                #Envío 200 OK
		                reply = 'SIP/2.0 200 OK\r\n\r\n'
		                print 'Enviando: ' + reply + ' a: ' + ip_puerto[0] + ' ' + ip_puerto[1]
		                self.wfile.write(reply)
		                fichero.write(str(time1) + ' Send to ' + ip_puerto[0] + ":"
		                + ip_puerto[1] + ": " + reply)
		                fichero1 = open(cHandler.path_database, 'a')
		                #fichero1.write("DIRECCIÓN\tIP\tPUERTO\tFECHA\tEXPIRES\r\n")
		                fichero1.write(str(direccion) + '\t')
		                fichero1.write(str(ip_puerto[0]) + '\t')
		                fichero1.write(str(ip_puerto[1]) + '\t')
		                fichero1.write(time.strftime("%Y%m%d%H%M%S", time.localtime()) + '\t')
		                fichero1.write(str(expires) + '\r\n')
		                fichero1.close()
		            elif expires == 0:
		                del USUARIOS[direccion]
		                #Envío 200 OK
		                reply = 'SIP/2.0 200 OK\r\n\r\n'
		                print 'Enviando: ' + reply + ' a: ' + ip_puerto[0] + ' ' + ip_puerto[1]
		                self.wfile.write(reply)
                        #Escribo en log
		                fichero.write(str(time1) + ' Send to ' + ip_puerto[0] + ":"
		                + ip_puerto[1] + ": " + reply)
            elif not LINE:
                break

            if LINE:
                if lista[0] == "INVITE":
		            en_lista = False
		            invitado = lista[1].split(':')[1]
		            #print invitado

		            for i in USUARIOS:
		                if invitado == i:
		                    en_lista = True
		            if en_lista:
		                self.my_socket.setsockopt(socket.SOL_SOCKET,
		                                          socket.SO_REUSEADDR, 1)
		                self.my_socket.connect((USUARIOS[invitado][0],
		                                        int(USUARIOS[invitado][1])))
		                self.my_socket.send(LINE)
		                print 'Enviado: ' + LINE 
                        #Escribo en log
		                fichero.write(str(time1) + ' Send to ' + str(USUARIOS[invitado][0])
                        + ":" + str(USUARIOS[invitado][1]) + ": " + LINE)
		                #Recibo el mensaje
		                data = self.my_socket.recv(1024)
		                print 'Recibido: ' + data
		                #Envio al ua1 el mensaje que recibo
		                print "Enviado: " + data
		                self.wfile.write(data)
                        #Escribo en log
		                fichero.write(str(time1) + ' Send to ' + str(USUARIOS[invitado][0])
                        + ":" + str(USUARIOS[invitado][1]) + ": " + data)

		            else:
		                # Envio NOT_FOUND
		                self.wfile.write(Not_Found)
		                # Lo guardo en el fichero de seguimiento


            elif not LINE:
                break

if __name__ == "__main__":
    parser = make_parser()
    cHandler = ProxyHandler()
    parser.setContentHandler(cHandler)
    parser.parse(open(config))

    #Fichero de log
    time1 = time.strftime("%Y%m%d%H%M%S", time.localtime())
    fichero = open(cHandler.path_log, "a")

    USUARIOS = {}

if len(sys.argv) != 2 and sys.argv[1] != config:
    print('Usage: python uaserver.py config')
    print('SIP/2.0 400 Bad Request')
    sys.exit()
else:
    # Creamos servidor de eco y escuchamos
    serv = SocketServer.UDPServer((cHandler.ip_server,
    int(cHandler.puerto_server)), EchoHandler)
    print "MiServer listening...\r\n"
    serv.serve_forever()
