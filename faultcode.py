from __future__ import print_function
import re
import sys
import telnetlib

def old_read_telnet(tn):
    a = ''
    try:
        while True:
            a += tn.rawq_getchar()
    except:
        pass
    return a

def read_telnet(tn):
    while True:
        line = tn.read_until("\n", timeout=1)  # Read one line
        # print("read_telnet got: " + line)
        # sys.stdout.flush()
        if (b"-->") in line:  # last line, no more read
            break
        else:
            oldline = line
    # print("read telnet returning: " + oldline)
    return oldline

def new_read_telnet(tn):
    a = ''
    ch = ''
    try:
        while ch != '\n':
            ch = tn.rawq.getchar()
            a += ch
    except:
        pass
    else:
        print("read_telnet got " + a)
        return a

# TODO make this more robust (what if st has no numbers represented?)
# as is, this might throw ValueError
def extract_float_from_string(st):
    substring = re.findall(r'[\d\.\d]+', st)
    return float(substring[0])

def get_float_value(tn, name):
    command = name + '\r\n'
    tn.write(command)
    response = read_telnet(tn)
    value = extract_float_from_string(response)
    return value

def get_integer_value(tn, name):
    command = name + '\r\n'
    tn.write(command)
    response = read_telnet(tn)
    digit = lambda x: int(filter(str.isdigit, x) or 0)
    value = digit(response)
    return value

def get_string_value(tn, name):
    command = name + '\r\n'
    tn.write(command)
    response = read_telnet(tn)
    return response

def print_display(tn):
    fault = get_integer_value(tn, 'DRV.FAULT1')
    warning = get_integer_value(tn, 'DRV.WARNING1')
    if fault != 0:
        displayed = "F " + str(fault)
    else:
        if warning != 0:
            displayed = "n " + str(warning)
        else:
            displayed = "o0"
    print(displayed)
    # The version of print imported from the future doesn't support flush
    sys.stdout.flush()

def emulate_drive_display(host):
    tn = telnetlib.Telnet()
    # tn.set_debuglevel(3)
    try:
        tn.open(host, timeout=1)
    except:
        print("Cannot reach host " + host + "!")
        sys.stdout.flush()
    else:
        print(host + " display reads: ", end='') # don't end with a newline
        print_display(tn)
        tn.close()

def print_vbus_voltage(host):
    tn = telnetlib.Telnet()
    try:
        tn.open(host, timeout=1)
    except:
        print("Cannot reach host " + host + "!")
        sys.stdout.flush()
    else:
        voltage = get_float_value(tn, 'VBUS.VALUE')
        print(host + " VBUS voltage: " + str(voltage) + " [Vdc]")
        sys.stdout.flush()
        tn.close()

def print_name(host):
    tn = telnetlib.Telnet()
    tn.open(host, timeout=1)
    response = get_string_value(tn, 'DRV.NAME')
    print(host + " name: " + response)
    sys.stdout.flush()
    tn.close()

HOST = "10.0.0.166"
print("Capture Far")
print_name(HOST)
emulate_drive_display(HOST)
print("")

HOST = "10.0.0.125"
print("Capture Near")
print_name(HOST)
sys.stdout.flush()
emulate_drive_display(HOST)
print("")

HOST = "10.0.0.120"
print("Payout Far")
print_name(HOST)
emulate_drive_display(HOST)
print("")

HOST = "10.0.0.101"
print("Payout Near")
print_name(HOST)
emulate_drive_display(HOST)
print("")
print_vbus_voltage(HOST)


