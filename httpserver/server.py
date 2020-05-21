import SimpleHTTPServer
import SocketServer
import os
import sys
import threading
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


class FlightOpsHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        pass

    def do_GET(self):
        # Are we alive?  Special case thing to request.
        if self.path == "/status":
            # Expand this to include whatever ya like.  For now, if this says "/status" back atcha, we're alive.
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            # self.wfile.write("Hello from the Flight Ops Handler!")
            self.wfile.write("Flight Ops Handler says " + self.path)
            return

        # Otherwise, find and serve up the file.
        if self.path == "/recovery":
            filename = "/recovery_status.html"
        else:
            filename = self.path
        response_file = self._find_and_open_file(filename)
        self._send_file(response_file)

    def do_PUT(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write("Flight Ops got a PUT!!  Yowza!  It is " + self.path)

    def _find_and_open_file(self, filename):
        fd = None
        local_repo_path = "C:/Users/cj/code/gita/FlightSystems/server/flight_ops/static"
        current_dir = os.getcwd()
        print "flight_ops: " + current_dir
        # repo_file = os.path.join(local_repo_path, filename)
        repo_file = local_repo_path + filename
        # current_dir_file = os.path.join(current_dir, filename)
        current_dir_file = current_dir + "/6001" + filename
        try:
            # fd = open("C:/Users/cj/code/gita/FlightSystems/server/flight_ops/static/recovery_status.html", 'r')
            print "flight_ops: **** Trying to open " + repo_file
            fd = open(repo_file, 'r')
        except:
            # if this too raises an exception, let it raise; we don't have anywhere else to look.
            print "flight_ops: **** Trying to open " + current_dir_file
            fd = open(current_dir_file, 'r')
        return fd

    def _send_file(self, fd):
        if fd is None:
            self.send_response(404)
            return
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(fd.read())


class MotorDriveHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        pass

    def do_GET(self):
        # Are we alive?  Special case thing to request.
        if self.path == "/status":
            # Expand this to include whatever ya like.  For now, if this says "/status" back atcha, we're alive.
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            # self.wfile.write("Hello from the Motor Drive Handler!")
            self.wfile.write("Motor Drive Handler says " + self.path)
            return

        # Otherwise, find and serve up the file.
        if self.path == "/recovery":
            filename = "/recovery_status.html"
        else:
            filename = self.path
        response_file = self._find_and_open_file(filename)
        self._send_file(response_file)

    def _find_and_open_file(self, filename):
        fd = None
        local_repo_path = "C:/Users/cj/code/gita/FlightSystems/server/flight_ops/static"
        current_dir = os.getcwd()
        print "flight_ops: " + current_dir
        # repo_file = os.path.join(local_repo_path, filename)
        repo_file = local_repo_path + filename
        # current_dir_file = os.path.join(current_dir, filename)
        current_dir_file = current_dir + "/5007" + filename
        try:
            print "motor_drive: **** Trying to open " + repo_file
            fd = open(repo_file, 'r')
        except:
            # if this too raises an exception, let it raise; we don't have anywhere else to look.
            print "motor_drive: **** Trying to open " + current_dir_file
            fd = open(current_dir_file, 'r')
        return fd

    def _send_file(self, fd):
        if fd is None:
            self.send_response(404)
            return
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(fd.read())


class HealthHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        pass

    def do_GET(self):
        # Are we alive?  Special case thing to request.
        if self.path == "/status":
            # Expand this to include whatever ya like.  For now, if this says "/status" back atcha, we're alive.
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write("Hello from the Health Handler!")
            return

        # Otherwise, find and serve up the file.
        if self.path == "/recovery":
            filename = "/recovery_status.html"
        else:
            filename = self.path
        response_file = self._find_and_open_file(filename)
        self._send_file(response_file)

    def _find_and_open_file(self, filename):
        fd = None
        local_repo_path = "C:/Users/cj/code/gita/FlightSystems/server/flight_ops/static"
        current_dir = os.getcwd()
        print "flight_ops: " + current_dir
        # repo_file = os.path.join(local_repo_path, filename)
        repo_file = local_repo_path + filename
        # current_dir_file = os.path.join(current_dir, filename)
        current_dir_file = current_dir + "/5003" + filename
        try:
            print "motor_drive: **** Trying to open " + repo_file
            fd = open(repo_file, 'r')
        except:
            # if this too raises an exception, let it raise; we don't have anywhere else to look.
            print "motor_drive: **** Trying to open " + current_dir_file
            fd = open(current_dir_file, 'r')
        return fd

    def _send_file(self, fd):
        if fd is None:
            self.send_response(404)
            return
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(fd.read())


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write("Hello from the Generic Handler!")


def run_server(port):
    assert port is not None

    # Serve files from here
    # directory = os.path.join(BASEDIR, str(port))
    # print directory
    # os.chdir(directory)
    
    # Each of these is going to have a bunch of specific requests to handle
    if port == 6001:
        handler = FlightOpsHandler
    elif port == 5007:
        handler = MotorDriveHandler
    elif port == 5003:
        handler = HealthHandler
    else:
        handler = Handler

    # Start the server
    httpd = ThreadingHTTPServer(("", port), handler)
    print "serving at port", port
    httpd.serve_forever()


BASEDIR = os.path.dirname(os.path.abspath(__file__))

# 6001: Flight ops service: contains stuff like recovery/ and config/
thread = threading.Thread(target=run_server, args=(6001,))
thread.start()

# Why don't these two respond??

# 5007: Motor drive service
thread = threading.Thread(target=run_server, args=(5007,))
thread.start()

# 5003: Console
thread = threading.Thread(target=run_server, args=(5003,))
thread.start()
