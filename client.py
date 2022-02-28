# TODO: Thread-based mock client with at least 2 threads
#           TODO: implement timer
#           TODO: make sure the program closes out correctly when server sends "GOODBYE"
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
        clientSocket.close()
        exit()
    return command

def handle_keyboard(seq_num):
    while True:
        data = sys.stdin.readline()
        if (not data or (data == "q\n" and sys.stdin.isatty())):
            rcv_cmd = send(Command.GOODBYE, seq_num, session_id, None)
            clientSocket.close()
            exit()
        else:
            message = pack_message(Command.DATA, seq_num, session_id, data)
            clientSocket.sendto(message,(serverName, serverPort))
        
        seq_num += 1

def handle_socket():
    while True:
        magic, version, command, sequence, session_id, data = receive()
        if (command == Command.GOODBYE):
            print('closing client')
            clientSocket.shutdown()
            clientSocket.close()
            exit()
        elif (command != Command.ALIVE):
            clientSocket.close()
            exit()

if __name__ == '__main__':
    seq_num = 0
    session_id = random.randint(0,(2**31) - 1)

    # Handshake start
    handshake(session_id)
    seq_num += 1
    # Handshake end

    t1 = Thread(target=handle_socket, daemon=True)
    t1.start()

    handle_keyboard(seq_num)
