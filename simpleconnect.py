# import getpass
import sys
import telnetlib

# HOST = "localhost"
HOST = "10.0.0.120"
print "got this far"
# user = raw_input("Enter your remote account: ")
# password = getpass.getpass()

tn = telnetlib.Telnet(HOST)
print "wow I did a telnet"

# tn.read_until("login: ")
tn.write("asdfasdf")
print "I wrote something"

tn.read_until("--> ")
print "I read something"

# tn.write(user + "\n")
tn.write("VBUS.VALUE" + "\n")
print "I wrote VBUS.VALUE"

# if password:
#     tn.read_until("Password: ")
#     tn.write(password + "\n")
# 
# tn.write("ls\n")
# tn.write("exit\n")

# print tn.read_all()
