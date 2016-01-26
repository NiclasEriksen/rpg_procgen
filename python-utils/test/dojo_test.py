import sys
import unittest
from utils import dojo


def slow(env, count):
    plist = []
    for x in range(count):
        plist.append(x)
    return plist


fast = lambda e, c: range(c)


def bad(env):
    return 1.0


def good(env):
    return 0.2


class DojoTest(unittest.TestCase):

    def test_Dojo(self):
        funcs = [slow, fast]
        environ = 55
        mydojo = dojo.Dojo(funcs, environ)
        self.assertSequenceEqual(funcs, mydojo.algorithms)
        self.assertEqual(environ, mydojo.environ)

    def test_TimingDojo_train(self):
        mydojo = dojo.TimingDojo([slow, fast], None)
        result = mydojo.train(55)
        self.assertEqual(result, fast)

    def test_FitnessDojo_train(self):
        mydojo = dojo.FitnessDojo([bad, good], None)
        result = mydojo.train()
        self.assertEqual(result, good)


if __name__ == "__main__":
    sys.exit(unittest.main())
