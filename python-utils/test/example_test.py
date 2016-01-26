import sys
import unittest
from .util.testutils import interactive, doprint

# You can use relative imports, if you like
# from .. import FOO


class SomeExampleTest(unittest.TestCase):
    # Tags can be set on the class level
    __tags__ = ["mytag", "anothertag"]

    def test_whatever(self):
        pass

    # Query user input with a y/n answer AFTER the test was run
    @interactive("Was the result acceptable?")
    def test_something_interactive(self):
        # Interact with the user - the test will be paused until the user
        # presses enter
        doprint("Dear user, please do something")
        # ...
        pass

    # Do not query user input, but require the test method to interact with
    # the user
    @interactive()
    def test_something_else_interactive(self):
        doprint("Attention, please rotate your chair now!")

# Everything else supported by unittest works as well.

if __name__ == "__main__":
    sys.exit(unittest.main())

