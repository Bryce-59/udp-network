#!/usr/bin/env python3 

import random
from socket import *
import sys

import pyuv

from fsa_client import FSA
from .packet import *

serverName = None
serverPort = None
SESSION_ID = random.randint(0x00000000, 0xFFFFFFFF)
seq_num = 0
FSA = FSA.HELLO

'''
Helper function that sends a command to the specified server
'''
def send(command, data=None):
    global seq_num
    packet = wrap_packet(command, seq_num, SESSION_ID, data)
    client.send((serverName, serverPort),packet)
    seq_num += 1

'''
Check that data is a valid P0P packet
'''
def valid(data):
    if len(data) >= MIN_SIZE:
        magic, version, _, _, _, _ = unwrap_packet(data)
        if magic == MAGIC and version == VERSION:
            return True 
    return False

'''
Enter the CLOSING phase and wait for GOODBYE or timeout
'''
def TimerGoodbye(handle=None):
    prepare_to_close()
    Timer.start(close_client,5,5)

'''
Enter the CLOSING phase and immediately CLOSE
No point waiting for a server that has gone crazy
'''
def protocol_error():
    prepare_to_close()
    goodbyeAsync.send()

'''
Send GOODBYE and prepare the client for termination
'''
def prepare_to_close():
    global FSA
    Timer.stop()
    if not FSA == FSA.CLOSING:
        FSA = FSA.CLOSING
        send(Command.GOODBYE, None)

'''
Stop the code
'''
def close_client(handle=None):
    global FSA
    clientTTY.stop_read()
    client.stop_recv()
    Timer.stop()
    loop.stop()
    FSA = FSA.CLOSED

'''
The main socket loop
'''
def handle_socket(handle, ip_port, flags, data, error):
    global FSA
    if valid(data):
        _, _, command, _, rcv_id, _ = unwrap_packet(data)
        
        if SESSION_ID == rcv_id:

            if command == Command.GOODBYE:
                FSA = FSA.CLOSING
                goodbyeAsync.send()

            if FSA == FSA.HELLO_WAIT and command == Command.HELLO:
                clientTTY.start_read(handle_keyboard) #start reading input
                FSA = FSA.READY
                Timer.stop()
            
            elif FSA == FSA.READY or FSA == FSA.READY_TIME:
                if command == Command.ALIVE:
                    FSA = FSA.READY
                else:
                    protocol_error()
            
            elif not FSA == FSA.CLOSING and not command == Command.ALIVE :
                protocol_error()
        else:
            protocol_error()

'''
The main input loop
'''
def handle_keyboard(handle, data, error):
    data_str = None
    if not data == None:
        data_str = data.decode("UTF-8")
    
    if not data_str or data_str == "q\n":
        if not data_str:
            print("eof")
        Timer.stop()
        TimerGoodbye()
    else:
        send(Command.DATA, data)
        if FSA == FSA.READY:
           Timer.start(TimerGoodbye,5,5)

if __name__ == '__main__':
    serverName = gethostbyname(sys.argv[1])
    serverPort = int(sys.argv[2])
    
    #initialize the event-loop
    loop = pyuv.Loop.default_loop()
    client = pyuv.UDP(loop)
    clientTTY = pyuv.TTY(loop, sys.stdin.fileno(), True)
    Timer = pyuv.Timer(loop)
    goodbyeAsync = pyuv.Async(loop, close_client)

    #sending the first packet and starting the connection
    client.start_recv(handle_socket)
    send(Command.HELLO, None)
    FSA = FSA.HELLO_WAIT
    Timer.start(TimerGoodbye,5,5)

    #start the loop
    loop.run()