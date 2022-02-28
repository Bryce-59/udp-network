# TODO: Thread-based mock client with at least 2 threads
#           thread 1: reads from keyboard
#           thread 2: listen to socket and actually receives server messages (doesn’t have to do anything… with it)
# TODO: Event-loop based mock client using pyuv (Note listening to event 1 and event 2 is done by a single thread)
#           event 1: keyboard
#           event 2: socket
# TODO: ONE of the above must be implemented COMPLETELY, the other can be incomplete
# TODO: Record with Dostoyevsky.txt
# TODO: Complete client-side Design Doc 50%

from message import *
import random
from socket import *
import sys


serverName = 'descartes.cs.utexas.edu'
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
            message = pack_message(Command.DATA, seq_num, session_id, data)
            clientSocket.sendto(message,(serverName, serverPort))
        
        seq_num += 1
        '''if (rcv_cmd == Command.GOODBYE):
            print('closing client')
            clientSocket.close()
            exit()
        elif (rcv_cmd != Command.ALIVE):
            clientSocket.close()
            exit()'''
