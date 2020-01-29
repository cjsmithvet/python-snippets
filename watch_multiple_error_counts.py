from __future__ import print_function
import re
import sys
import time
import telnetlib

def read_telnet(tn):
    while True:
        line = tn.read_until("\n", timeout=0.1)  # Read one line
        if (b"-->") in line:  # last line, no more read
            break
        else:
            oldline = line
    return oldline

def get_integer_value(tn, name):
    command = name + '\r\n'
    tn.write(command)
    response = read_telnet(tn)
    digit = lambda x: int(filter(str.isdigit, x) or 0)
    value = digit(response)
    return value

def print_crcerrcount(tn, string="drive"):
    errcount = get_integer_value(tn, 'FB1.SFDCRCERRORCOUNT')
    # errcount = get_integer_value(tn, 'DRV.FAULT1') # something else to query if we need to
    print(string + " CRC error count: " + str(errcount))

def print_crcerrcounts(tn1, tn2, tn3, tn4):
    print_crcerrcount(tn1, "cap_far")
    print_crcerrcount(tn2, "cap_near")
    print_crcerrcount(tn3, "pay_far")
    print_crcerrcount(tn4, "pay_near")
    # The version of print imported from the future doesn't support flush
    sys.stdout.flush()

def do_every(period,f,*args):
    def g_tick():
        t = time.time()
        count = 0
        while True:
            count += 1
            yield max(t + count*period - time.time(),0)
    g = g_tick()
    while True:
        time.sleep(g.next())
        f(*args)

cap_far = "10.0.0.166"
tn_cap_far = telnetlib.Telnet()
# tn.set_debuglevel(3)
tn_cap_far.open(cap_far, timeout=1)

cap_near = "10.0.0.125"
tn_cap_near = telnetlib.Telnet()
# tn.set_debuglevel(3)
tn_cap_near.open(cap_near, timeout=1)

pay_far = "10.0.0.120"
tn_pay_far = telnetlib.Telnet()
# tn.set_debuglevel(3)
tn_pay_far.open(pay_far, timeout=1)

pay_near = "10.0.0.101"
tn_pay_near = telnetlib.Telnet()
# tn.set_debuglevel(3)
tn_pay_near.open(pay_near, timeout=1)

do_every(1,print_crcerrcounts,tn_cap_far,tn_cap_near,tn_pay_far,tn_pay_near)
