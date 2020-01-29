from __future__ import print_function
from getmac import get_mac_address

# Pretty-print a MAC address
def macprint (value = 0):
    # print(hex(value))
    print (':'.join(['{:02x}'.format((value >> ele) & 0xff) for ele in range(0,8*6,8)][::-1])) 


eth_mac = get_mac_address(interface="eth0")
print("Ethernet 0: ")
print(eth_mac)
# macprint(eth_mac)

win_mac = get_mac_address(interface="Ethernet 3")
print("Ethernet 3: ")
print(win_mac)
# macprint(win_mac)

# Kollmorgen far capture motor
ip_mac = get_mac_address(ip="10.0.0.166")
print("Kollmorgen far: ")
print(ip_mac)
# macprint(ip_mac)

# ip6_mac = get_mac_address(ip6="::1")

host_mac = get_mac_address(hostname="localhost")
print("Localhost: ")
print(host_mac)
# macprint(host_mac)

# updated_mac = get_mac_address(ip="10.0.0.1", network_request=True)
