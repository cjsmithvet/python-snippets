import argparse
import logging
import re
import socket
import telnetlib
import threading
import time


# Periods and timeouts below are in seconds.
# Throughout this code: time.sleep() may never return if someone changes the OS clock.
# There doesn't seem to be any way around that in python.

# How long to wait for responses when discovering drives.
DRIVE_SERVICE_DISCOVERY_TIMEOUT = 2.0
# How often to check the drives for new status.
DRIVE_SERVICE_QUERY_PERIOD = 1.0
# How often to check for exiting the service.
DRIVE_SERVICE_POLL_PERIOD = 1.0
# Timeout to use for telnet connection.
DRIVE_SERVICE_CONNECTION_TIMEOUT = 1.0
# How often to publish a simple log message indicating the service is alive.
DRIVE_SERVICE_HEARTBEAT_PERIOD = 600.0

# Last ditch attempt to talk to something even if no one responded to broadcast.
KOLLMORGEN_SINGLE_DRIVE_DEFAULT_ADDRESS = "10.0.0.166"
# Broadcast address for discovery of Kollmorgen drives.
KOLLMORGEN_DEFAULT_DISCOVERY_ADDRESS = "10.0.255.255"
# Port for discovery of Kollmorgen drives.
KOLLMORGEN_DEFAULT_DISCOVERY_PORT = 5002


class MotorDriveInterfaceError(Exception):
    pass


class MotorDriveConnectionError(MotorDriveInterfaceError):
    pass


class TelnetInterface(object):
    """Handle a single telnet connection as a series of strings back and forth."""

    def __init__(self, address=KOLLMORGEN_SINGLE_DRIVE_DEFAULT_ADDRESS, prompt=b"-->"):
        self._logger = logging.getLogger(address)
        self._ip_address = address
        self._tn = telnetlib.Telnet()
        self._connected = False
        # String to expect from the remote host
        self._prompt = prompt

    def connect(self, timeout=DRIVE_SERVICE_CONNECTION_TIMEOUT):
        if not self._connected:
            try:
                self._tn.open(self._ip_address, timeout=timeout)
                self._connected = True
            except (socket.timeout, EOFError):
                raise MotorDriveConnectionError()

    def disconnect(self):
        if self._connected:
            self._tn.close()
            self._connected = False

    def poll(self, command):
        response = None
        if not self._connected:
            self.connect()
        command_string = command + "\r\n"
        try:
            junk = self._tn.read_very_eager()  # discard pending junk unrelated to this request
            if junk != '':
                self._logger.warn("Received unexpected transmission from remote host: " + junk)
            self._tn.write(command_string)
            response = self._read_telnet()
        except Exception:
            # Commands and responses could get out of sync unless we start over
            self.disconnect()
            raise MotorDriveConnectionError()
        return response

    def _read_telnet(self, timeout=DRIVE_SERVICE_CONNECTION_TIMEOUT):
        # Reads a response, if any, and a prompt (e.g. "-->").
        # So far, responses are all single lines.
        try:
            # TODO: Test with a mock far end that is endlessly spewing random junk
            result = self._tn.read_until(self._prompt, timeout=timeout)
        except (socket.error, EOFError):
            self._connected = False
            raise MotorDriveConnectionError("Unexpected EOF")
        lines = result.split("\n")
        if len(lines) != 2 or lines[-1] != self._prompt:
            raise MotorDriveConnectionError("Unexpected response: {}".format(lines))
        return lines[0]


