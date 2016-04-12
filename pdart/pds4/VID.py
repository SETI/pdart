import re
import unittest


class VID(object):
    """Representation of a PDS4 VID."""

    def __init__(self, str):
        """
        Create a VID object from a string, throwing an exception if
        the VID string is malformed.
        """
        vs = str.split('.')

        # Check requirements
        assert len(str) <= 255
        assert len(vs) == 2
        for v in vs:
            assert re.match('\\A(0|[1-9][0-9]*)\\Z', v)

        self.VID = str
        self.major = int(vs[0])
        self.minor = int(vs[1])

    def __cmp__(self, other):
        res = self.major - other.major
        if res == 0:
            res = self.minor - other.minor
        return res

    def __str__(self):
        return self.VID

    def __repr__(self):
        return 'VID(%r)' % self.VID

############################################################


class TestVID(unittest.TestCase):
    def test_init(self):
        # sanity-check
        with self.assertRaises(Exception):
            VID(None)

        with self.assertRaises(Exception):
            VID('foo')

        VID('0.0')
        with self.assertRaises(Exception):
            VID('0.0.0')
        with self.assertRaises(Exception):
            VID('5.')
        with self.assertRaises(Exception):
            VID('.5')
        with self.assertRaises(Exception):
            VID('0.01')

        # test fields
        v = VID('3.14159265')
        self.assertEqual(3, v.major)
        self.assertEqual(14159265, v.minor)

    def test_cmp(self):
        self.assertTrue(VID('2.3') == VID('2.3'))
        self.assertTrue(VID('2.3') != VID('2.4'))
        self.assertTrue(VID('2.3') < VID('3.2'))
        self.assertTrue(VID('2.3') > VID('2.2'))

    def test_str(self):
        self.assertEquals('2.3', str(VID('2.3')))

    def test_repr(self):
        self.assertEquals("VID('2.3')", repr(VID('2.3')))

if __name__ == '__main__':
    unittest.main()