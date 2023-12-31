import socket
from socket import *
import sys
from threading import Thread

from ...packet import *

# a global counter incremented when a command is sent
server_seq = 0
loss = {}

def send_message(command, session_id, clientAddress):
    global server_seq
    response = wrap_packet(command, server_seq, session_id)
    serverSocket.sendto(response, clientAddress)
    server_seq = server_seq + 1

def close_session(sessions, session_id, clientAddress):
    if session_id in sessions:
        sessions.pop(session_id)
    send_message(Command.GOODBYE, session_id, clientAddress)

def handle_socket(sessions):
    global lost
    while True:
        message, clientAddress = serverSocket.recvfrom(2048)
        magic, version, command, seq_num, session_id, data = unwrap_packet(message)

        if command == Command.HELLO:
            print('%s [%d] Session created' % (hex(session_id), seq_num))
            sessions[session_id] = [seq_num, clientAddress]
            loss[session_id] = 0
            send_message(Command.HELLO, session_id, clientAddress)
            continue
        else:
            expected = sessions[session_id][0]
            if (seq_num > expected):
                for i in range (sessions[session_id][0] + 1, seq_num, 1):
                    loss[session_id] += 1
                expected = seq_num 
            
            if (seq_num == expected or seq_num == 0):
                sessions[session_id][0] = seq_num + 1
                if command == Command.DATA:
                    send_message(Command.ALIVE, session_id, clientAddress)
                else:
                    close_session(sessions, session_id, clientAddress)
                    print('%s Session closed' % hex(session_id), lost)
                    total = sessions[session_id][0]
                    print(hex(session_id),"Loss: "+loss[session_id]+"/"+total+" ("+(loss[session_id]/total)+"%)")
        

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
            for session_id in list(sessions):
                clientAddress = sessions[session_id][1]
                close_session(sessions, session_id, clientAddress)
            break
    serverSocket.close()