class KollmorgenDriveInterface(object):
    """Connect to a Kollmorgen motor drive and return information about it."""

    def __init__(self, drive_name, ip_address):
        self._logger = logging.getLogger(drive_name)
        self._drive_name = drive_name
        self._ip_address = ip_address
        self._previous_fault = None
        self._previous_warning = None
        self._telnet_interface = TelnetInterface(self._ip_address)
        self._telnet_interface.connect()
        self._is_active = True

    @staticmethod
    def parse_packet(datapacket):
        # Packet payload format (here there be dragons):
        # Bytes 0 - 4 ???
        # Bytes 5 - 16 name, appears to be null terminated
        # Bytes 17 - 28 perhaps, IP address encoded as ASCII, appears to be null terminated
        # Bytes 29 - 44 ???
        name_substring = datapacket[5:17]
        name_substring = name_substring[:name_substring.index(chr(0))]
        addr_substring = datapacket[17:]
        addr_substring = addr_substring[:addr_substring.index(chr(0))]
        return name_substring, addr_substring

    @staticmethod
    def discover_drives(discovery_address, timeout=DRIVE_SERVICE_DISCOVERY_TIMEOUT):
        # This function needs re-review for all timeout related stuff
        packets_received = []
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        start_time = time.time()
        end_time = start_time + timeout
        # This message is magic, copied directly from a Wireshark trace.
        # I have no idea what meaning any of it has to a Kollmorgen drive,
        # except that when the drive receives this message on port 5002
        # it will reply.
        message = bytearray([0x12, 0xaf, 0x12, 0xaf, 0x00, 0x00, 0x00, 0x00,
                             0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                             0x00, 0x32, 0x35, 0x35, 0x2e, 0x32, 0x35, 0x35,
                             0x2e, 0x30, 0x2e, 0x30, 0x00, 0x00, 0x00, 0x00,
                             0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                             0x00, 0xa4, 0x03, 0x00, 0x00])
        address, port = discovery_address.split(":")
        discovery_destination = (address, int(port))
        try:
            sent = sock.sendto(message, discovery_destination)
        except socket.error:
            return packets_received

        while True:
            current_time = time.time()
            if current_time >= end_time:
                break
            time_remaining = end_time - current_time
            try:
                sock.settimeout(time_remaining)
                data, server = sock.recvfrom(4096)
            except (socket.error, socket.timeout, EOFError):
                return packets_received
            packets_received.append(data)
        return packets_received

    @staticmethod
    def extract_first_float_from_string(st):
        substrings = re.findall(r'\d+\.\d+', st)
        if not substrings:
            raise ValueError()
        retval = float(substrings[0])
        return retval

    @staticmethod
    def extract_first_int_from_string(st):
        substrings = re.findall(r'\d+', st)
        if not substrings:
            raise ValueError()
        retval = int(substrings[0])
        return retval

    def _get_float_value(self, name):
        response = self._telnet_interface.poll(name)
        if response is None:
            raise MotorDriveConnectionError()
        if "Command was not found" in response:
            raise ValueError()
        value = KollmorgenDriveInterface.extract_first_float_from_string(response)
        return value

    def _get_integer_value(self, name):
        response = self._telnet_interface.poll(name)
        if response is None:
            raise MotorDriveConnectionError()
        if "Command was not found" in response:
            raise ValueError()
        value = KollmorgenDriveInterface.extract_first_int_from_string(response)
        return value

    def _get_string_value(self, name):
        response = self._telnet_interface.poll(name)
        if response is None:
            raise MotorDriveConnectionError()
        if "Command was not found" in response:
            raise ValueError()
        return response

    def get_display_string(self):
        if not self._is_active:
            return None
        try:
            fault = self._get_integer_value('DRV.FAULT1')
            warning = self._get_integer_value('DRV.WARNING1')
        except ValueError:
            return None
        # Log any change in the fault and warning
        if fault != self._previous_fault:
            logger.info("Drive at %s reporting fault status %s (0 is nominal)", self._ip_address, str(fault))
            self._previous_fault = fault
        if warning != self._previous_warning:
            logger.info("Drive at %s reporting warning status %s (0 is nominal)", self._ip_address, str(warning))
            self._previous_warning = warning
        # Build the string displayed by the motor drive
        if fault:
            displayed = "F " + str(fault)
        elif warning:
            displayed = "n " + str(warning)
        else:
            displayed = "o 0"
        return displayed

    def get_name(self):
        return self._drive_name

    def get_vbus_voltage(self):
        if not self._is_active:
            return None
        try:
            return self._get_float_value('VBUS.VALUE')
        except ValueError:
            return None

    def get_vbus_voltage_string(self):
        if not self._is_active:
            return None
        try:
            return self._get_string_value('VBUS.VALUE')
        except ValueError:
            return None

    def get_motor_current_string(self):
        if not self._is_active:
            return None
        try:
            return self._get_string_value('DRV.ICONT')
        except ValueError:
            return None

    def get_motor_temp_string(self):
        if not self._is_active:
            return None
        try:
            return self._get_string_value('MOTOR.TEMPC')
        except ValueError:
            return None

    def get_address(self):
        return self._ip_address

    def suspend_connection(self):
        if self._is_active:
            self._telnet_interface.disconnect()
            self._is_active = False

    def resume_connection(self):
        if not self._is_active:
            self._telnet_interface.connect()
            self._is_active = True

    def is_suspended(self):
        return not self._is_active

    def shutdown(self):
        self.suspend_connection()


