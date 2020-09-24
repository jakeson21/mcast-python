import struct
import pdb
import binascii

# class Packet:
#     def __init__(self):
#         pass


def _getPacketFormat(length):
    '''Packet has  the following fields:
            count: ulong (L) - packet count
            length: ulong (L) - number of bytes that follow
            bytes: (s) data bytes
            crc32: long long (q) crc32 of packet
    '''
    return '>LL{}s'.format(length)


def serialize(datadict):
    '''datadict is a dict with fields:
            count: ulong (L) - packet count
            length: ulong (L) - number of bytes that follow
            bytes: (s) data bytes
    '''
    fmt = '>LL{}s'.format(datadict['length'])
    payload = struct.pack(fmt, datadict['count'], datadict['length'], datadict['bytes'])
    # Add crc of payload
    payload = payload + struct.pack('>q', binascii.crc32(payload))
    return payload


def deserialize(data):
    header_fmt = '>LL'
    count, length = struct.unpack_from(header_fmt, data)
    fmt = '>LL{}sq'.format(length)
    count, length, dbytes, crc = struct.unpack_from(fmt, data)
    crc2 = binascii.crc32(data[:struct.calcsize(fmt[:-1])])
    return {'count': count, 'length': length, 'bytes': dbytes, 'crc': crc, 'crcpass': crc==crc2}


if __name__ == "__main__":
    data = {'count': 2, 'length': 50, 'bytes': bytes(range(50))}
    ser = serialize(data)
    orig = deserialize(ser)
    print('data = {}'.format(data))
    print('serialized = {}'.format(ser))
    print('deserialized = {}'.format(orig))
