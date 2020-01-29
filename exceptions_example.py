# From programiz.com/python-programming/user-defined-exception
# Example in a tutorial
# with some edits to make it work in python 2.7.

from __future__ import print_function
import sys

# define Python user-defined exceptions
class Error(Exception):
    """Base class for other exceptions"""
    pass
class ValueTooSmallError(Error):
    """Raised when the input value is too small"""
    pass
class ValueTooLargeError(Error):
    """Raised when the input value is too large"""
    pass
# our main program
# user guesses a number until he/she gets it right
# you need to guess this number
number = 432
print("Guess a number!")
print()
while True:
    try:
        print("Enter a number: ", end='')
        sys.stdout.flush()
        i_num = int(raw_input())
        if i_num < number:
            raise ValueTooSmallError
        elif i_num > number:
            raise ValueTooLargeError
        break
    except ValueTooSmallError:
        print("This value is too small, try again!")
        print()
#    except ValueTooLargeError:
#        print("This value is too large, try again!")
#        print()
print("Congratulations! You guessed it correctly.")
