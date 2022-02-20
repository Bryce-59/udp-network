# TODO: Implement client-side Timer

from message import *
from socket import *
import sys
from threading import *

'''
Helper function that closes a session with id == session_id
'''
def close_session(sessions, session_id, server_seq_num, clientAddress):
    sessions.pop(session_id)
    response = pack_message(Command.GOODBYE, server_seq_num, session_id)
    serverSocket.sendto(response, clientAddress)
    
'''
Helper function which handles the DATA and GOODBYE commands 
'''
def respond_to_command(sessions, command, session_id, server_seq_num, clientAddress)
    if command == Command.DATA:
        print('%s [%d] %s' % (hex(session_id), seq_num, message.decode('ASCII')))
        response = pack_message(Command.ALIVE, server_seq_num, session_id)
        serverSocket.sendto(response, clientAddress)
    else:
        print('%s [%d] GOODBYE from client.' % (hex(session_id), seq_num))
        close_session(sessions, session_id, server_seq_num, clientAddress)
        print('%s Session closed' % hex(session_id))


def handle_socket():
    server_seq_num = 0
    sessions = {}

    while True:
        message, clientAddress = serverSocket.recvfrom(2048)
        magic, version, command, seq_num, session_id, message = unpack_message(message)

        # check if the packet is valid
        if magic != MAGIC or version != VERSION:
            pass

        # check is the session is not known
        if session_id not in sessions:
            # create session and send hello back
            if command == Command.HELLO and seq_num == 0:
                print('%s [%d] Session created' % (hex(session_id), seq_num))
                sessions[session_id] = seq_num
                response = pack_message(Command.HELLO, server_seq_num, session_id)
                serverSocket.sendto(response, clientAddress)
                server_seq_num += 1
                pass
        # if the session is known, respond accordingly:
        else:
            # ignore if HELLO is sent at a weird time
            if command == Command.HELLO:
                pass
            # else handle the legal commands:
            elif command == Command.DATA or command == Command.GOODBYE:
                expected = sessions[session_id] + 1
                # if there are lost packets, note them and then continue normally
                if (seq_num > expected):
                    for i in range (sessions[session_id] + 1, seq_num, 1):
                        print('%s [%d] Lost packet!' % (hex(session_id), i))
                    expected = seq_num

                # if a valid sequence number, continue: 
                if (seq_num == expected or seq_num == 0):
                    sessions[session_id] = seq_num + 1
                    respond_to_command(sessions, command, session_id, server_seq_num, clientAddress)
                    server_seq_num += 1
                    pass
                # otherwise there is a duplicate and you should ignore
                elif (seq_num == expected - 1):
                    print('%s [%d] Duplicate packet!' % (hex(session_id), seq_num))
                    pass
        # if the code reaches here, there was a protocol error 
        close_session(sessions, session_id, server_seq_num, clientAddress)
        server_seq_num += 1

def handle_keyboard():
    while True:
        text = sys.stdin.readline()
        if (not text or (text == "q\n" and sys.stdin.isatty())):
            print("EXITING")
            exit()
    

if __name__ == '__main__':

    serverPort = 5000
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind((b'0.0.0.0', serverPort))
    print('Waiting on port %d...' % serverPort)

    t1 = Thread(target=handle_socket, daemon=True)
    t1.start()

    handle_keyboard()

'''
Inspect message:
- check magic and version
-- if they are wrong, silently discard

- next: examine session id field
-- if id field is new, open new session and hand packet to it
--- check that command is HELLO; if not, terminate session
--- check that sequence number is 0 (since this is the first thing we'd expect)

-- else, hand packet to existing session
--- if we receive a hello, terminate session
--- make sure that the sequence number is what we expect
---- if greater than expected, print "LOST PACKET"
---- if same as last received, print "DUPLICATE PACKET" and discard the packet
---- if less than expected, this is a protocol error; send GOODBYE, print "PROTOCOL ERROR", and terminate
'''