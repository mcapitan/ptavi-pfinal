#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""
Programa cliente que abre un socket a un servidor
"""

import socket
import sys
import os
import time
from xml.sax import make_parser
from xml.sax.handler import ContentHandler


class ClientHandler(ContentHandler):
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
            self.username = attrs.get('username', "")
            self.passwd = attrs.get('passwd', "")
        elif name == 'uaserver':
            self.ip_uaserver = attrs.get('ip', "")
            self.puerto_uaserver = attrs.get('puerto', "")
        elif name == 'rtpaudio':
            self.puerto_rtpaudio = attrs.get('puerto', "")
        elif name == 'regproxy':
            self.ip_regproxy = attrs.get('ip', "")
            self.puerto_regproxy = attrs.get('puerto', "")
        elif name == 'log':
            self.path_log = attrs.get('path', "")
        elif name == 'audio':
            self.path_audio = attrs.get('path', "")


if __name__ == "__main__":
    parser = make_parser()
    cHandler = ClientHandler()
    parser.setContentHandler(cHandler)
    config = str(sys.argv[1])
    parser.parse(open(config))

    if len(sys.argv) != 4:
        print('Usage: python uaclient.py config method option')
        sys.exit()

    metodo = str(sys.argv[2])
    opcion = (sys.argv[3])

    # Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    my_socket.connect((cHandler.ip_regproxy, int(cHandler.puerto_regproxy)))

    #Fichero de log
    time = time.strftime("%Y%m%d%H%M%S", time.localtime())
    fichero = open(cHandler.path_log, "a")

    # Contenido que vamos a enviar
    try:
        if metodo == 'REGISTER':
            LINE = metodo + ' sip:' + cHandler.username + ":"
            LINE += cHandler.puerto_uaserver + ' SIP/2.0\r\n'
            LINE += 'Expires: ' + opcion + '\r\n'
            #Envío el mensaje
            my_socket.send(LINE + '\r\n')
            print 'Enviando: ' + LINE
            #Escribo en el log
            fichero.write(str(time) + ' Starting...\r\n')
            fichero.write(str(time) + ' Send to ' + cHandler.ip_regproxy + ":"
            + str(cHandler.puerto_regproxy) + ": " + LINE)
            #Recibo el mensaje
            data = my_socket.recv(1024)
            print 'Recibido: ' + data
            #Escribo en el log
            fichero.write(str(time) + ' Received from ' + cHandler.ip_regproxy
            + ":" + str(cHandler.puerto_regproxy) + ": " + data)
        elif metodo == 'INVITE':
            LINE = metodo + ' sip:' + opcion + ' SIP/2.0\r\n'
            LINE += 'Content-Type: application/sdp\r\n\r\n'
            LINE += 'v=0\r\n' + 'o=' + cHandler.username + ' '
            LINE += cHandler.ip_uaserver + '\r\n' + 's=misesion\r\n'
            LINE += 't=0\r\n' + 'm=audio ' + str(cHandler.puerto_rtpaudio)
            LINE += ' RTP'
            #Envío el mensaje
            my_socket.send(LINE + '\r\n')
            print 'Enviando: ' + LINE
            #Escribo en el log
            fichero.write(str(time) + ' Send to ' + cHandler.ip_regproxy + ":"
            + str(cHandler.puerto_regproxy) + ": " + LINE + '\r\n')
            #Recibo el mensaje
            data = my_socket.recv(1024)
            print 'Recibido: ' + data
            #Escribo en el log
            fichero.write(str(time) + ' Received from ' + cHandler.ip_regproxy
            + ":" + str(cHandler.puerto_regproxy) + ": " + data)
            #Envío el ACK
            LINE1 = 'ACK sip:' + opcion + ' SIP/2.0'
            my_socket.send(LINE1 + '\r\n')
            print 'Enviando: ' + LINE1
            #Intercambio de RTP
            aEjecutar = './mp32rtp -i ' + cHandler.ip_uaserver + ' -p '
            aEjecutar += cHandler.puerto_uaserver + ' < '
            aEjecutar += cHandler.audio
            print "Vamos a ejecutar", aEjecutar
            os.system(aEjecutar)
            print "Ha terminado\r\n"
            #data = my_socket.recv(1024)
            #print 'Recibido: ', data
        elif metodo == 'BYE':
            LINE = metodo + ' sip:' + opcion + ' SIP/2.0\r\n'
            #Envío el mensaje
            my_socket.send(LINE + '\r\n')
            print 'Enviando: ' + LINE
            #Escribo en el log
            fichero.write(str(time) + ' Send to ' + cHandler.ip_regproxy + ":"
            + str(cHandler.puerto_regproxy) + ": " + LINE)
            #Recibo el mensaje
            data = my_socket.recv(1024)
            print 'Recibido: ' + data
            #Escribo en el log
            fichero.write(str(time) + ' Received from ' + cHandler.ip_regproxy
            + ":" + str(cHandler.puerto_regproxy) + ": " + data)
            fichero.write(str(time) + ' Finishing.\r\n')
    except socket.error:
        print ('Error: No server listening at ' + cHandler.ip_uaserver +
        ' port ' + str(cHandler.puerto_uaserver) + '\r\n')
        #Escribo en el log
        fichero.write('Error: No server listening at ' + cHandler.ip_uaserver
        + str(cHandler.puerto_uaserver) + '\r\n')

    print "Terminando socket..."

    # Cerramos todo
    my_socket.close()
    print "Fin."
