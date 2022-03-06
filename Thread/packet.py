from enum import IntEnum

MAGIC = 0xC356
VERSION = 1

class Command(IntEnum):
    HELLO = 0
    DATA = 1
    ALIVE = 2
    GOODBYE = 3

def wrap_packet(command, sequence_number, session_id, data=None):
    m = MAGIC.to_bytes(2,byteorder='big')
    v = VERSION.to_bytes(1,byteorder='big')
    cmd = command.to_bytes(1,byteorder='big')
    seq = sequence_number.to_bytes(4,byteorder='big')
    s_id = session_id.to_bytes(4,byteorder='big')
    packet = b''.join((m,v,cmd,seq,s_id))
    if command == Command.DATA:
        packet = b''.join((packet, data.encode('UTF-8')))
    return packet

def unwrap_packet(packet):
    m = int.from_bytes(packet[:2],byteorder='big')
    v = int.from_bytes(packet[2:3],byteorder='big')
    cmd = int.from_bytes(packet[3:4],byteorder='big')
    seq = int.from_bytes(packet[4:8],byteorder='big')
    s_id = int.from_bytes(packet[8:12],byteorder='big')
    data = packet[12:]
    return m, v, cmd, seq, s_id, data