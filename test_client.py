import random
from message import *
from socket import *
import sys

serverName = 'descartes.cs.utexas.edu'
serverPort = 5000
clientSocket = socket(AF_INET, SOCK_DGRAM)

def send(command, seq_num, session_id, data=None):
    message = pack_message(command, seq_num, session_id, data)
    clientSocket.sendto(message,(serverName, serverPort))

if __name__ == '__main__':
    session_id = random.randint(0x00000000, 0xFFFFFFFF)
    seq_num = 0

    # Handshake start
    send(Command.HELLO, seq_num, session_id)
    seq_num += 1
    clientSocket.recvfrom(2048)

    while True:
        data = sys.stdin.readline()
        if (not data or (data == "q\n" and sys.stdin.isatty())):
            send(Command.GOODBYE, seq_num, session_id, None)
            seq_num += 1
            break
        else:
            message = pack_message(Command.DATA, seq_num, session_id, data)
            clientSocket.sendto(message,(serverName, serverPort))
        seq_num += 1
    
    clientSocket.close()
