import random
from socket import *
import sys

from ...packet import *

serverName = 'localhost'
serverPort = 5000
clientSocket = socket(AF_INET, SOCK_DGRAM)

def send(command, seq_num, session_id, data=None):
    data_str = None
    if data:
        data_str = data.encode('UTF-8')
    message = wrap_packet(command, seq_num, session_id, data_str)
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
            message = wrap_packet(Command.DATA, seq_num, session_id, data.encode('UTF-8'))
            clientSocket.sendto(message,(serverName, serverPort))
        seq_num += 1
    
    clientSocket.close()