# TODO (CJS): Merge this class and the KollmorgenDriveInterface class.
# The division is making less and less sense.
class DriveAgent(object):
    """Handle fault/warning monitoring and bus voltage queries for a single drive."""

    def __init__(self, drive_name, drive_ip_address):
        self._unable_to_connect = False
        self._drive_interface = KollmorgenDriveInterface(drive_name, drive_ip_address)
        self._drive_name = drive_name
        self._drive_address = drive_ip_address
        self._display_string = None
        self._voltage = None
        self._current = None
        self._temp = None
        self._data_lock = threading.Lock()
        self.finished = False  # Set to True when the thread for this agent should terminate.

    def query(self):
        with self._data_lock:
            try:
                self._display_string = self._drive_interface.get_display_string()
                self._voltage = self._drive_interface.get_vbus_voltage_string()
                self._current = self._drive_interface.get_motor_current_string()
                self._temp = self._drive_interface.get_motor_temp_string()
            except MotorDriveConnectionError:
                # Other than the name and address, which don't change once established,
                # do not return the other results; they are stale or misleading.
                self._display_string = "None"
                self._voltage = "None"
                self._current = "None"
                self._temp = "None"

    def print_all_values(self):
        with self._data_lock:
            # printstring = self._drive_name + " (" + self._drive_address + "): "
            name = self._drive_name if not None else "None"
            address = self._drive_address if not None else "None"
            display = self._display_string if not None else "None"
            voltage = self._voltage if not None else "None"
            current = self._current if not None else "None"
            temp = self._temp if not None else "None"
            printstring = "{} ({}):".format(name, address)
            printdisplay = "   Display {}".format(display)
            printvolt = "  Voltage {}".format(voltage)
            printcurrent = "  Current {}".format(current)
            printtemp = "  Temperature {}".format(temp)
            print(printstring)
            print(printdisplay)
            print(printvolt)
            print(printcurrent)
            print(printtemp)

    def shutdown(self):
        self._drive_interface.shutdown()


class MotorDriveService(object):
    """
        The MotorDriveService object is responsible for detecting motor drives on the network.
        Currently it can do this specifically for network objects that respond on port 5002
        (Kollmorgen motor drives).  As those objects come and go based on periodic polling, the
        MotorDriveService creates and destroys DriveAgent objects to interact with them.
    """

    def __init__(self, discovery_address):
        self._logger = logging.getLogger(__name__)
        self.finished = False
        self._agents_lock = threading.Lock()
        self._agents = {}
        self._threads = {}
        self._discovery_address = discovery_address
        self._discover_drives()
        self._next_heartbeat_time = time.time()  # may as well have one at the outset

    def shutdown(self):
        self._logger.info("Shutting down")
        self.finished = True

    def _discover_drives(self):
        # See who's out there and talking to us now
        # This function can take several seconds to return
        response_packets = KollmorgenDriveInterface.discover_drives(self._discovery_address)

        # We acquire the agents lock so that we can modify the _agents list in peace
        with self._agents_lock:
            # Remember what drives we thought were out there before
            previous_drive_addresses = set(self._agents.keys())
            for packet in response_packets:
                drive_name, drive_ip_address = KollmorgenDriveInterface.parse_packet(packet)
                if drive_ip_address in previous_drive_addresses:
                    # This one requires no changes to _agents or _threads
                    previous_drive_addresses.remove(drive_ip_address)
                    continue
                # This drive is new!  Make an agent and a thread for it
                self._logger.info("Drive found at %s", drive_ip_address)
                agent = DriveAgent(drive_name, drive_ip_address)
                thread = threading.Thread(target=MotorDriveService.agent_thread_function,
                                          args=(agent, self))
                thread.start()
                self._agents[drive_ip_address] = agent
                self._threads[drive_ip_address] = thread
            # Anything left in this list is a drive that has stopped responding
            for address in previous_drive_addresses:
                self._logger.info("Drive no longer responding at %s", address)
                self._agents[address].finished = True
                self._threads[address].join()  # Block until the thread is actually done
                del self._threads[address]
                del self._agents[address]

    @staticmethod
    def agent_thread_function(drive_agent, parent):
        while not parent.finished and not drive_agent.finished:
            start_time = time.time()
            drive_agent.query()
            drive_agent.print_all_values()
            end_time = time.time()
            if end_time >= start_time + DRIVE_SERVICE_QUERY_PERIOD:
                continue
            time.sleep(DRIVE_SERVICE_QUERY_PERIOD - max(end_time - start_time, 0))
        drive_agent.shutdown()

    def run(self):
        try:
            while not self.finished:
                # self._rest_server.handle_request()
                time.sleep(1)

        except KeyboardInterrupt:
            self.shutdown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Motor Drive Service')

    parser.add_argument('--discovery-address', type=str,
                        default=KOLLMORGEN_DEFAULT_DISCOVERY_ADDRESS + ":" + str(KOLLMORGEN_DEFAULT_DISCOVERY_PORT),
                        help='The address:port to broadcast to in order to listen for motor drives')
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger("Motor Drive Service")

    service = MotorDriveService(args.discovery_address)
    logger.info("Starting up...")
    service.run()
