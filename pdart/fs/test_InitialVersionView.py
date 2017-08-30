from pdart.fs.InitialVersionView import *
from pdart.fs.VersionedViewTestCases import *
import unittest

from fs.memoryfs import MemoryFS

_ROOT = u'/'
# type: unicode

_V1 = u'v$1'
# type: unicode

_BUNDLE_ID = u'hst_00000'
# type: unicode

_ALL = [u'*']
# type: List[unicode]

_VERSION_DIRS = [u'v$*']
# type: List[unicode]

_SUBDIR_VERSIONS_FILENAME = u'subdir$versions.txt'
# type: unicode


class TestInitialVersionView(unittest.TestCase):
    def setUp(self):
        self.legacy_fs = MemoryFS()
        self.bundle_id = _BUNDLE_ID
        self.view = InitialVersionView(self.bundle_id, self.legacy_fs)

    def test_bare_fs(self):
        """
        Test that the proper hierarchy is synthesized even for an
        empty legacy filesystem.
        """
        BUNDLE_DIR = join(_ROOT, _BUNDLE_ID)
        self.assertTrue(self.view.exists(_ROOT))
        self.assertTrue(self.view.isdir(_ROOT))
        self.assertEqual([_BUNDLE_ID], self.view.listdir(_ROOT))
        self.assertTrue(self.view.exists(BUNDLE_DIR))
        self.assertTrue(self.view.isdir(BUNDLE_DIR))
        self.assertEqual([_V1], self.view.listdir(BUNDLE_DIR))

        BUNDLE_DIR_V1 = join(BUNDLE_DIR, _V1)
        self.assertTrue(self.view.exists(BUNDLE_DIR_V1))
        self.assertTrue(self.view.isdir(BUNDLE_DIR_V1))
        self.assertEqual([_SUBDIR_VERSIONS_FILENAME],
                         self.view.listdir(BUNDLE_DIR_V1))

        # add a label
        BUNDLE_LABEL_FILENAME = u'bundle.xml'
        self.legacy_fs.touch(BUNDLE_LABEL_FILENAME)
        BUNDLE_LABEL_FILEPATH = join(_ROOT,
                                     _BUNDLE_ID,
                                     _V1,
                                     BUNDLE_LABEL_FILENAME)
        self.assertTrue(self.view.exists(BUNDLE_LABEL_FILEPATH))
        self.assertTrue(self.view.isfile(BUNDLE_LABEL_FILEPATH))
        self.assertEquals("", self.view.gettext(BUNDLE_LABEL_FILEPATH))

    def test_collection(self):
        """
        Test that the proper hierarchy is synthesized even for an
        empty collection in a legacy filesystem.
        """
        COLLECTION_ID = u'data_xxx_raw'
        COLLECTION_DIR = join(_ROOT, _BUNDLE_ID, COLLECTION_ID)
        self.legacy_fs.makedir(COLLECTION_ID)
        self.assertTrue(self.view.exists(COLLECTION_DIR))
        self.assertTrue(self.view.isdir(COLLECTION_DIR))
        self.assertEqual([_V1], self.view.listdir(COLLECTION_DIR))

        COLLECTION_DIR_V1 = join(COLLECTION_DIR, _V1)
        self.assertTrue(self.view.exists(COLLECTION_DIR_V1))
        self.assertTrue(self.view.isdir(COLLECTION_DIR_V1))
        self.assertEqual([_SUBDIR_VERSIONS_FILENAME],
                         self.view.listdir(COLLECTION_DIR_V1))

        # add a label
        COLLECTION_LABEL_FILENAME = u'collection.xml'
        self.legacy_fs.touch(join(COLLECTION_ID, COLLECTION_LABEL_FILENAME))
        COLLECTION_LABEL_FILEPATH = join(_ROOT,
                                         _BUNDLE_ID,
                                         COLLECTION_ID,
                                         _V1,
                                         COLLECTION_LABEL_FILENAME)
        self.assertTrue(self.view.exists(COLLECTION_LABEL_FILEPATH))
        self.assertTrue(self.view.isfile(COLLECTION_LABEL_FILEPATH))
        self.assertEquals("", self.view.gettext(COLLECTION_LABEL_FILEPATH))

    def test_product(self):
        """
        Test that the proper hierarchy is synthesized even for an
        single product in a legacy filesystem.
        """
        COLLECTION_ID = u'data_xxx_raw'
        COLLECTION_DIR = join(_ROOT, _BUNDLE_ID, COLLECTION_ID)
        VISIT = u'visit_xx'
        PRODUCT_ID = u'u2q9xx01j_raw'
        PRODUCT_DIR = join(COLLECTION_DIR, PRODUCT_ID)
        PRODUCT_DIR_V1 = join(PRODUCT_DIR, _V1)
        FITS_FILENAME = PRODUCT_ID + '.fits'
        FITS_FILEPATH = join(PRODUCT_DIR_V1, FITS_FILENAME)

        self.legacy_fs.makedirs(join(COLLECTION_ID, VISIT))
        self.legacy_fs.touch(join(COLLECTION_ID, VISIT, FITS_FILENAME))

        self.assertTrue(self.view.exists(PRODUCT_DIR))
        self.assertTrue(self.view.isdir(PRODUCT_DIR))
        self.assertEquals([_V1], self.view.listdir(PRODUCT_DIR))

        self.assertTrue(self.view.exists(PRODUCT_DIR_V1))
        self.assertTrue(self.view.isdir(PRODUCT_DIR_V1))
        self.assertEquals(set([FITS_FILENAME, _SUBDIR_VERSIONS_FILENAME]),
                          set(self.view.listdir(PRODUCT_DIR_V1)))

        self.assertTrue(self.view.exists(FITS_FILEPATH))
        self.assertTrue(self.view.isfile(FITS_FILEPATH))

        # add a label
        PRODUCT_LABEL_FILENAME = PRODUCT_ID + '.xml'
        self.legacy_fs.touch(join(COLLECTION_ID,
                                  VISIT,
                                  PRODUCT_LABEL_FILENAME))
        PRODUCT_LABEL_FILEPATH = join(_ROOT,
                                      _BUNDLE_ID,
                                      COLLECTION_ID,
                                      PRODUCT_ID,
                                      _V1,
                                      PRODUCT_LABEL_FILENAME)
        self.assertTrue(self.view.exists(PRODUCT_LABEL_FILEPATH))
        self.assertTrue(self.view.isfile(PRODUCT_LABEL_FILEPATH))
        self.assertEquals("", self.view.gettext(PRODUCT_LABEL_FILEPATH))


class TestInitialVersionViewAsVersionedView(VersionedViewTestCases,
                                            unittest.TestCase):
    def make_fs(self):
        self.memoryFS = MemoryFS()
        self.memoryFS.makedirs(u'/data_xxx_raw/visit_xx')
        self.memoryFS.touch(u'/data_xxx_raw/visit_xx/u2q9xx01j_raw.fits')
        return InitialVersionView(_BUNDLE_ID, self.memoryFS)

    def destroy_fs(self, fs):
        fs.close()
        self.memoryFS.close()

    def check_subdir_versions_file(self,
                                   version_dir,
                                   subdir_versions_filepath):
        # call the superclass's version
        VersionedViewTestCases.check_subdir_versions_file(
            self, version_dir, subdir_versions_filepath)

        # In a filesystem with only one version, we have one
        # additional condition: all subdirectories in the filesystem
        # should appear in the subdir_versions file.
        expected = set(info.name
                       for info
                       in self.view.filterdir(join(version_dir, '..'),
                                              None, None,
                                              _VERSION_DIRS, _ALL))

        actual = set()
        with self.view.open(subdir_versions_filepath) as f:
            for line in f:
                actual.add(line.split()[0])

        # self.assertEqual(expected, actual)
