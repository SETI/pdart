import unittest

from fs.tempfs import TempFS
from fs.test import FSTestCases

from pdart.fs.CopyOnWriteFS import CopyOnWriteFS


class TestCopyOnWriteFS(FSTestCases, unittest.TestCase):
    def make_fs(self):
        # type: () -> CopyOnWriteFS
        self.cow_base_fs = TempFS()
        self.cow_delta_fs = TempFS()
        return CopyOnWriteFS(self.cow_base_fs, self.cow_delta_fs)

    def test_getsyspath(self):
        # type: () -> None
        FOO_PATH = u"/foo.txt"

        self.cow_base_fs.settext(FOO_PATH, u"foo")

        # the file exists in the base_fs
        self.assertEqual(
            self.cow_base_fs.getsyspath(FOO_PATH), self.fs.getsyspath(FOO_PATH)
        )

        # then we overwrite it; it now exists in the delta_fs
        self.fs.settext(FOO_PATH, u"bar")
        self.assertEqual(
            self.cow_delta_fs.getsyspath(FOO_PATH), self.fs.getsyspath(FOO_PATH)
        )

        # now we delete it; any new changes would go into the delta_fs
        self.fs.remove(FOO_PATH)
        self.assertEqual(
            self.cow_delta_fs.getsyspath(FOO_PATH), self.fs.getsyspath(FOO_PATH)
        )

        BAR_PATH = u"/bar.txt"
        self.cow_base_fs.settext(BAR_PATH, u"bar")

        # the file exists in the base_fs
        self.assertEqual(
            self.cow_base_fs.getsyspath(BAR_PATH), self.fs.getsyspath(BAR_PATH)
        )

        # now we delete it; any new changes would go into the delta_fs
        self.fs.remove(BAR_PATH)
        self.assertEqual(
            self.cow_delta_fs.getsyspath(BAR_PATH), self.fs.getsyspath(BAR_PATH)
        )

        FOOBAR_PATH = u"/foobar.txt"
        # file never existed; any new changes would go into the delta_fs
        self.assertEqual(
            self.cow_delta_fs.getsyspath(FOOBAR_PATH), self.fs.getsyspath(FOOBAR_PATH)
        )

    def test_fs_delta(self):
        # type: () -> None
        delta = self.fs.delta()
        self.assertTrue(delta)
        self.assertIs(self.cow_delta_fs, delta.additions())
        self.assertFalse(delta.deletions())

        BAR_PATH = u"/bar.txt"
        FOO_PATH = u"/foo.txt"

        self.cow_base_fs.settext(FOO_PATH, u"FOO!")
        self.fs.remove(FOO_PATH)
        delta = self.fs.delta()
        self.assertTrue(self.cow_base_fs.exists(FOO_PATH))
        self.assertFalse(delta.additions().exists(FOO_PATH))
        self.assertEqual(set([FOO_PATH]), delta.deletions())

        self.fs.settext(BAR_PATH, u"BAR!")
        delta = self.fs.delta()
        self.assertFalse(self.cow_base_fs.exists(BAR_PATH))
        self.assertTrue(delta.additions().exists(BAR_PATH))

    def test_remove_duplicates(self):
        # type: () -> None

        # set the files in the base
        self.cow_base_fs.makedir(u"/foo")
        FOO_BAR_PATH = u"/foo/bar.txt"
        FOO_BAZ_PATH = u"/foo/baz.txt"
        self.cow_base_fs.settext(FOO_BAR_PATH, u"BAR!")
        self.cow_base_fs.settext(FOO_BAZ_PATH, u"BAZ!")

        # lowercase, then re-uppercase BAR.
        self.fs.settext(FOO_BAR_PATH, u"bar!")
        self.assertEqual(u"bar!", self.fs.gettext(FOO_BAR_PATH))
        self.fs.settext(FOO_BAR_PATH, u"BAR!")
        self.assertEqual(u"BAR!", self.fs.gettext(FOO_BAR_PATH))

        # just lowercase BAZ.
        self.fs.settext(FOO_BAZ_PATH, u"baz!")
        self.assertEqual(u"baz!", self.fs.gettext(FOO_BAZ_PATH))

        # sanity test
        delta = self.fs.delta()
        self.assertEqual(set([FOO_BAR_PATH, FOO_BAZ_PATH]), delta.deletions())
        self.assertTrue(delta.additions().exists(FOO_BAR_PATH))
        self.assertTrue(delta.additions().exists(FOO_BAZ_PATH))

        # now normalize.  it should erase the BAR actions.
        self.fs.normalize()

        delta = self.fs.delta()
        self.assertEqual(set([FOO_BAZ_PATH]), delta.deletions())
        self.assertFalse(delta.additions().exists(FOO_BAR_PATH))
        self.assertTrue(delta.additions().exists(FOO_BAZ_PATH))

    def test_remove_empty_dirs(self):
        self.fs.makedirs(u"/a/b/c/d")
        self.fs.makedirs(u"/a/e/f/g")
        self.fs.touch(u"/a/e/f/foo.txt")
        self.fs.normalize()
        self.assertFalse(self.cow_delta_fs.exists(u"/a/b"))
        self.assertFalse(self.cow_delta_fs.exists(u"/a/e/f/g"))
        self.assertTrue(self.cow_delta_fs.exists(u"/a/e/f/foo.txt"))

    def test_directories_empty_case(self):
        self.fs.normalize()
        self.assertFalse(self.fs.delta().directories())

    def test_directories_deletion_case(self):
        self.cow_base_fs.makedirs(u"/foo/bar/baz")
        self.cow_base_fs.touch(u"/foo/bar/baz/quux.txt")

        self.fs.remove(u"/foo/bar/baz/quux.txt")
        self.fs.touch(u"/foo/bar/baz/quux.txt")
        self.fs.normalize()
        self.assertFalse(self.fs.delta().directories())

    def test_directories_deletion_case2(self):
        self.cow_base_fs.makedirs(u"/foo/bar/baz")
        self.cow_base_fs.touch(u"/foo/bar/baz/quux.txt")

        self.fs.remove(u"/foo/bar/baz/quux.txt")
        self.fs.touch(u"/foo/bar/baz/quux.txt")
        self.fs.touch(u"/foo/bar/baz/quux2.txt")
        self.fs.normalize()
        self.assertEqual(
            {u"/", u"/foo", u"/foo/bar", u"/foo/bar/baz"}, self.fs.delta().directories()
        )

    def test_directories_multiple_cases(self):
        # set the files in the base
        self.cow_base_fs.makedir(u"/foo")
        FOO_BAR_PATH = u"/foo/bar.txt"
        FOO_BAZ_PATH = u"/foo/baz.txt"
        self.cow_base_fs.settext(FOO_BAR_PATH, u"BAR!")
        self.cow_base_fs.settext(FOO_BAZ_PATH, u"BAZ!")

        # lowercase, then re-uppercase BAR.
        self.fs.settext(FOO_BAR_PATH, u"bar!")
        self.assertEqual(u"bar!", self.fs.gettext(FOO_BAR_PATH))
        self.fs.settext(FOO_BAR_PATH, u"BAR!")
        self.assertEqual(u"BAR!", self.fs.gettext(FOO_BAR_PATH))

        # just lowercase BAZ.
        self.fs.settext(FOO_BAZ_PATH, u"baz!")
        self.assertEqual(u"baz!", self.fs.gettext(FOO_BAZ_PATH))

        # something in the root directory
        self.fs.touch(u"/quux.txt")

        # make some empty dirs
        self.fs.makedirs(u"/a/b/c/d")
        self.fs.makedirs(u"/a/e/f/g")
        self.fs.touch(u"/a/e/f/foo.txt")

        self.fs.normalize()

        fs_delta = self.fs.delta()
        expected = {u"/foo", u"/a/e/f", u"/a/e", u"/a", u"/"}
        self.assertEqual(expected, fs_delta.directories())