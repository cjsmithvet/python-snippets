from __future__ import print_function
import sys
import time

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

def hello(s):
    print('hello {} ({:.4f})'.format(s,time.time()))
    # The version of print imported from the future doesn't support flush
    sys.stdout.flush()
    # time.sleep(.3)

do_every(0.001,hello,'foo')
