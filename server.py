
from socket import *
from message import *
from threading import *
import sys


def handle_socket():
    server_seq_num = 0
    sessions = {}

    while True:
        message, clientAddress = serverSocket.recvfrom(2048)

        magic, version, command, seq_num, session_id, message = unpack_message(message)
        # TODO: WE CAN REFACTOR THIS A LITTLE BIT... IT'S JUST THAT THE VERIFY_SESSION
        # FUNCTION WAS CONFUSING FOR ME... THIS MORE CLEARLY SHOWS THE PROGRESSION THE CHECKING GOES THROUGH

        if magic == MAGIC and version == VERSION:
            # now we know the packet is valid
            if session_id in sessions:
                # error check
                if command == Command.HELLO:
                    sessions.pop(session_id)
                elif seq_num > (sessions[session_id] + 1):
                    print('LOST PACKET')
                elif seq_num == sessions[session_id]:
                    print('DUPLICATE PACKET')
                elif seq_num < sessions[session_id]:
                    print('PROTOCOL ERROR')
                    response = pack_message(Command.GOODBYE, server_seq_num, session_id)
                    serverSocket.sendto(response, clientAddress)
                    server_seq_num += 1
                else:
                    # respond to message
                    sessions[session_id] = sessions[session_id] + 1
                    if command == Command.DATA:
                        print('%s [%d] %s' % (hex(session_id), seq_num, message.decode('ASCII')))
                        response = pack_message(Command.ALIVE, server_seq_num, session_id)
                        serverSocket.sendto(response, clientAddress)
                        server_seq_num += 1
                    elif command == Command.GOODBYE:
                        print('%s [%d] GOODBYE from client.' % (hex(session_id), seq_num))
                        response = pack_message(Command.GOODBYE, server_seq_num, session_id)
                        serverSocket.sendto(response, clientAddress)
                        server_seq_num += 1
                        sessions.pop(session_id)
                        print('%s Session closed' % hex(session_id))
            else:
                # make new session
                if command == Command.HELLO and seq_num == 0:
                    # create session and send hello back
                    print('%s [%d] Session created' % (hex(session_id), seq_num))
                    sessions[session_id] = seq_num
                    response = pack_message(Command.HELLO, server_seq_num, session_id)
                    serverSocket.sendto(response, clientAddress)
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