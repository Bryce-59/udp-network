# TODO: Thread-based mock client with at least 2 threads
#           TODO: timer does not properly close out
# TODO: Event-loop based mock client using pyuv (Note listening to event 1 and event 2 is done by a single thread)
#           event 1: keyboard
#           event 2: socket
# TODO: ONE of the above must be implemented COMPLETELY, the other can be incomplete
# TODO: Record with Dostoyevsky.txt
# TODO: Complete client-side Design Doc 50%

from message import *
import random
import socket
from socket import *
import sys
import threading
from threading import *

serverName = 'descartes.cs.utexas.edu'
serverPort = 5000
clientSocket = socket(AF_INET, SOCK_DGRAM)

def send(command, seq_num, session_id, data=None):
    message = pack_message(command, seq_num, session_id, data)
    clientSocket.sendto(message,(serverName, serverPort))

def receive():
    modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
    return unpack_message(modifiedMessage)

"""
A function that accepts a command, sequence number, and (if command == Command.DATA)
a string to append.
The function packs and transmits the message to the server, and waits for a response.
This response is then analyzed and then, if valid, the command is returned.
"""
def handshake(session_id):
    send(Command.HELLO, 0, session_id)
    _, _, command, _, _, _ = receive()

    if (command != Command.HELLO):
        close_session()
    return command

def close_session():
    try:
        clientSocket.shutdown(SHUT_WR)
        clientSocket.close()
    except:
        pass
    exit()
            


if __name__ == '__main__':
    seq_num = 0
    session_id = random.randint(0,(2**31) - 1)

    # Handshake start
    handshake(session_id)
    seq_num += 1
    # Handshake end

    # implement event_client

