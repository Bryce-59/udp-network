from socket import *
import random
from message import *

if __name__ == '__main__':
    SEQ_NUM = 0
    SESSION_ID = random.randint(0,100)

    serverName = 'descartes.cs.utexas.edu' # CHECK TO MAKE SURE THIS IS CORRECT BEFORE RUNNING - note to self
    serverPort = 5000
    clientSocket = socket(AF_INET, SOCK_DGRAM)

    packet = message_packing(Command.HELLO, SEQ_NUM, SESSION_ID)
    clientSocket.sendto(packet,(serverName, serverPort))
    message = input('Input message: ')
    packet = message_packing(Command.DATA, SEQ_NUM + 1, SESSION_ID) # Default is 0 until handshaking is implemented
    packet = b''.join((packet, message.encode('ASCII')))
    print(packet)

    clientSocket.sendto(packet,(serverName, serverPort))

    modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
    print(modifiedMessage.decode())

    clientSocket.close()
