#! /usr/bin/python3
# -*- coding: utf-8 -*-
import socket
import struct
import sys
import argparse
import time
import logging
from packet import *
import random
import numpy as np


# create logger with 'spam_application'
log = logging.getLogger('multicast-demo')
log.setLevel(logging.INFO)
# create file handler which logs even debug messages
fh = logging.FileHandler('mcast.log')
fh.setLevel(logging.INFO)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
log.addHandler(fh)
log.addHandler(ch)

 
def send(mcast_address, mcast_port, iface, message, loop):
    multicast_addr = mcast_address  # '238.1.1.1'
    multicast_port = mcast_port  # 8787
    multicast_group = (multicast_addr, multicast_port)
    iface_addr = iface  # '192.168.16.231'  # Interface IP to send from
    server_address = (iface_addr, 0)
 
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    # bind to specific interface
    sock.bind(server_address)
 
    # Set allowable multicast hop limit
    ttl = struct.pack('b', 3)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
    #if message is None:
    #    message = serialize({'count': 0, 'length': 5, 'bytes': bytes(range(5))})
    #print('sending "{}"'.format(message))

    # Send to multicast group
    length = 4000
    
    n = 1
    while True:
        # message = serialize({'count': n, 'length': length, 'bytes': bytes(random.sample(range(256), length))})
        message = serialize({'count': n, 'length': length, 'bytes': np.random.randint(0, 256, size=(length,), dtype=np.uint8).tobytes()})
        if type(message) is not bytes:
            sock.sendto(message.encode(), multicast_group)
        elif type(message) is bytes:
            sock.sendto(message, multicast_group)
        log.info('Sent message {}'.format(n))
        # time.sleep(.01)
        n += 1
        if loop !=0 and loop<n:
            break

    sock.close()
 
 
def receive(mcast_address, mcast_port, iface):
    multicast_addr = mcast_address  # '238.1.1.1'
    multicast_port = mcast_port  # 8787
    bind_addr = iface  # '192.168.16.232'  # Interface IP to receive on
 
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    # Bind to all interfaces
    sock.bind(('', multicast_port))
    log.info('Listening on {} for {}:{}'.format(bind_addr, multicast_addr, multicast_port))
 
    # Join multicast group
    membership = socket.inet_aton(multicast_addr) + socket.inet_aton(bind_addr)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, membership)
    # Allow reusing port number
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
 
    while True:
        message, address = sock.recvfrom(4096)
        payload = deserialize(message)
        log.info('{}:{} recvd: "{}"'.format(address[0], address[1], payload['count']))
 
 
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Multicast demo')
    parser.add_argument('type', choices=['tx', 'rx'], default='tx', help='Type')
    parser.add_argument('-a', '--mcast-address', default='238.1.1.1', help='Multicast address')
    parser.add_argument('-p', '--mcast-port', default=2000, type=int, help='Multicast port')
    parser.add_argument('-i', '--iface', default='0.0.0.0', help='Local interface address to use')
    parser.add_argument('-m', '--message', default=None, help='Message to send')
    parser.add_argument('-l', '--loop', default=1, type=int, help='Number of times to send the tx message, 0=infinite')
    args = parser.parse_args()
 
    try:
        if args.type.lower() == 'tx':
            send(args.mcast_address, args.mcast_port, args.iface, args.message, args.loop)
        elif args.type.lower() == 'rx':
            receive(args.mcast_address, args.mcast_port, args.iface)
    except KeyboardInterrupt:
        pass
    exit(0)
