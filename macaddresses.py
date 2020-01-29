from __future__ import print_function
import uuid

# Pretty-print a MAC address
def macprint (value = 0):
    # print(hex(value))
    print (':'.join(['{:02x}'.format((value >> ele) & 0xff) for ele in range(0,8*6,8)][::-1])) 

# Test: Get my own MAC address
def mymac():
    return uuid.getnode()

macprint(mymac())
