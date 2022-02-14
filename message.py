from enum import IntEnum

MAGIC = 0xC356
VERSION = 1

class Command(IntEnum):
    HELLO = 0
    DATA = 1
    ALIVE = 2
    GOODBYE = 3

def pack_message(command, sequence_number, session_id, message=None):
    m = MAGIC.to_bytes(2,byteorder='big')
    v = VERSION.to_bytes(1,byteorder='big')
    cmd = command.to_bytes(1,byteorder='big')
    seq = sequence_number.to_bytes(4,byteorder='big')
    s_id = session_id.to_bytes(4,byteorder='big')
    packet = b''.join((m,v,cmd,seq,s_id))
    if command == Command.DATA:
        packet = b''.join((packet, message.encode('ASCII')))
    return packet

def unpack_message(message):
    m = int.from_bytes(message[:2],byteorder='big')
    v = int.from_bytes(message[2:3],byteorder='big')
    cmd = int.from_bytes(message[3:4],byteorder='big')
    seq = int.from_bytes(message[4:8],byteorder='big')
    s_id = int.from_bytes(message[8:12],byteorder='big')
    data = message[12:]
    return m, v, cmd, seq, s_id, data