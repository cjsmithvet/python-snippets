from __future__ import print_function
import re
import sys
import telnetlib

#
# Bunch of helper functions
#

def extract_float_from_string(st):
    try:
        substring = re.findall(r'[\d\.\d]+', st)
        retval = float(substring[0])
    except ValueError:
        raise ValueNotFoundError
    return retval

#
# OK now the well-organized stuff
#

class MotorDriveInterfaceError(Exception): pass
class ValueNotFoundError(MotorDriveInterfaceError): pass

class MotorDriveInterface:
    '''Connect to a Kollmorgen motor drive and return information about it'''
    def __init__(self, address="10.0.0.166"):
        self.ip_address = address
        self.tn = telnetlib.Telnet()
        self.connected = False

    def connect(self):
        try:
            self.tn.open(self.ip_address, timeout=1)
        except:
            self.connected = False
            print("Cannot reach host " + self.ip_address + "!")
            sys.stdout.flush()
        else:
            self.connected = True

    def disconnect(self):
        if self.connected:
            self.tn.close()
            self.connected = False

    def read_telnet(self):
        if not self.connected:
            raise MotorDriveInterfaceError
        while True:
            line = self.tn.read_until("\n", timeout=1)  # Read one line
            if (b"-->") in line:  # last line, no more read
                break
            else:
                oldline = line
        if ("Command was not found") in oldline:
            raise MotorDriveInterfaceError
        return oldline

    def get_float_value(self, name):
        command = name + '\r\n'
        self.tn.write(command)
        response = self.read_telnet()
        value = extract_float_from_string(response)
        return value

    def get_integer_value(self, name):
        command = name + '\r\n'
        self.tn.write(command)
        response = self.read_telnet()
        digit = lambda x: int(filter(str.isdigit, x) or 0)
        value = digit(response)
        return value

    def get_string_value(self, name):
        command = name + '\r\n'
        self.tn.write(command)
        response = self.read_telnet()
        return response

    def get_display_string(self):
        if not self.connected:
            raise MotorDriveInterfaceError
        fault = self.get_integer_value('DRV.FAULT1')
        warning = self.get_integer_value('DRV.WARNING1')
        if fault != 0:
            displayed = "F " + str(fault)
        else:
            if warning != 0:
                displayed = "n " + str(warning)
            else:
                displayed = "o0"
        return displayed

    def get_name(self):
        if not self.connected:
            raise MotorDriveInterfaceError
        return self.get_string_value('DRV.NAME')

    def get_vbus_voltage(self):
        if not self.connected:
            raise MotorDriveInterfaceError
        try:
            voltage = self.get_float_value('VBUS.VALUE')
        except MotorDriveInterfaceError:
            print("Error getting voltage!")
        else:
            return voltage

    def just_print_everything(self):
        if not self.connected:
            self.connect()
        print("Address " + self.ip_address + ", ", end='')
        name = self.get_name()
        print("name " + name, end='')
        display_string = self.get_display_string()
        print("Display reads: " + display_string)
        voltage = self.get_vbus_voltage()
        print("VBUS voltage: " + str(voltage) + " [Vdc]")
        sys.stdout.flush()

tn1 = MotorDriveInterface("10.0.0.166")
tn1.just_print_everything()
tn1.disconnect()

tn2 = MotorDriveInterface("10.0.0.125")
tn2.just_print_everything()
tn2.disconnect()

tn3 = MotorDriveInterface("10.0.0.120")
tn3.just_print_everything()
tn3.disconnect()

tn4 = MotorDriveInterface("10.0.0.101")
tn4.just_print_everything()
tn4.disconnect()


