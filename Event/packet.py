from enum import IntEnum

MAGIC = 0xE86D
VERSION = 2
MIN_SIZE = 12

'''
An enum class to represent the finite commands that can be sent over the network.
'''
class Command(IntEnum):
    HELLO = 0
    DATA = 1
    ALIVE = 2
    GOODBYE = 3

'''
Wrap the data for transmission.
'''
def wrap_packet(command, sequence_number, session_id, data=None):
    m = MAGIC.to_bytes(2,byteorder='big')
    v = VERSION.to_bytes(1,byteorder='big')
    cmd = command.to_bytes(1,byteorder='big')
    seq = sequence_number.to_bytes(4,byteorder='big')
    s_id = session_id.to_bytes(4,byteorder='big')
    packet = b''.join((m,v,cmd,seq,s_id))
    if data and command == Command.DATA:
        packet = b''.join((packet, data))
    return packet

'''
Unwrap the data upon reception.
'''
def unwrap_packet(packet):
    m = int.from_bytes(packet[:2],byteorder='big')
    v = int.from_bytes(packet[2:3],byteorder='big')
    cmd = int.from_bytes(packet[3:4],byteorder='big')
    seq = int.from_bytes(packet[4:8],byteorder='big')
    s_id = int.from_bytes(packet[8:12],byteorder='big')
    data = packet[12:]
    return m, v, cmd, seq, s_id, data