
from packet import *
import socket
from socket import *
import sys
import threading
from threading import *

server_seq = 0 # increment when server sends a packet

'''
Helper function that sends a command to a session that belongs
to clientAddress
'''
def send(command, session_id, clientAddress):
    global server_seq
    response = wrap_packet(command, server_seq, session_id)
    serverSocket.sendto(response, clientAddress)
    server_seq = server_seq + 1

'''
Helper function that closes a session with id == session_id
'''
def close_session(sessions, session_id, clientAddress):
    if session_id in sessions:
        sessions.pop(session_id)
        print(hex(session_id),"Session closed")
    send(Command.GOODBYE, session_id, clientAddress)

'''
Helper function to respond to DATA and GOODBYE commands
'''
def respond_to_command(sessions, session_id, clientAddress, command, seq_num, data, timers):
    sessions[session_id][0] = seq_num + 1
    if command == Command.DATA:
        # stop timer
        timers[session_id].cancel()
        
        # print data
        print('%s [%d] %s' % (hex(session_id), seq_num, data.decode('UTF-8')), end='')
        
        # start timer
        timers[session_id] = threading.Timer(5, close_session, [sessions, session_id, clientAddress])
        timers[session_id].start()
    elif command == Command.GOODBYE:
        print('%s [%d] GOODBYE from client.' % (hex(session_id), seq_num))
        close_session(sessions, session_id, clientAddress)   

'''
Helper function which processes valid P0P packets

Corner cases -
    Continue | seq_num > expected value (lost)
    Ignore   | seq_num == expected value - 1 (duplicate)
    Goodbye  | seq_num < expected value - 1 and seq_num != 0 (out-of-order)

    if seq_num >= expected value or seq_num == 0 (valid):
        Ignore   | command == HELLO
        Goodbye  | command == ALIVE
'''
def check_command(sessions, session_id, clientAddress, command, seq_num, data, timers):
        # Scenario A: A valid FSA transition exists
        if command == Command.DATA or command == Command.GOODBYE:
            expected_seq = sessions[session_id][0]
            # Scenario A1: The sequence number is too large
            # (Note missing packets and continue to Scenario 2)
            if seq_num > expected_seq:
                for i in range (sessions[session_id][0] + 1, seq_num, 1):
                    print('%s [%d] Lost packet!' % (hex(session_id), i))
                expected_seq = seq_num
            
            # Scenario A2: The sequence number is valid
            # (Inspect the contents and proceed accordingly)
            if seq_num == expected_seq or seq_num == 0:
                respond_to_command(sessions, session_id, clientAddress, command, seq_num, data, timers)

            # Scenario A3: The packet appears to be a duplicate
            # (Note the duplicate and ignore its contents)
            elif seq_num == expected_seq - 1:
                print('%s [%d] Duplicate packet!' % (hex(session_id), seq_num))
            
            # Scenario A4: The sequence number is too small
            # (Terminate the session as this is invalid)
            else:
                close_session(sessions, session_id, client_address)
        # Scenario B: No valid FSA transition exists
        elif command != Command.HELLO:
            close_session(sessions, session_id, clientAddress)

'''
The main socket loop

Corner cases -
    Ignore   | packet < 12 bytes (not P0P packet)
    Ignore   | magic != MAGIC or version != VERSION
    Ignore   | session_id is valid but the IP:port is not
    ???      | session_id has not been seen before, but command is not HELLO 
'''
def handle_socket(sessions):
    MIN_SIZE = 12
    timers = {}

    while True:
        packet, clientAddress = serverSocket.recvfrom(2048)
        if len(packet) >= MIN_SIZE:
            magic, version, command, seq_num, session_id, data = unwrap_packet(packet)
            if magic == MAGIC and version == VERSION:
                if session_id not in sessions:
                    if command == Command.HELLO and seq_num == 0:
                        print('%s [%d] Session created' % (hex(session_id), seq_num))
                        sessions[session_id] = [seq_num, clientAddress]
                        send(Command.HELLO, session_id, clientAddress)
                        
                        # start initial timer
                        timers[session_id] = threading.Timer(5, close_session, [sessions, session_id, clientAddress])
                        timers[session_id].start()
                    else: 
                        # what do we do if "session_id not in sessions" and "command !=  HELLO"??? <<<<
                        pass
                else:
                    if clientAddress == sessions[session_id][1]:
                        check_command(sessions, session_id, clientAddress, command, seq_num, data, timers)

if __name__ == '__main__':
    # set up port and socket
    serverPort = int(sys.argv[1])
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind((b'0.0.0.0', serverPort))
    print('Waiting on port %d...' % serverPort)

    sessions = {}
    t1 = Thread(target=handle_socket, args=(sessions,), daemon=True)
    t1.start()
    while True:
        text = sys.stdin.readline()
        if (not text or (text == "q\n" and sys.stdin.isatty())):
            # close out of every session
            print('Server shutdown')
            for session_id in list(sessions):
                clientAddress = sessions[session_id][1]
                close_session(sessions, session_id, clientAddress)
            break
    
    serverSocket.close()
