#! /usr/bin/python3.7
# -*- coding: utf-8 -*-
import socket
import struct
import sys
import argparse
import time
import logging


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
 
    print('sending "{}"'.format(message))
    # Send to multicast group
    if loop<=0:
        log.info('Press ctrl+C to stop sending')
        while True:
            sock.sendto(message.encode(), multicast_group)
            time.sleep(1)
    else:
        for n in range(loop):
            log.info('Sending {} of {}'.format(n+1, loop))
            sock.sendto(message.encode(), multicast_group)
            time.sleep(1)
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
        message, address = sock.recvfrom(2048)
        log.info('{}:{} sent: "{}"'.format(address[0], address[1], message))
 
 
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Multicast demo')
    parser.add_argument('type', choices=['tx', 'rx'], default='tx', help='Type')
    parser.add_argument('-a', '--mcast-address', default='238.1.1.1', help='Multicast address')
    parser.add_argument('-p', '--mcast-port', default=2000, type=int, help='Multicast port')
    parser.add_argument('-i', '--iface', default='0.0.0.0', help='Local interface address to use')
    parser.add_argument('-m', '--message', default='test message', help='Message to send')
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
