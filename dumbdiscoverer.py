from __future__ import print_function
import socket
import struct
import sys

#
# Create a UDP SOCKET
#
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(0.25)

#
# Create the MESSAGE
# 
message = bytearray([0x12, 0xaf, 0x12, 0xaf, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x32, 0x35, 0x35, 0x2e, 0x32, 0x35, 0x35, 0x2e, 0x30, 0x2e, 0x30,  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xa4, 0x03, 0x00, 0x00])

#
# See who's out there
#

print("Scanning.  This will take a little over a minute...")
sys.stdout.flush()

for i in range(255):
    server_ip = '10.0.0.' + str(i)
    server_address = (server_ip, 5002)

    try:

        # Send data
        # print ('Checking "%s"' % server_ip)
        # sys.stdout.flush()
        sent = sock.sendto(message, server_address)

        # Listen until timeout
        data, server = sock.recvfrom(4096)
        print ('FOUND! %s ' % data, end='')
        print ('at %s' % server_ip)
        sys.stdout.flush()
        
    except (socket.timeout, socket.error):
        continue

    # finally:

    #     print ('closing socket')
    #     sys.stdout.flush()
    #     sock.close()
