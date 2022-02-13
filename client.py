from socket import *
import random

MAGIC = 0xC356
VERSION = 1
SEQ_NUM = 0
SESSION_ID = random.randint(0,100)

def message_packing(command,message=None):
    m = MAGIC.to_bytes(2,byteorder='big')
    v = VERSION.to_bytes(1,byteorder='big')
    c = command.to_bytes(1,byteorder='big')
    s = SEQ_NUM.to_bytes(4,byteorder='big')
    si = SESSION_ID.to_bytes(4,byteorder='big')
    header = b''.join((m,v,c,s,si))
    if (command == 1):
        return b''.join((header,message.encode('ASCII')))
    return header

serverName = 'aristotle.cs.utexas.edu' #CHECK TO MAKE SURE THIS IS CORRECT BEFORE RUNNING - note to self
serverPort = 5000
clientSocket = socket(AF_INET, SOCK_DGRAM)

message = input('Input message: ')
packet = message_packing(0, message) #Default is 0 until handshaking is implemented
print(packet)

clientSocket.sendto(packet,(serverName, serverPort))

modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
print(modifiedMessage.decode())

clientSocket.close()
