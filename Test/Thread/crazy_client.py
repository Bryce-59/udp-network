#!/usr/bin/env python3 

import random
from socket import *
from threading import Event, Thread, Timer
import sys

from ...fsa_client import FSA
from ...packet import *

crazy_HELLO = Command.HELLO
crazy_DATA = Command.ALIVE
crazy_GOODBYE = Command.GOODBYE

clientSocket = socket(AF_INET, SOCK_DGRAM)
shutdown_time = Event()
serverName = None
serverPort = None
SESSION_ID = random.randint(0x00000000, 0xFFFFFFFF)
seq_num = 0
FSA = FSA.HELLO
timer = None

'''
Helper function that sends a command to the specified server
'''
def send(command, data=None):
    global seq_num
    if crazy_DATA == Command.DATA:
        packet = wrap_packet(command, seq_num, SESSION_ID, data)
    else:
        packet = wrap_packet(command, seq_num, SESSION_ID, None)
    clientSocket.sendto(packet,(serverName, serverPort))
    seq_num += 1


'''
Corner cases -
    Ignore   | packet < 12 bytes (not P0P packet)
    Ignore   | magic != MAGIC or version != VERSION
    
    Goodbye  | server sends incorrect session id
    Goodbye  | no FSA (i.e. not expected command and not GOODBYE)
'''
def request(expected):
    global FSA
    while True:
        packet, serverAddress = clientSocket.recvfrom(2048)
        if len(packet) >= MIN_SIZE:
            magic, version, command, sequence, rcv_id, data = unwrap_packet(packet)
            if magic == MAGIC and version == VERSION: 
                if not SESSION_ID == rcv_id:
                    return False
        
                if command == expected:
                    return True
                elif command == Command.GOODBYE:
                    if not FSA == FSA.CLOSING:
                        FSA = FSA.CLOSING
                        # print('closing client')
                    close_client(False)
                return False

'''
Start the code
'''
def open_client():
    global timer
    global FSA
    timer = Timer(5, prepare_to_close)
    send(crazy_HELLO, None)
    FSA = FSA.HELLO_WAIT
    timer.start()
    hello = request(Command.HELLO)
    timer.cancel()
    if hello:
        FSA = FSA.READY

        # Start the main running threads
        t1 = Thread(target=handle_socket, daemon=True)
        t2 = Thread(target=handle_keyboard, daemon=True)
        t1.start()
        t2.start()
    else:
        prepare_to_close(False)

def prepare_to_close(wait=True):
    global FSA
    if not FSA == FSA.CLOSING: 
        FSA = FSA.CLOSING
        send(crazy_GOODBYE, None)
        # print('closing client')
        close_client(wait)

'''
Enter the CLOSING phase and transition to CLOSED
based on server response
'''
def close_client(wait=True):
    global timer
    timer.cancel()
    if wait:
        timer = Timer(5, close_client, [False])
        timer.start()
        request(Command.GOODBYE)
        timer.cancel()
    shutdown_time.set()

'''
The main socket loop
'''
def handle_socket():
    global FSA
    while True:
        alive = request(Command.ALIVE)
        
        if alive:
            if FSA == FSA.READY_TIME:
                timer.cancel()
                FSA = FSA.READY
        else:
            break
    prepare_to_close(False)

'''
The main input loop
'''
def handle_keyboard():
    global timer
    global FSA
    while True:
        data = sys.stdin.readline()
        if data == "q\n" and sys.stdin.isatty():
            prepare_to_close(True)
            break
        elif not data:
            print("eof")
            prepare_to_close(True)
            break
        else:
            send(crazy_DATA, data.encode('UTF-8'))
            if FSA == FSA.READY:
                timer = Timer(5, prepare_to_close)
                FSA = FSA.READY_TIME
                timer.start()

if __name__ == '__main__':
    serverName = sys.argv[1]
    serverPort = int(sys.argv[2])
    
    # Start (HELLO_WAIT, READY/READY_TIME)
    t_start = Thread(target=open_client, daemon=True)
    t_start.start()

    # Wait to shut down 
    shutdown_time.wait()
    try:
        clientSocket.shutdown(SHUT_WR)
    except:
        pass
    clientSocket.close()
    FSA = FSA.CLOSED