import unittest

from fs.path import join
from fs.tempfs import TempFS
from typing import TYPE_CHECKING

from pdart.fs.DirUtils import lid_to_dir
from pdart.fs.MultiversionBundleFS import MultiversionBundleFS
from pdart.fs.VersionView import VersionView
from pdart.pds4.LIDVID import LIDVID
from pdart.update.Update import is_fits_file, update_bundle

if TYPE_CHECKING:
    from fs.base import FS
    from pdart.update.Update import FILENAME_FILTER
    from pdart.fs.CopyOnWriteFS import CopyOnWriteVersionView


class Test_Update(unittest.TestCase):
    def setUp(self):
        # type: () -> None
        mvfs = MultiversionBundleFS(TempFS())

        # >>> write empty_tree
        bundle_lidvid = LIDVID('urn:nasa:pds:b::1')
        collection_lidvid = LIDVID('urn:nasa:pds:b:c::1')
        collection2_lidvid = LIDVID('urn:nasa:pds:b:c2::1')
        product_lidvid = LIDVID('urn:nasa:pds:b:c:p::1')
        product2_lidvid = LIDVID('urn:nasa:pds:b:c:p2::1')
        product3_lidvid = LIDVID('urn:nasa:pds:b:c2:p3::1')

        mvfs.make_lidvid_directories(bundle_lidvid)
        mvfs.add_subcomponent(bundle_lidvid, collection_lidvid)
        mvfs.add_subcomponent(bundle_lidvid, collection2_lidvid)
        mvfs.add_subcomponent(collection_lidvid, product_lidvid)
        mvfs.add_subcomponent(collection_lidvid, product2_lidvid)
        mvfs.add_subcomponent(collection2_lidvid, product3_lidvid)
        # <<< end write empty tree

        vv = VersionView(bundle_lidvid, mvfs)
        vv.settext(join(lid_to_dir(product_lidvid.lid()), u"foo.fits"),
                   u'some text')
        vv.settext(join(lid_to_dir(product_lidvid.lid()), u"bar.fits"),
                   u'some other text')

        vv.settext(join(lid_to_dir(product2_lidvid.lid()), u'baz.fits'),
                   u'blah blah blah')

        vv.settext(join(lid_to_dir(product3_lidvid.lid()), u'beep.fits'),
                   u'BEEP BEEP!')

        self.multiversioned_fs = mvfs

        self.last_bundle_lidvid = bundle_lidvid

    def tearDown(self):
        self.multiversioned_fs = None
        self.last_bundle_lidvid = None

    def assert_filtered_filesystems_equal(self, lhs, rhs, include_file):
        # type: (FS, FS, FILENAME_FILTER) -> None
        """
        Assert that the two filesystems have identical contents after
        filtering out files that fail the filter.
        """

        def assert_entries_equal_at(path):
            # type: (unicode) -> None
            if lhs.isdir(path) or rhs.isdir(path):
                assert_directories_equal_at(path)
            else:
                assert_files_equal_at(path)

        def assert_directories_equal_at(path):
            # type: (unicode) -> None
            self.assertTrue(lhs.isdir(path),
                            '%s is not a directory in lhs' % path)
            self.assertTrue(lhs.exists(path),
                            'directory %s does not exist in lhs' % path)
            self.assertTrue(rhs.isdir(path),
                            '%s is not a directory in rhs' % path)
            self.assertTrue(rhs.exists(path),
                            'directory %s does not exist in rhs' % path)
            # check file contents
            entries = set(lhs.listdir(path) + rhs.listdir(path))
            for entry in entries:
                child_path = join(path, entry)
                assert_entries_equal_at(child_path)

        def assert_files_equal_at(path):
            # type: (unicode) -> None
            if not include_file(path):
                return
            self.assertTrue(lhs.exists(path),
                            'file %s does not exist in lhs' % path)
            self.assertTrue(rhs.exists(path),
                            'file %s does not exist in rhs' % path)
            lhs_bytes = lhs.getbytes(path)
            rhs_bytes = rhs.getbytes(path)

            self.assertEqual(lhs_bytes, rhs_bytes,
                             'file contents at %s are not equal: %s /= %s' %
                             (path, lhs_bytes, rhs_bytes))

        lhs.tree()
        rhs.tree()
        assert_directories_equal_at(u'/')

    def test_update_bundle_with_empty_update(self):
        # type: () -> None
        def update(_fs):
            # type: (CopyOnWriteVersionView) -> None
            pass

        update_bundle(self.multiversioned_fs,
                      self.last_bundle_lidvid,
                      True, update)
        # doing nothing does not update the bundle
        self.assertEqual(self.last_bundle_lidvid,
                         self.multiversioned_fs.current_bundle_lidvid())

    def test_update_bundle_with_file_update(self):
        # type: () -> None
        def update(fs):
            # type: (CopyOnWriteVersionView) -> None
            fs.settext(u'/b/c/p/foo.fits', u'something new')

        cow_fs = update_bundle(self.multiversioned_fs,
                               self.last_bundle_lidvid,
                               True, update)

        # TODO changing a file does update the bundle
        curr_bundle_lidvid = self.multiversioned_fs.current_bundle_lidvid()
        self.assertNotEqual(self.last_bundle_lidvid,
                            curr_bundle_lidvid)
        self.assertEqual(self.last_bundle_lidvid.next_major_lidvid(),
                         curr_bundle_lidvid)

        old_vv = cow_fs
        new_vv = VersionView(curr_bundle_lidvid, self.multiversioned_fs)
        self.assert_filtered_filesystems_equal(old_vv, new_vv, is_fits_file)

    def test_update_bundle_with_file_addition(self):
        # type: () -> None
        def update(fs):
            # type: (CopyOnWriteVersionView) -> None
            fs.settext(u'/b/c/p/foobar.fits', u"I'm a new file")

        cow_fs = update_bundle(self.multiversioned_fs,
                               self.last_bundle_lidvid,
                               True, update)

        # TODO changing a file does update the bundle
        curr_bundle_lidvid = self.multiversioned_fs.current_bundle_lidvid()
        self.assertNotEqual(self.last_bundle_lidvid,
                            curr_bundle_lidvid)
        self.assertEqual(self.last_bundle_lidvid.next_major_lidvid(),
                         curr_bundle_lidvid)

        old_vv = cow_fs
        new_vv = VersionView(curr_bundle_lidvid, self.multiversioned_fs)
        self.assert_filtered_filesystems_equal(old_vv, new_vv, is_fits_file)

    def test_update_bundle_with_file_deletion(self):
        # type: () -> None
        def update(fs):
            # type: (CopyOnWriteVersionView) -> None
            fs.remove(u'/b/c/p/foo.fits')

        cow_fs = update_bundle(self.multiversioned_fs,
                               self.last_bundle_lidvid,
                               False, update)
        # TODO changing a file does update the bundle
        curr_bundle_lidvid = self.multiversioned_fs.current_bundle_lidvid()
        self.assertNotEqual(self.last_bundle_lidvid,
                            curr_bundle_lidvid)
        self.assertEqual(self.last_bundle_lidvid.next_minor_lidvid(),
                         curr_bundle_lidvid)

        old_vv = cow_fs
        new_vv = VersionView(curr_bundle_lidvid, self.multiversioned_fs)
        self.assert_filtered_filesystems_equal(old_vv, new_vv, is_fits_file)

    def test_update_bundle_with_product_deletion(self):
        # type: () -> None
        def update(fs):
            # type: (CopyOnWriteVersionView) -> None
            fs.removetree(u'/b/c/p')

        cow_fs = update_bundle(self.multiversioned_fs,
                               self.last_bundle_lidvid,
                               False, update)
        # TODO changing a file does update the bundle
        curr_bundle_lidvid = self.multiversioned_fs.current_bundle_lidvid()
        self.assertNotEqual(self.last_bundle_lidvid,
                            curr_bundle_lidvid)
        self.assertEqual(self.last_bundle_lidvid.next_minor_lidvid(),
                         curr_bundle_lidvid)

        old_vv = cow_fs
        new_vv = VersionView(curr_bundle_lidvid, self.multiversioned_fs)
        self.assert_filtered_filesystems_equal(old_vv, new_vv, is_fits_file)

    # @unittest.skip
    def test_update_bundle_with_product_addition(self):
        # type: () -> None
        def update(fs):
            # type: (CopyOnWriteVersionView) -> None
            fs.makedirs(u'/b/c/p7')
            fs.settext(u'/b/c/p7/foo.txt', u'xxx')

        cow_fs = update_bundle(self.multiversioned_fs,
                               self.last_bundle_lidvid,
                               False, update)
        # TODO changing a file does update the bundle
        curr_bundle_lidvid = self.multiversioned_fs.current_bundle_lidvid()
        self.assertNotEqual(self.last_bundle_lidvid,
                            curr_bundle_lidvid)
        self.assertEqual(self.last_bundle_lidvid.next_minor_lidvid(),
                         curr_bundle_lidvid)

        old_vv = cow_fs
        new_vv = VersionView(curr_bundle_lidvid, self.multiversioned_fs)
        self.assert_filtered_filesystems_equal(old_vv, new_vv, is_fits_file)

    def test_update_bundle_with_collection_deletion(self):
        # type: () -> None
        def update(fs):
            # type: (CopyOnWriteVersionView) -> None
            fs.removetree(u'/b/c')

        cow_fs = update_bundle(self.multiversioned_fs,
                               self.last_bundle_lidvid,
                               False, update)
        # TODO changing a file does update the bundle
        curr_bundle_lidvid = self.multiversioned_fs.current_bundle_lidvid()
        self.assertNotEqual(self.last_bundle_lidvid,
                            curr_bundle_lidvid)
        self.assertEqual(self.last_bundle_lidvid.next_minor_lidvid(),
                         curr_bundle_lidvid)

        old_vv = cow_fs
        new_vv = VersionView(curr_bundle_lidvid, self.multiversioned_fs)
        self.assert_filtered_filesystems_equal(old_vv, new_vv, is_fits_file)

    def test_update_bundle_with_collection_addition(self):
        # type: () -> None
        def update(fs):
            # type: (CopyOnWriteVersionView) -> None
            fs.makedirs(u'/b/c7/p8')
            fs.touch(u'/b/c7/p8/foo.fits')

        cow_fs = update_bundle(self.multiversioned_fs,
                               self.last_bundle_lidvid,
                               False, update)
        # TODO changing a file does update the bundle
        curr_bundle_lidvid = self.multiversioned_fs.current_bundle_lidvid()
        self.assertNotEqual(self.last_bundle_lidvid,
                            curr_bundle_lidvid)
        self.assertEqual(self.last_bundle_lidvid.next_minor_lidvid(),
                         curr_bundle_lidvid)

        old_vv = cow_fs
        new_vv = VersionView(curr_bundle_lidvid, self.multiversioned_fs)
        self.assert_filtered_filesystems_equal(old_vv, new_vv, is_fits_file)