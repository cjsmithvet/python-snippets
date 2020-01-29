import sys
import telnetlib
import time

print "Hello"

HOST = "10.0.0.120"
print "got this far"

tn = telnetlib.Telnet()
tn.set_debuglevel(3)
print "About to open the connection, timeout of 10 seconds"
tn.open(HOST, timeout=10)
print "wow I did a telnet"

tn.write("VBUS.VALUE" + "\n")
print "I wrote VBUS.VALUE and am about to sleep 10 seconds"

time.sleep(10)

print tn.read_some()

sys.exit(0)
print tn.read_very_lazy()
print tn.read_until("-->", timeout=10)

tn.write("VBUS.VALUE" + "\n")
print "I wrote VBUS.VALUE again"

# print tn.read_all(timeout=10)
print tn.read_until("-->", timeout=10)

tn.close()
