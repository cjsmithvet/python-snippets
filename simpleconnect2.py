import sys
import telnetlib


def read_telnet(tn):
    a = ''
    try:
        while True:
            a += tn.rawq_getchar()
    except:
        pass
    return a

HOST = "10.0.0.120"
tn = telnetlib.Telnet()
# tn.set_debuglevel(3)
tn.open(HOST, timeout=1)
command = 'VBUS.VALUE\r\n'
print command
tn.write(command)

a = read_telnet(tn)
# a = tn.read_eager()
print a


command = 'drv.fault1\r\n'
print command
tn.write(command)

tn.fill_rawq()
a = tn.read_eager()
print a




command = 'drv.warning1\r\n'
print command
tn.write(command)

tn.fill_rawq()
a = tn.read_eager()
print a


tn.close()
