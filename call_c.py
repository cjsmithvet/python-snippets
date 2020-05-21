""" Simple examples of calling C functions through ctypes module. """
import ctypes
import pathlib


if __name__ == "__main__":
    # Load the shared library into c types.
    # libname = pathlib.Path().absolute() / "libcmult.so"
    libname = "/c/Users/cj/code/git/FlightSystems/build/host_win/server/proxies/libproxies.a"
    print libname
    c_lib = ctypes.CDLL(libname)
