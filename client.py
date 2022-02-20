# TODO: Implement client-side Timer
# TODO: Remove stop-and-wait handling for non-HELLO messages (EX2 Q2)

from message import *
import random
from socket import *
import sys


serverName = 'aristotle.cs.utexas.edu'
serverPort = 5000
clientSocket = socket(AF_INET, SOCK_DGRAM)
session_id = random.randint(0,(2**31) - 1)

"""
A function that accepts a command, sequence number, and (if command == Command.DATA)
a string to append.
The function packs and transmits the message to the server, and waits for a response.
This response is then analyzed and then, if valid, the command is returned.
"""
def send_and_receive(command, seq_num, session_id, data=None):
    message = pack_message(command, seq_num, session_id, data)
    clientSocket.sendto(message,(serverName, serverPort))
    
    modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
    magic, version, command, seq_num, session_id, response = unpack_message(modifiedMessage)
    return command

if __name__ == '__main__':

    seq_num = 0
    # Handshake start
    rcv_cmd = send_and_receive(Command.HELLO, seq_num, session_id)
    seq_num += 1
    if (rcv_cmd != Command.HELLO):
        clientSocket.close()
        exit()
    # Handshake end

    while True:
        data = sys.stdin.readline()
        if (not data or (data == "q\n" and sys.stdin.isatty())):
            rcv_cmd = send_and_receive(Command.GOODBYE, seq_num, session_id, None)
            clientSocket.close()
            exit()
        else:
            rcv_cmd = send_and_receive(Command.DATA, seq_num, session_id, data)
        
        seq_num += 1
        if (rcv_cmd == Command.GOODBYE):
            print('closing client')
            clientSocket.close()
            exit()
        elif (rcv_cmd != Command.ALIVE):
            clientSocket.close()
            exit()
