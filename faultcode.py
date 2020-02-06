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

class MotorDriveInterface(object):
    '''Connect to a Kollmorgen motor drive and return information about it'''
    def __init__(self, address="10.0.0.113"):
        self._ip_address = address
        self._tn = telnetlib.Telnet()
        self._connected = False

    def _connect(self):
        try:
            self._tn.open(self._ip_address, timeout=1)
        except:
            self._connected = False
            print("Cannot reach host " + self._ip_address + "!")
            sys.stdout.flush()
        else:
            self._connected = True

    def _disconnect(self):
        if self._connected:
            self._tn.close()
            self._connected = False

    def _read_telnet(self):
        if not self._connected:
            raise MotorDriveInterfaceError
        while True:
            line = self._tn.read_until("\n", timeout=1)  # Read one line
            if (b"-->") in line:  # last line, no more read
                break
            else:
                oldline = line
        # if ("Command was not found") in oldline:
        #     raise MotorDriveInterfaceError
        return oldline

    def _get_float_value(self, name):
        command = name + '\r\n'
        self._tn.write(command)
        response = self._read_telnet()
        value = extract_float_from_string(response)
        return value

    def _get_integer_value(self, name):
        command = name + '\r\n'
        self._tn.write(command)
        response = self._read_telnet()
        digit = lambda x: int(filter(str.isdigit, x) or 0)
        value = digit(response)
        return value

    def _get_string_value(self, name):
        command = name + '\r\n'
        self._tn.write(command)
        response = self._read_telnet()
        return response

    def _get_display_string(self):
        if not self._connected:
            raise MotorDriveInterfaceError
        fault = self._get_integer_value('DRV.FAULT1')
        warning = self._get_integer_value('DRV.WARNING1')
        if fault != 0:
            displayed = "F " + str(fault)
        else:
            if warning != 0:
                displayed = "n " + str(warning)
            else:
                displayed = "o0"
        return displayed

    def _get_name(self):
        if not self._connected:
            raise MotorDriveInterfaceError
        return self._get_string_value('DRV.NAME')

    def _get_vbus_voltage(self):
        if not self._connected:
            raise MotorDriveInterfaceError
        try:
            voltage = self._get_float_value('VBUS.VALUE')
        except MotorDriveInterfaceError:
            print("Error getting voltage!")
        else:
            return voltage

    def just_print_everything(self):
        if not self._connected:
            self._connect()
        print("Address " + self._ip_address + ", ", end='')
        name = self._get_name()
        print("name " + name, end='')
        display_string = self._get_display_string()
        print("Display reads: " + display_string)
        voltage = self._get_vbus_voltage()
        print("VBUS voltage: " + str(voltage) + " [Vdc]")
        sys.stdout.flush()
        self._disconnect()

tn1 = MotorDriveInterface("10.0.0.166")
tn1.just_print_everything()

# tn2 = MotorDriveInterface("10.0.0.125")
# tn2.just_print_everything()

# tn3 = MotorDriveInterface("10.0.0.120")
# tn3.just_print_everything()

# tn4 = MotorDriveInterface("10.0.0.101")
# tn4.just_print_everything()


