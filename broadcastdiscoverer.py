from __future__ import print_function
import argparse
import socket
import struct
import sys
import time

#
# Create a UDP SOCKET for BROADCAST
#
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(0.1)


#
# Create the MESSAGE
# This is a magic set of bytes stolen from a Wireshark trace.
# I have no idea what meaning any of it has to a Kollmorgen drive,
# except that when the drive receives this message on port 5002
# it will reply.
# 
message = bytearray([0x12, 0xaf, 0x12, 0xaf, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x32, 0x35, 0x35, 0x2e, 0x32, 0x35, 0x35, 0x2e, 0x30, 0x2e, 0x30,  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xa4, 0x03, 0x00, 0x00])


#
# Determine WHERE TO SEND IT
#
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
DEFAULT_DISCOVERY_ADDRESS = "10.0.255.255"
DEFAULT_DISCOVERY_PORT = 5002


#
# See who's out there
#
def discover_drives(address, timeout):
    print("Scanning.  This will take a few seconds...")
    sys.stdout.flush()
    current_time = time.time()
    end_time = current_time + timeout

    packets_received = []
    try:
        sent = sock.sendto(message, address)
    except socket.error:
        return packets_received

    while True:
        current_time = time.time()
        if current_time >= end_time:
            break
        time_remaining = end_time - current_time
        try:
            sock.settimeout(time_remaining)
            data, server = sock.recvfrom(4096)
        except (socket.error, socket.timeout, EOFError):
            return packets_received
        packets_received.append(data)
    return packets_received


#
# What are we hearing?
#
def parse_packet(datapacket):
    # Packet payload format (here there be dragons):
    # Bytes 0 - 4 ???
    # Bytes 5 - 16 name, appears to be null terminated
    # Bytes 17 - 28 perhaps, IP address encoded as ASCII, appears to be null terminated
    # Bytes 29 - 44 ???
    name_substring = datapacket[5:17]
    name_substring = name_substring[:name_substring.index(chr(0))]
    addr_substring = datapacket[17:]
    addr_substring = addr_substring[:addr_substring.index(chr(0))]
    return name_substring, addr_substring


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Broadcast Drive Discoverer')

    parser.add_argument('--discovery-address', type=str,
                        default=DEFAULT_DISCOVERY_ADDRESS + ":" + str(DEFAULT_DISCOVERY_PORT),
                        help='The address:port to broadcast to in order to listen for motor drives')
    parser.add_argument('--timeout', type=int,
                        default=10,
                        help='The number of seconds to listen for motor drives')
    args = parser.parse_args()

    address, port = (":" + args.discovery_address).split(":")[-2:]

    response_packets = discover_drives((address, int(port)), timeout=args.timeout)
# print("Found " + response_packets.length() + " drives.")
sys.stdout.flush()
for packet in response_packets:
    drive_name, drive_ip_address = parse_packet(packet)
    print("Drive " + drive_name + " at " + drive_ip_address)
    sys.stdout.flush()
