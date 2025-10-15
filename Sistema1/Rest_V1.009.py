PuertoEscuchaLiderSupervivencia=38020
PuertoEscuchaSeguidorBuscaLider=44444
PuertoEscuchaGeneralSeguidor=37020
TiempoDeConsultaSupervivencia=5
PuertoEscuchaSeguidorPreguntaSupervivencia=39020
PuertoEscuchaParticularCoordinador=36020
import distutils.log
import json
import os
from pickle import TRUE
import socket
import threading
import time
import logging
import random
EscuchaGeneralSeguidorSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
EscuchaGeneralSeguidorSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    
message="nca"
EscuchaGeneralSeguidorSocket.sendto(message.encode(), ("192.168.1.9", PuertoEscuchaParticularCoordinador))
time.sleep(1)
s = socket.socket()         # Create a socket object
host = socket.gethostname() # Get local machine name
port = 12345                 # Reserve a port for your service.
s.connect((host, port))
a="Hello server!"
#s.send(a.encode())
SW="Replicate_V1.009"
f = open(SW+".py",'rb')
print ('Sending...')
l = f.read(1024)
while (l):
    print ('Sending...')
    s.send(l)
    l = f.read(1024)
f.close()
print ("Done Sending")
s.shutdown(socket.SHUT_WR)
print (s.recv(1024))
s.close()