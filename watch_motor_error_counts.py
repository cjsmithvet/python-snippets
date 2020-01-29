from __future__ import print_function
import re
import sys
import time
import telnetlib

def read_telnet(tn):
    a = ''
    try:
        while True:
            a += tn.rawq_getchar()
    except:
        pass
    return a

def get_integer_value(tn, name):
    command = name + '\r\n'
    tn.write(command)
    response = read_telnet(tn)
    digit = lambda x: int(filter(str.isdigit, x) or 0)
    value = digit(response)
    return value

def print_crcerrcount(tn):
    errcount = get_integer_value(tn, 'FB1.SFDCRCERRORCOUNT')
    print("Current CRC error count: " + str(errcount))
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

host = "10.0.0.166"
tn = telnetlib.Telnet()
# tn.set_debuglevel(3)
tn.open(host, timeout=1)

do_every(1,print_crcerrcount,tn)
