
from message import *
import socket
from socket import *
import sys
import threading
from threading import *

# a global counter incremented when a command is sent
SERVER_SEQ = 0

'''
Helper function that sends a command to a session that belongs
to clientAddress
'''
def send_message(command, session_id, clientAddress):
    global SERVER_SEQ
    response = pack_message(command, SERVER_SEQ, session_id)
    serverSocket.sendto(response, clientAddress)
    SERVER_SEQ = SERVER_SEQ + 1

'''
Helper function that closes a session with id == session_id
'''
def close_session(sessions, session_id, clientAddress):
    if session_id in sessions:
        sessions.pop(session_id)
    send_message(Command.GOODBYE, session_id, clientAddress)
    
'''
Helper function which handles the DATA and GOODBYE commands 
'''
def respond_to_command(sessions, session_id, clientAddress, command, seq_num, data):
    if command == Command.DATA:
        print('%s [%d] %s' % (hex(session_id), seq_num, data.decode('UTF-8')), end='')
        send_message(Command.ALIVE, session_id, clientAddress)
    else:
        print('%s [%d] GOODBYE from client.' % (hex(session_id), seq_num))
        close_session(sessions, session_id, clientAddress)
        print('%s Session closed' % hex(session_id))


def handle_socket(sessions):
    timers = {}

    while True:
        message, clientAddress = serverSocket.recvfrom(2048)
        magic, version, command, seq_num, session_id, data = unpack_message(message)
        # cancel timer here
        if session_id in timers:
            timers[session_id].cancel()

        # check if the packet is valid
        if magic != MAGIC or version != VERSION:
            continue

        # check is the session is not known
        if session_id not in sessions:
            # create session and send hello back
            if command == Command.HELLO and seq_num == 0:
                print('%s [%d] Session created' % (hex(session_id), seq_num))
                sessions[session_id] = [seq_num, clientAddress]
                send_message(Command.HELLO, session_id, clientAddress)
                # start timer
                timer = threading.Timer(5, close_session, [sessions, session_id, clientAddress])
                timers[session_id] = timer
                timer.start()
                continue
        # if the session is known, respond accordingly:
        else:
            # ignore if HELLO is sent at a weird time
            if command == Command.HELLO:
                continue
            # else handle the legal commands:
            elif command == Command.DATA or command == Command.GOODBYE:
                expected = sessions[session_id][0]
                # if there are lost packets, note them and then continue normally
                if (seq_num > expected):
                    for i in range (sessions[session_id][0] + 1, seq_num, 1):
                        print('%s [%d] Lost packet!' % (hex(session_id), i))
                    expected = seq_num

                # if a valid sequence number, continue: 
                if (seq_num == expected or seq_num == 0):
                    sessions[session_id][0] = seq_num + 1
                    respond_to_command(sessions, session_id, clientAddress, command, seq_num, data)

                    # restart timer
                    timer = threading.Timer(5, close_session, [sessions, session_id, clientAddress])
                    timers[session_id] = timer
                    timer.start()
                    continue
                # otherwise there is a duplicate and you should ignore
                elif (seq_num == expected - 1):
                    print('%s [%d] Duplicate packet!' % (hex(session_id), seq_num))
                    continue
        # if the code reaches here, there was a protocol error
        close_session(sessions, session_id, clientAddress)

if __name__ == '__main__':
    # set up server and port
    serverPort = 5000
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
            for session_id in sessions.keys():
                clientAddress = sessions[session_id][1]
                close_session(sessions, session_id, clientAddress)
            break
    serverSocket.close()
