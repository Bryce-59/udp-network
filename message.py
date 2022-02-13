from enum import IntEnum

MAGIC = 0xC356
VERSION = 1

class Command(IntEnum):
    HELLO = 0
    DATA = 1
    ALIVE = 2
    GOODBYE = 3

def message_packing(command, sequence_number, session_id):
    m = MAGIC.to_bytes(2,byteorder='big')
    v = VERSION.to_bytes(1,byteorder='big')
    cmd = command.to_bytes(1,byteorder='big')
    seq = sequence_number.to_bytes(4,byteorder='big')
    s_id = session_id.to_bytes(4,byteorder='big')
    return b''.join((m,v,cmd,seq,s_id))

def message_unpacking(message):
    m = int.from_bytes(message[:2],byteorder='big')
    v = int.from_bytes(message[2:3],byteorder='big')
    if (m != MAGIC or v != VERSION): #if magic or version numbers are wrong, should be "silently discarded" (invalid)
        return False, None, None, None, None
    
    cmd = int.from_bytes(message[3:4],byteorder='big')
    seq = int.from_bytes(message[4:8],byteorder='big')
    s_id = int.from_bytes(message[8:12],byteorder='big')
    data = message[12:]
    return True, cmd, seq, s_id, data