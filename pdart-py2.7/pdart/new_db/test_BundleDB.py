import os
import tempfile
import unittest

from typing import TYPE_CHECKING

from pdart.new_db.BundleDB import create_bundle_db_in_memory
from pdart.new_db.SqlAlchTables import Base, Bundle, NonDocumentCollection
from pdart.new_db.Utils import file_md5
from pdart.new_labels.CollectionInventory import get_collection_inventory_name
from pdart.new_labels.CollectionLabel import get_collection_label_name
from pdart.pds4.LIDVID import LIDVID

if TYPE_CHECKING:
    from typing import Set

_TABLES = {'bundles',
           'collections', 'document_collections', 'non_document_collections',
           'products', 'browse_products', 'document_products', 'fits_products',
           'files', 'fits_files', 'bad_fits_files', 'browse_files',
           'document_files',
           'hdus', 'cards',
           'bundle_labels', 'collection_labels',
           'collection_inventories', 'product_labels',
           'proposal_info'}  # type: Set[str]


class Test_BundleDB(unittest.TestCase):
    def setUp(self):
        # type: () -> None
        self.db = create_bundle_db_in_memory()
        self.db.create_tables()
        (handle, filepath) = tempfile.mkstemp()
        os.write(handle, os.urandom(32))
        os.close(handle)
        self.dummy_os_filepath = filepath

    def tearDown(self):
        os.remove(self.dummy_os_filepath)

    def test_BundleDB(self):
        # type: () -> None
        db = self.db
        self.assertTrue(db.is_open())
        metadata = Base.metadata
        self.assertEqual(set(metadata.tables.keys()), _TABLES)
        db.close()
        self.assertFalse(db.is_open())

    ############################################################

    def test_create_bundle(self):
        # type: () -> None
        bundle_lidvid = 'urn:nasa:pds:hst_99999::1.1'
        self.assertTrue(self.db.session.query(Bundle).filter(
            Bundle.lidvid == bundle_lidvid).count() == 0)
        self.assertFalse(self.db.bundle_exists(bundle_lidvid))
        self.db.create_bundle(bundle_lidvid)
        self.assertTrue(self.db.session.query(Bundle).filter(
            Bundle.lidvid == bundle_lidvid).count() == 1)
        self.assertTrue(self.db.bundle_exists(bundle_lidvid))
        self.db.create_bundle(bundle_lidvid)
        self.assertTrue(self.db.bundle_exists(bundle_lidvid))

    def test_bundle_exists(self):
        # type: () -> None
        bundle_lidvid = 'urn:nasa:pds:hst_99999::1.1'
        self.assertFalse(self.db.bundle_exists(bundle_lidvid))
        self.db.create_bundle(bundle_lidvid)
        self.assertTrue(self.db.bundle_exists(bundle_lidvid))

    def test_get_bundle(self):
        # type: () -> None
        bundle_lidvid = 'urn:nasa:pds:hst_99999::1.1'
        self.db.create_bundle(bundle_lidvid)
        bundle = self.db.get_bundle()
        self.assertEqual(bundle_lidvid, bundle.lidvid)
        self.assertEqual(99999, bundle.proposal_id)

    def test_get_bundle_collections(self):
        # type: () -> None
        bundle_lidvid = 'urn:nasa:pds:hst_99999::1.1'
        non_doc_collection_lidvid = 'urn:nasa:pds:hst_99999:data_acs_raw::1.1'
        doc_collection_lidvid = 'urn:nasa:pds:hst_99999:document::1.1'

        # test empty
        self.db.create_bundle(bundle_lidvid)
        self.assertFalse(self.db.get_bundle_collections(bundle_lidvid))

        # test inserting one
        self.db.create_non_document_collection(non_doc_collection_lidvid,
                                               bundle_lidvid)
        self.assertEqual({non_doc_collection_lidvid},
                         {c.lidvid
                          for c
                          in self.db.get_bundle_collections(bundle_lidvid)})

        # test inserting a different kind
        self.db.create_document_collection(doc_collection_lidvid,
                                           bundle_lidvid)
        self.assertEqual({non_doc_collection_lidvid, doc_collection_lidvid},
                         {c.lidvid
                          for c
                          in self.db.get_bundle_collections(bundle_lidvid)})

    ############################################################

    def test_create_document_collection(self):
        # type: () -> None
        bundle_lidvid = 'urn:nasa:pds:hst_99999::1.1'
        self.db.create_bundle(bundle_lidvid)

        collection_lidvid = 'urn:nasa:pds:hst_99999:document::1.8'
        self.assertFalse(
            self.db.document_collection_exists(collection_lidvid))

        self.db.create_document_collection(collection_lidvid,
                                           bundle_lidvid)
        self.assertTrue(
            self.db.document_collection_exists(collection_lidvid))

        self.db.create_document_collection(collection_lidvid,
                                           bundle_lidvid)
        self.assertTrue(
            self.db.document_collection_exists(collection_lidvid))

    def test_create_non_document_collection(self):
        # type: () -> None
        bundle_lidvid = 'urn:nasa:pds:hst_99999::1.1'
        self.db.create_bundle(bundle_lidvid)

        collection_lidvid = 'urn:nasa:pds:hst_99999:data_acs_raw::1.8'
        self.assertFalse(
            self.db.non_document_collection_exists(collection_lidvid))

        self.db.create_non_document_collection(collection_lidvid,
                                               bundle_lidvid)
        self.assertTrue(
            self.db.non_document_collection_exists(collection_lidvid))

        self.db.create_non_document_collection(collection_lidvid,
                                               bundle_lidvid)
        self.assertTrue(
            self.db.non_document_collection_exists(collection_lidvid))

    def test_collection_exists(self):
        # type: () -> None
        bundle_lidvid = 'urn:nasa:pds:hst_99999::1.1'
        collection_lidvid = 'urn:nasa:pds:hst_99999:data_acs_raw::1.1'
        self.db.create_bundle(bundle_lidvid)
        self.assertFalse(self.db.collection_exists(collection_lidvid))
        self.db.create_non_document_collection(collection_lidvid,
                                               bundle_lidvid)

        self.assertTrue(self.db.collection_exists(collection_lidvid))

    def test_document_collection_exists(self):
        # type: () -> None
        bundle_lidvid = 'urn:nasa:pds:hst_99999::1.1'
        self.db.create_bundle(bundle_lidvid)

        non_doc_collection_lidvid = 'urn:nasa:pds:hst_99999:data_acs_raw::1.1'
        doc_collection_lidvid = 'urn:nasa:pds:hst_99999:document::1.1'

        self.db.create_non_document_collection(non_doc_collection_lidvid,
                                               bundle_lidvid)
        self.assertFalse(
            self.db.document_collection_exists(
                doc_collection_lidvid))

        self.db.create_document_collection(doc_collection_lidvid,
                                           bundle_lidvid)

        self.assertTrue(
            self.db.document_collection_exists(
                doc_collection_lidvid))

    def test_non_document_collection_exists(self):
        # type: () -> None
        bundle_lidvid = 'urn:nasa:pds:hst_99999::1.1'
        self.db.create_bundle(bundle_lidvid)

        non_doc_collection_lidvid = 'urn:nasa:pds:hst_99999:data_acs_raw::1.1'
        doc_collection_lidvid = 'urn:nasa:pds:hst_99999:document::1.1'

        self.db.create_document_collection(doc_collection_lidvid,
                                           bundle_lidvid)

        self.assertFalse(
            self.db.non_document_collection_exists(
                non_doc_collection_lidvid))

        self.db.create_non_document_collection(non_doc_collection_lidvid,
                                               bundle_lidvid)
        self.assertTrue(
            self.db.non_document_collection_exists(
                non_doc_collection_lidvid))

    def test_get_collection(self):
        bundle_lidvid = 'urn:nasa:pds:hst_99999::1.1'
        self.db.create_bundle(bundle_lidvid)

        collection_lidvid = 'urn:nasa:pds:hst_99999:data_acs_raw::1.8'
        self.db.create_non_document_collection(collection_lidvid,
                                               bundle_lidvid)

        collection = self.db.get_collection(collection_lidvid)
        self.assertEqual(NonDocumentCollection, type(collection))
        self.assertEqual('acs', collection.instrument)
        self.assertEqual('raw', collection.suffix)

    def test_get_collection_products(self):
        # type: () -> None
        bundle_lidvid = 'urn:nasa:pds:hst_99999::1.1'
        collection_lidvid = 'urn:nasa:pds:hst_99999:data_acs_raw::1.8'
        p1_lidvid = 'urn:nasa:pds:hst_99999:data_acs_raw:j6gp01lzq::1.8'
        p2_lidvid = 'urn:nasa:pds:hst_99999:data_acs_raw:j6gp02lzq::1.8'
        p3_lidvid = 'urn:nasa:pds:hst_99999:data_acs_raw:j6gp03lzq::1.8'

        self.db.create_bundle(bundle_lidvid)
        self.db.create_non_document_collection(collection_lidvid,
                                               bundle_lidvid)
        self.assertFalse(self.db.get_collection_products(
            collection_lidvid))

        self.db.create_fits_product(p1_lidvid,
                                    collection_lidvid)

        self.assertEqual({p1_lidvid},
                         {p.lidvid
                          for p
                          in self.db.get_collection_products(
                             collection_lidvid)})

        self.db.create_fits_product(p2_lidvid,
                                    collection_lidvid)

        self.assertEqual({p1_lidvid, p2_lidvid},
                         {p.lidvid
                          for p
                          in self.db.get_collection_products(
                             collection_lidvid)})

        self.db.create_fits_product(p3_lidvid,
                                    collection_lidvid)

        self.assertEqual({p1_lidvid, p2_lidvid, p3_lidvid},
                         {p.lidvid
                          for p
                          in self.db.get_collection_products(
                             collection_lidvid)})

    ############################################################

    def test_create_browse_product(self):
        # type: () -> None
        bundle_lidvid = 'urn:nasa:pds:hst_99999::1.1'
        self.db.create_bundle(bundle_lidvid)

        data_collection_lidvid = 'urn:nasa:pds:hst_99999:data_acs_raw::1.8'
        self.db.create_non_document_collection(data_collection_lidvid,
                                               bundle_lidvid)

        browse_collection_lidvid = 'urn:nasa:pds:hst_99999:browse_acs_raw::1.8'
        self.db.create_non_document_collection(browse_collection_lidvid,
                                               bundle_lidvid)

        fits_product_lidvid = 'urn:nasa:pds:hst_99999:data_acs_raw:p::8.1'
        browse_product_lidvid = 'urn:nasa:pds:hst_99999:browse_acs_raw:p::8.1'

        with self.assertRaises(Exception):
            self.db.create_browse_product(browse_product_lidvid,
                                          fits_product_lidvid,
                                          browse_collection_lidvid)

        self.db.create_fits_product(fits_product_lidvid,
                                    data_collection_lidvid)

        self.assertFalse(self.db.browse_product_exists(browse_product_lidvid))

        self.db.create_browse_product(browse_product_lidvid,
                                      fits_product_lidvid,
                                      browse_collection_lidvid)
        self.assertTrue(self.db.browse_product_exists(browse_product_lidvid))

        self.db.create_browse_product(browse_product_lidvid,
                                      fits_product_lidvid,
                                      browse_collection_lidvid)
        self.assertTrue(self.db.browse_product_exists(browse_product_lidvid))

    def test_create_document_product(self):
        # type: () -> None
        bundle_lidvid = 'urn:nasa:pds:hst_99999::1.1'
        self.db.create_bundle(bundle_lidvid)
        collection_lidvid = 'urn:nasa:pds:hst_99999:document::1.8'
        self.db.create_document_collection(collection_lidvid,
                                           bundle_lidvid)
        product_lidvid = 'urn:nasa:pds:hst_99999:document:important_stuff::1.8'
        self.assertFalse(
            self.db.document_product_exists(product_lidvid))

        self.db.create_document_product(product_lidvid,
                                        collection_lidvid)
        self.assertTrue(
            self.db.document_product_exists(product_lidvid))

    def test_create_fits_product(self):
        # type: () -> None
        bundle_lidvid = 'urn:nasa:pds:hst_99999::1.1'
        self.db.create_bundle(bundle_lidvid)

        collection_lidvid = 'urn:nasa:pds:hst_99999:data_acs_raw::1.8'
        self.db.create_non_document_collection(collection_lidvid,
                                               bundle_lidvid)

        product_lidvid = 'urn:nasa:pds:hst_99999:data_acs_raw:p::8.1'
        self.assertFalse(self.db.fits_product_exists(product_lidvid))

        self.db.create_fits_product(product_lidvid, collection_lidvid)
        self.assertTrue(self.db.fits_product_exists(product_lidvid))

        self.db.create_fits_product(product_lidvid, collection_lidvid)
        self.assertTrue(self.db.fits_product_exists(product_lidvid))

    def test_product_exists(self):
        # type: () -> None
        bundle_lidvid = 'urn:nasa:pds:hst_99999::1.1'
        self.db.create_bundle(bundle_lidvid)
        data_coll_lidvid = 'urn:nasa:pds:hst_99999:data_acs_raw::1.8'
        browse_coll_lidvid = 'urn:nasa:pds:hst_99999:browse_acs_raw::1.8'
        doc_coll_lidvid = 'urn:nasa:pds:hst_99999:document::1.8'
        self.db.create_non_document_collection(data_coll_lidvid,
                                               bundle_lidvid)
        self.db.create_non_document_collection(browse_coll_lidvid,
                                               bundle_lidvid)
        self.db.create_document_collection(doc_coll_lidvid,
                                           bundle_lidvid)

        fits_prod_lidvid = \
            'urn:nasa:pds:hst_99999:data_acs_raw:p::1.8'
        browse_prod_lidvid = \
            'urn:nasa:pds:hst_99999:browse_acs_raw:p::1.8'
        doc_prod_lidvid = \
            'urn:nasa:pds:hst_99999:document:specs::1.8'

        self.assertFalse(self.db.product_exists(fits_prod_lidvid))
        self.assertFalse(self.db.product_exists(browse_prod_lidvid))
        self.assertFalse(self.db.product_exists(doc_prod_lidvid))

        self.db.create_fits_product(fits_prod_lidvid,
                                    data_coll_lidvid)

        self.assertTrue(self.db.product_exists(fits_prod_lidvid))
        self.assertFalse(self.db.product_exists(browse_prod_lidvid))
        self.assertFalse(self.db.product_exists(doc_prod_lidvid))

        self.db.create_browse_product(browse_prod_lidvid,
                                      fits_prod_lidvid,
                                      browse_coll_lidvid)

        self.assertTrue(self.db.product_exists(fits_prod_lidvid))
        self.assertTrue(self.db.product_exists(browse_prod_lidvid))
        self.assertFalse(self.db.product_exists(doc_prod_lidvid))

        self.db.create_document_product(doc_prod_lidvid,
                                        doc_coll_lidvid)

        self.assertTrue(self.db.product_exists(fits_prod_lidvid))
        self.assertTrue(self.db.product_exists(browse_prod_lidvid))
        self.assertTrue(self.db.product_exists(doc_prod_lidvid))

    def test_browse_product_exists(self):
        # type: () -> None
        bundle_lidvid = 'urn:nasa:pds:hst_99999::1.1'
        self.db.create_bundle(bundle_lidvid)
        collection_lidvid = 'urn:nasa:pds:hst_99999:browse_acs_raw::1.8'
        self.db.create_non_document_collection(collection_lidvid,
                                               bundle_lidvid)
        fits_prod_lidvid = \
            'urn:nasa:pds:hst_99999:data_acs_raw:p::1.8'
        product_lidvid = \
            'urn:nasa:pds:hst_99999:browse_acs_raw:p::1.8'

        self.assertFalse(self.db.browse_product_exists(product_lidvid))

        self.db.create_fits_product(fits_prod_lidvid,
                                    collection_lidvid)
        self.db.create_browse_product(product_lidvid,
                                      fits_prod_lidvid,
                                      collection_lidvid)
        self.assertTrue(self.db.browse_product_exists(product_lidvid))

    def test_document_product_exists(self):
        # type: () -> None
        bundle_lidvid = 'urn:nasa:pds:hst_99999::1.1'
        self.db.create_bundle(bundle_lidvid)
        collection_lidvid = 'urn:nasa:pds:hst_99999:document::1.8'
        self.db.create_document_collection(collection_lidvid,
                                           bundle_lidvid)
        product_lidvid = 'urn:nasa:pds:hst_99999:document:important_stuff::1.8'

        self.assertFalse(self.db.document_product_exists(product_lidvid))
        self.db.create_document_product(product_lidvid,
                                        collection_lidvid)
        self.assertTrue(self.db.document_product_exists(product_lidvid))

    def test_fits_product_exists(self):
        # type: () -> None
        bundle_lidvid = 'urn:nasa:pds:hst_99999::1.1'
        self.db.create_bundle(bundle_lidvid)
        collection_lidvid = 'urn:nasa:pds:hst_99999:data_acs_raw::1.8'
        self.db.create_non_document_collection(collection_lidvid,
                                               bundle_lidvid)
        product_lidvid = 'urn:nasa:pds:hst_99999:data_acs_raw:p::1.8'

        self.assertFalse(self.db.fits_product_exists(product_lidvid))
        self.db.create_fits_product(product_lidvid,
                                    collection_lidvid)
        self.assertTrue(self.db.fits_product_exists(product_lidvid))

    def test_get_product(self):
        bundle_lidvid = 'urn:nasa:pds:hst_99999::1.1'
        self.db.create_bundle(bundle_lidvid)

        collection_lidvid = 'urn:nasa:pds:hst_99999:data_acs_raw::1.8'
        self.db.create_non_document_collection(collection_lidvid,
                                               bundle_lidvid)

        product_lidvid = 'urn:nasa:pds:hst_99999:data_acs_raw:p::8.1'
        self.db.create_fits_product(product_lidvid, collection_lidvid)

        product = self.db.get_product(product_lidvid)
        self.assertEqual(product_lidvid, product.lidvid)
        self.assertEqual(collection_lidvid, product.collection_lidvid)

    def test_get_product_files(self):
        # type: () -> None
        bundle_lidvid = 'urn:nasa:pds:hst_99999::1.1'
        self.db.create_bundle(bundle_lidvid)

        collection_lidvid = 'urn:nasa:pds:hst_99999:data_acs_raw::1.8'
        self.db.create_non_document_collection(collection_lidvid,
                                               bundle_lidvid)

        product_lidvid = 'urn:nasa:pds:hst_99999:data_acs_raw:p::8.1'
        self.db.create_fits_product(product_lidvid, collection_lidvid)

        self.assertFalse(self.db.get_product_files(product_lidvid))

        self.db.create_fits_file(self.dummy_os_filepath,
                                 'p_raw.fits', product_lidvid, 1)
        self.assertEqual(1, len(self.db.get_product_files(product_lidvid)))

    ############################################################

    def test_create_browse_file(self):
        # type: () -> None
        bundle_lidvid = 'urn:nasa:pds:hst_99999::1.1'
        self.db.create_bundle(bundle_lidvid)

        data_collection_lidvid = 'urn:nasa:pds:hst_99999:data_acs_raw::1.8'
        self.db.create_non_document_collection(data_collection_lidvid,
                                               bundle_lidvid)

        browse_collection_lidvid = 'urn:nasa:pds:hst_99999:browse_acs_raw::1.8'
        self.db.create_non_document_collection(browse_collection_lidvid,
                                               bundle_lidvid)

        fits_product_lidvid = 'urn:nasa:pds:hst_99999:data_acs_raw:p::8.1'
        self.db.create_fits_product(fits_product_lidvid,
                                    data_collection_lidvid)
        browse_product_lidvid = 'urn:nasa:pds:hst_99999:browse_acs_raw:p::8.1'
        self.db.create_browse_product(browse_product_lidvid,
                                      fits_product_lidvid,
                                      browse_collection_lidvid)

        basename = 'file.jpg'
        self.assertFalse(
            self.db.browse_file_exists(basename, browse_product_lidvid))

        self.db.create_browse_file(self.dummy_os_filepath,
                                   basename, browse_product_lidvid, 1)
        self.assertTrue(
            self.db.browse_file_exists(basename, browse_product_lidvid))

        self.db.create_browse_file(self.dummy_os_filepath,
                                   basename, browse_product_lidvid, 1)
        self.assertTrue(
            self.db.browse_file_exists(basename, browse_product_lidvid))

    def test_create_document_file(self):
        # type: () -> None
        bundle_lidvid = 'urn:nasa:pds:hst_99999::1.1'
        self.db.create_bundle(bundle_lidvid)

        collection_lidvid = 'urn:nasa:pds:hst_99999:document::1.8'
        self.db.create_document_collection(collection_lidvid,
                                           bundle_lidvid)

        product_lidvid = 'urn:nasa:pds:hst_99999:document:p::8.1'
        self.db.create_document_product(product_lidvid, collection_lidvid)

        filename = 'stuff.pdf'
        self.assertFalse(self.db.document_file_exists(filename,
                                                      product_lidvid))

        self.db.create_document_file(self.dummy_os_filepath,
                                     filename, product_lidvid)
        self.assertTrue(self.db.document_file_exists(filename,
                                                     product_lidvid))

    def test_create_fits_file(self):
        # type: () -> None
        bundle_lidvid = 'urn:nasa:pds:hst_99999::1.1'
        self.db.create_bundle(bundle_lidvid)

        collection_lidvid = 'urn:nasa:pds:hst_99999:data_acs_raw::1.8'
        self.db.create_non_document_collection(collection_lidvid,
                                               bundle_lidvid)

        product_lidvid = 'urn:nasa:pds:hst_99999:data_acs_raw:p::8.1'
        self.db.create_fits_product(product_lidvid, collection_lidvid)

        basename = 'file.fits'
        self.assertFalse(self.db.fits_file_exists(basename, product_lidvid))

        self.db.create_fits_file(self.dummy_os_filepath,
                                 basename, product_lidvid, 1)
        self.assertTrue(self.db.fits_file_exists(basename, product_lidvid))

        self.db.create_fits_file(self.dummy_os_filepath,
                                 basename, product_lidvid, 1)
        self.assertTrue(self.db.fits_file_exists(basename, product_lidvid))

    def test_file_exists(self):
        # type: () -> None
        bundle_lidvid = 'urn:nasa:pds:hst_99999::1.1'
        self.db.create_bundle(bundle_lidvid)
        raw_collection_lidvid = 'urn:nasa:pds:hst_99999:data_acs_raw::1.8'
        browse_collection_lidvid = 'urn:nasa:pds:hst_99999:browse_acs_raw::1.8'
        doc_collection_lidvid = 'urn:nasa:pds:hst_99999:document::1.8'
        self.db.create_non_document_collection(raw_collection_lidvid,
                                               bundle_lidvid)
        self.db.create_non_document_collection(browse_collection_lidvid,
                                               bundle_lidvid)
        self.db.create_document_collection(doc_collection_lidvid,
                                           bundle_lidvid)
        bad_fits_prod_lidvid = \
            'urn:nasa:pds:hst_99999:data_acs_raw:x::1.8'
        fits_prod_lidvid = \
            'urn:nasa:pds:hst_99999:data_acs_raw:p::1.8'
        browse_prod_lidvid = \
            'urn:nasa:pds:hst_99999:browse_acs_raw:p::1.8'
        doc_prod_lidvid = \
            'urn:nasa:pds:hst_99999:document:specs::1.8'
        self.db.create_fits_product(bad_fits_prod_lidvid,
                                    raw_collection_lidvid)
        self.db.create_fits_product(fits_prod_lidvid,
                                    raw_collection_lidvid)
        self.db.create_browse_product(browse_prod_lidvid,
                                      fits_prod_lidvid,
                                      browse_collection_lidvid)
        self.db.create_document_product(doc_prod_lidvid,
                                        doc_collection_lidvid)

        bad_fits_filename = 'x_raw.fits'
        fits_filename = 'p_raw.fits'
        browse_filename = 'p_raw.jpg'
        doc_filename = 'specs.pdf'
        doc_filename_2 = 'specs.txt'

        self.assertFalse(self.db.file_exists(bad_fits_filename,
                                             bad_fits_prod_lidvid))
        self.assertFalse(self.db.file_exists(fits_filename,
                                             fits_prod_lidvid))
        self.assertFalse(self.db.file_exists(browse_filename,
                                             browse_prod_lidvid))
        self.assertFalse(self.db.file_exists(doc_filename,
                                             doc_prod_lidvid))
        self.assertFalse(self.db.file_exists(doc_filename_2,
                                             doc_prod_lidvid))

        self.db.create_bad_fits_file(self.dummy_os_filepath,
                                     bad_fits_filename,
                                     bad_fits_prod_lidvid,
                                     'kablooey!')

        self.assertTrue(self.db.file_exists(bad_fits_filename,
                                            bad_fits_prod_lidvid))
        self.assertFalse(self.db.file_exists(fits_filename,
                                             fits_prod_lidvid))
        self.assertFalse(self.db.file_exists(browse_filename,
                                             browse_prod_lidvid))
        self.assertFalse(self.db.file_exists(doc_filename,
                                             doc_prod_lidvid))
        self.assertFalse(self.db.file_exists(doc_filename_2,
                                             doc_prod_lidvid))

        self.db.create_fits_file(self.dummy_os_filepath,
                                 fits_filename,
                                 fits_prod_lidvid,
                                 666)

        self.assertTrue(self.db.file_exists(bad_fits_filename,
                                            bad_fits_prod_lidvid))
        self.assertTrue(self.db.file_exists(fits_filename,
                                            fits_prod_lidvid))
        self.assertFalse(self.db.file_exists(browse_filename,
                                             browse_prod_lidvid))
        self.assertFalse(self.db.file_exists(doc_filename,
                                             doc_prod_lidvid))
        self.assertFalse(self.db.file_exists(doc_filename_2,
                                             doc_prod_lidvid))

        self.db.create_browse_file(self.dummy_os_filepath,
                                   browse_filename,
                                   browse_prod_lidvid,
                                   666)

        self.assertTrue(self.db.file_exists(bad_fits_filename,
                                            bad_fits_prod_lidvid))
        self.assertTrue(self.db.file_exists(fits_filename,
                                            fits_prod_lidvid))
        self.assertTrue(self.db.file_exists(browse_filename,
                                            browse_prod_lidvid))
        self.assertFalse(self.db.file_exists(doc_filename,
                                             doc_prod_lidvid))
        self.assertFalse(self.db.file_exists(doc_filename_2,
                                             doc_prod_lidvid))

        self.db.create_document_file(self.dummy_os_filepath,
                                     doc_filename,
                                     doc_prod_lidvid)

        self.assertTrue(self.db.file_exists(bad_fits_filename,
                                            bad_fits_prod_lidvid))
        self.assertTrue(self.db.file_exists(fits_filename,
                                            fits_prod_lidvid))
        self.assertTrue(self.db.file_exists(browse_filename,
                                            browse_prod_lidvid))
        self.assertTrue(self.db.file_exists(doc_filename,
                                            doc_prod_lidvid))
        self.assertFalse(self.db.file_exists(doc_filename_2,
                                             doc_prod_lidvid))

        self.db.create_document_file(self.dummy_os_filepath,
                                     doc_filename_2,
                                     doc_prod_lidvid)

        self.assertTrue(self.db.file_exists(bad_fits_filename,
                                            bad_fits_prod_lidvid))
        self.assertTrue(self.db.file_exists(fits_filename,
                                            fits_prod_lidvid))
        self.assertTrue(self.db.file_exists(browse_filename,
                                            browse_prod_lidvid))
        self.assertTrue(self.db.file_exists(doc_filename,
                                            doc_prod_lidvid))
        self.assertTrue(self.db.file_exists(doc_filename_2,
                                            doc_prod_lidvid))

    def test_bad_fits_file_exists(self):
        # type: () -> None
        bundle_lidvid = 'urn:nasa:pds:hst_99999::1.1'
        self.db.create_bundle(bundle_lidvid)

        collection_lidvid = 'urn:nasa:pds:hst_99999:data_acs_raw::1.8'
        self.db.create_non_document_collection(collection_lidvid,
                                               bundle_lidvid)

        product_lidvid = 'urn:nasa:pds:hst_99999:data_acs_raw:p::8.1'
        self.db.create_fits_product(product_lidvid, collection_lidvid)

        filename = 'p_raw.fits'
        self.assertFalse(self.db.bad_fits_file_exists(filename,
                                                      product_lidvid))

        self.db.create_bad_fits_file(self.dummy_os_filepath,
                                     filename, product_lidvid, "kablooey!")
        self.assertTrue(self.db.bad_fits_file_exists(filename,
                                                     product_lidvid))

    def test_browse_file_exists(self):
        # type: () -> None
        bundle_lidvid = 'urn:nasa:pds:hst_99999::1.1'
        self.db.create_bundle(bundle_lidvid)
        raw_collection_lidvid = 'urn:nasa:pds:hst_99999:data_acs_raw::1.8'
        collection_lidvid = 'urn:nasa:pds:hst_99999:browse_acs_raw::1.8'
        self.db.create_non_document_collection(raw_collection_lidvid,
                                               bundle_lidvid)
        self.db.create_non_document_collection(collection_lidvid,
                                               bundle_lidvid)
        fits_product_lidvid = 'urn:nasa:pds:hst_99999:data_acs_raw:p::1.8'
        product_lidvid = 'urn:nasa:pds:hst_99999:browse_acs_raw:p::1.8'
        self.db.create_fits_product(fits_product_lidvid,
                                    raw_collection_lidvid)
        self.db.create_browse_product(product_lidvid,
                                      fits_product_lidvid,
                                      collection_lidvid)
        basename = 'p.jpg'
        self.assertFalse(self.db.browse_file_exists(basename,
                                                    product_lidvid))
        self.db.create_browse_file(self.dummy_os_filepath,
                                   basename, product_lidvid, 1024)
        self.assertTrue(self.db.browse_file_exists(basename,
                                                   product_lidvid))

    def test_document_file_exists(self):
        # type: () -> None
        bundle_lidvid = 'urn:nasa:pds:hst_99999::1.1'
        self.db.create_bundle(bundle_lidvid)

        collection_lidvid = 'urn:nasa:pds:hst_99999:document::1.8'
        self.db.create_document_collection(collection_lidvid,
                                           bundle_lidvid)

        product_lidvid = 'urn:nasa:pds:hst_99999:document:p::8.1'
        self.db.create_document_product(product_lidvid, collection_lidvid)

        filename = 'stuff.pdf'
        self.assertFalse(self.db.document_file_exists(filename,
                                                      product_lidvid))

        self.db.create_document_file(self.dummy_os_filepath,
                                     filename, product_lidvid)
        self.assertTrue(self.db.document_file_exists(filename,
                                                     product_lidvid))

    def test_fits_file_exists(self):
        # type: () -> None
        bundle_lidvid = 'urn:nasa:pds:hst_99999::1.1'
        self.db.create_bundle(bundle_lidvid)

        collection_lidvid = 'urn:nasa:pds:hst_99999:data_acs_raw::1.8'
        self.db.create_non_document_collection(collection_lidvid,
                                               bundle_lidvid)

        product_lidvid = 'urn:nasa:pds:hst_99999:data_acs_raw:p::8.1'
        self.db.create_fits_product(product_lidvid, collection_lidvid)

        filename = 'p_raw.fits'
        self.assertFalse(self.db.fits_file_exists(filename,
                                                  product_lidvid))

        self.db.create_fits_file(self.dummy_os_filepath,
                                 filename, product_lidvid, 1)
        self.assertTrue(self.db.fits_file_exists(filename,
                                                 product_lidvid))

    def test_get_file(self):
        # type: () -> None
        bundle_lidvid = 'urn:nasa:pds:hst_99999::1.1'
        self.db.create_bundle(bundle_lidvid)

        collection_lidvid = 'urn:nasa:pds:hst_99999:data_acs_raw::1.8'
        self.db.create_non_document_collection(collection_lidvid,
                                               bundle_lidvid)

        product_lidvid = 'urn:nasa:pds:hst_99999:data_acs_raw:p::8.1'
        self.db.create_fits_product(product_lidvid, collection_lidvid)

        filename = 'p_raw.fits'
        with self.assertRaises(Exception):
            self.db.get_file(filename,
                             product_lidvid)

        self.db.create_fits_file(self.dummy_os_filepath,
                                 filename, product_lidvid, 1)
        self.assertTrue(self.db.get_file(filename,
                                         product_lidvid))

    ############################################################

    def test_create_bundle_label(self):
        # type: () -> None
        bundle_lidvid = 'urn:nasa:pds:hst_99999::1.1'
        self.db.create_bundle(bundle_lidvid)

        self.assertFalse(self.db.bundle_label_exists(bundle_lidvid))
        basename = 'bundle.xml'
        self.db.create_bundle_label(self.dummy_os_filepath,
                                    basename, bundle_lidvid)
        self.assertTrue(self.db.bundle_label_exists(bundle_lidvid))
        self.db.create_bundle_label(self.dummy_os_filepath,
                                    basename, bundle_lidvid)
        self.assertTrue(self.db.bundle_label_exists(bundle_lidvid))

    def test_bundle_label_exists(self):
        # type: () -> None
        bundle_lidvid = 'urn:nasa:pds:hst_99999::1.1'
        self.db.create_bundle(bundle_lidvid)

        self.assertFalse(self.db.bundle_label_exists(bundle_lidvid))
        basename = 'bundle.xml'
        self.db.create_bundle_label(self.dummy_os_filepath,
                                    basename, bundle_lidvid)
        self.assertTrue(self.db.bundle_label_exists(bundle_lidvid))

    def test_get_bundle_label(self):
        # type: () -> None
        bundle_lidvid = 'urn:nasa:pds:hst_99999::1.1'
        self.db.create_bundle(bundle_lidvid)

        basename = 'bundle.xml'
        self.db.create_bundle_label(self.dummy_os_filepath,
                                    basename, bundle_lidvid)
        bundle_label = self.db.get_bundle_label(bundle_lidvid)
        self.assertEquals(bundle_lidvid, bundle_label.bundle_lidvid)
        self.assertEquals(basename, bundle_label.basename)
        self.assertEquals(file_md5(self.dummy_os_filepath),
                          bundle_label.md5_hash)

    def test_create_collection_label(self):
        # type: () -> None
        bundle_lidvid = 'urn:nasa:pds:hst_99999::1.1'
        self.db.create_bundle(bundle_lidvid)
        collection_lidvid = 'urn:nasa:pds:hst_99999:data_acs_raw::1.1'
        self.db.create_non_document_collection(collection_lidvid,
                                               bundle_lidvid)

        self.assertFalse(self.db.collection_label_exists(collection_lidvid))
        basename = 'collection.xml'
        self.db.create_collection_label(self.dummy_os_filepath,
                                        basename, collection_lidvid)
        self.assertTrue(self.db.collection_label_exists(collection_lidvid))
        self.db.create_collection_label(self.dummy_os_filepath,
                                        basename, collection_lidvid)
        self.assertTrue(self.db.collection_label_exists(collection_lidvid))

    def test_collection_label_exists(self):
        # type: () -> None
        bundle_lidvid = 'urn:nasa:pds:hst_99999::1.1'
        self.db.create_bundle(bundle_lidvid)
        collection_lidvid = 'urn:nasa:pds:hst_99999:data_acs_raw::1.1'
        self.db.create_non_document_collection(collection_lidvid,
                                               bundle_lidvid)

        self.assertFalse(self.db.collection_label_exists(collection_lidvid))
        basename = 'collection.xml'
        self.db.create_collection_label(self.dummy_os_filepath,
                                        basename, collection_lidvid)
        self.assertTrue(self.db.collection_label_exists(collection_lidvid))

    def test_get_collection_label(self):
        # type: () -> None
        bundle_lidvid = 'urn:nasa:pds:hst_99999::1.1'
        self.db.create_bundle(bundle_lidvid)
        collection_lidvid = 'urn:nasa:pds:hst_99999:data_acs_raw::1.1'
        self.db.create_non_document_collection(collection_lidvid,
                                               bundle_lidvid)

        basename = get_collection_label_name(self.db,
                                             collection_lidvid)
        self.db.create_collection_label(self.dummy_os_filepath,
                                        basename, collection_lidvid)
        collection_label = self.db.get_collection_label(
            collection_lidvid)
        self.assertEquals(collection_lidvid,
                          collection_label.collection_lidvid)
        self.assertEquals(basename, collection_label.basename)
        self.assertEquals(file_md5(self.dummy_os_filepath),
                          collection_label.md5_hash)

    def test_create_collection_inventory(self):
        # type: () -> None
        bundle_lidvid = 'urn:nasa:pds:hst_99999::1.1'
        self.db.create_bundle(bundle_lidvid)
        collection_lidvid = 'urn:nasa:pds:hst_99999:data_acs_raw::1.1'
        self.db.create_non_document_collection(collection_lidvid,
                                               bundle_lidvid)

        self.assertFalse(
            self.db.collection_inventory_exists(collection_lidvid))
        basename = 'collection.xml'
        self.db.create_collection_inventory(self.dummy_os_filepath,
                                            basename, collection_lidvid)
        self.assertTrue(self.db.collection_inventory_exists(collection_lidvid))
        self.db.create_collection_inventory(self.dummy_os_filepath,
                                            basename, collection_lidvid)
        self.assertTrue(self.db.collection_inventory_exists(collection_lidvid))

    def test_collection_inventory_exists(self):
        # type: () -> None
        bundle_lidvid = 'urn:nasa:pds:hst_99999::1.1'
        self.db.create_bundle(bundle_lidvid)
        collection_lidvid = 'urn:nasa:pds:hst_99999:data_acs_raw::1.1'
        self.db.create_non_document_collection(collection_lidvid,
                                               bundle_lidvid)

        self.assertFalse(
            self.db.collection_inventory_exists(collection_lidvid))
        basename = 'collection.xml'
        self.db.create_collection_inventory(self.dummy_os_filepath,
                                            basename, collection_lidvid)
        self.assertTrue(self.db.collection_inventory_exists(collection_lidvid))

    def test_get_collection_inventory(self):
        # type: () -> None
        bundle_lidvid = 'urn:nasa:pds:hst_99999::1.1'
        self.db.create_bundle(bundle_lidvid)
        collection_lidvid = 'urn:nasa:pds:hst_99999:data_acs_raw::1.1'
        self.db.create_non_document_collection(collection_lidvid,
                                               bundle_lidvid)

        basename = get_collection_inventory_name(self.db,
                                                 collection_lidvid)
        self.db.create_collection_inventory(self.dummy_os_filepath,
                                            basename, collection_lidvid)
        collection_inventory = self.db.get_collection_inventory(
            collection_lidvid)
        self.assertEquals(collection_lidvid,
                          collection_inventory.collection_lidvid)
        self.assertEquals(basename, collection_inventory.basename)
        self.assertEquals(file_md5(self.dummy_os_filepath),
                          collection_inventory.md5_hash)

    def test_create_product_label(self):
        # type: () -> None
        bundle_lidvid = 'urn:nasa:pds:hst_99999::1.1'
        self.db.create_bundle(bundle_lidvid)
        collection_lidvid = 'urn:nasa:pds:hst_99999:data_acs_raw::1.1'
        self.db.create_non_document_collection(collection_lidvid,
                                               bundle_lidvid)
        product_lidvid = 'urn:nasa:pds:hst_99999:data_acs_raw:j6gp01lzq::1.8'
        self.db.create_fits_product(product_lidvid, collection_lidvid)

        self.assertFalse(self.db.product_label_exists(product_lidvid))
        basename = '%s.xml' % LIDVID(product_lidvid).lid().product_id
        self.db.create_product_label(self.dummy_os_filepath,
                                     basename, product_lidvid)
        self.assertTrue(self.db.product_label_exists(product_lidvid))
        self.db.create_product_label(self.dummy_os_filepath,
                                     basename, product_lidvid)
        self.assertTrue(self.db.product_label_exists(product_lidvid))

    def test_product_label_exists(self):
        # type: () -> None
        bundle_lidvid = 'urn:nasa:pds:hst_99999::1.1'
        self.db.create_bundle(bundle_lidvid)
        collection_lidvid = 'urn:nasa:pds:hst_99999:data_acs_raw::1.1'
        self.db.create_non_document_collection(collection_lidvid,
                                               bundle_lidvid)
        product_lidvid = 'urn:nasa:pds:hst_99999:data_acs_raw:j6gp01lzq::1.8'
        self.db.create_fits_product(product_lidvid, collection_lidvid)

        self.assertFalse(self.db.product_label_exists(product_lidvid))
        basename = '%s.xml' % LIDVID(product_lidvid).lid().product_id
        self.db.create_product_label(self.dummy_os_filepath,
                                     basename, product_lidvid)
        self.assertTrue(self.db.product_label_exists(product_lidvid))

    def test_get_product_label(self):
        # type: () -> None
        bundle_lidvid = 'urn:nasa:pds:hst_99999::1.1'
        self.db.create_bundle(bundle_lidvid)
        collection_lidvid = 'urn:nasa:pds:hst_99999:data_acs_raw::1.1'
        self.db.create_non_document_collection(collection_lidvid,
                                               bundle_lidvid)
        product_lidvid = 'urn:nasa:pds:hst_99999:data_acs_raw:j6gp01lzq::1.8'
        self.db.create_fits_product(product_lidvid, collection_lidvid)

        basename = 'j6gp01lzq_raw.fits'
        self.db.create_product_label(self.dummy_os_filepath,
                                     basename, product_lidvid)
        product_label = self.db.get_product_label(product_lidvid)
        self.assertEquals(product_lidvid,
                          product_label.product_lidvid)
        self.assertEquals(basename, product_label.basename)
        self.assertEquals(file_md5(self.dummy_os_filepath),
                          product_label.md5_hash)

    ############################################################

    def test_get_card_dictionaries(self):
        # type: () -> None

        # We don't test the functionality of get_card_dictionaries()
        # here, since we'd first need to populate the database with
        # the contents of the FITS file and that machinery is in
        # FitsFileDB.  So the real testing happens there.  I leave
        # this empty test as the equivalent of a "this page left
        # intentionally blank" message.
        pass

    def test_exploratory(self):
        # type: () -> None
        # what happens if you create tables twice?
        self.db.create_tables()
        # no exception, at least

    ############################################################

    def test_get_proposal_info(self):
        # type: () -> None
        bundle_lid = 'urn:nasa:pds:hst_99999'
        self.assertFalse(self.db.proposal_info_exists(bundle_lid))
        with self.assertRaises(Exception):
            self.db.get_proposal_info(bundle_lid)

        self.db.create_proposal_info(bundle_lid,
                                     proposal_title='Proposal of marriage',
                                     pi_name='Romeo Montague',
                                     author_list='R. Montague, B. Montague',
                                     proposal_year='1476',
                                     publication_year='1597')
        self.assertTrue(self.db.proposal_info_exists(bundle_lid))

        not_a_bundle_lid = 'urn:nasa:pds:space_1999'
        self.assertFalse(self.db.proposal_info_exists(not_a_bundle_lid))

        proposal_info = self.db.get_proposal_info(bundle_lid)
        self.assertEqual('Proposal of marriage',
                         proposal_info.proposal_title)