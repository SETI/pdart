"""
**SCRIPT:** Build the bundle databases then build bundle, collection,
and product labels, and collection inventories.  Uses the bundle
databases.
"""
from contextlib import closing
import os.path
import sqlite3

from pdart.db.CreateBundleDatabase import BundleDatabaseCreator
from pdart.db.DatabaseName import DATABASE_NAME
from pdart.pds4.Archive import Archive
from pdart.pds4.Archives import *
from pdart.pds4.Collection import Collection
from pdart.pds4.LID import LID
from pdart.pds4labels.BrowseProductImageDB import *
from pdart.pds4labels.BrowseProductLabelDB import *
from pdart.pds4labels.BundleLabel import *
from pdart.pds4labels.CollectionLabel import *
from pdart.pds4labels.DBCalls import *
from pdart.pds4labels.ProductLabel import *
from pdart.pds4labels.RawSuffixes import RAW_SUFFIXES
from pdart.rules.Combinators import *

from typing import cast, Iterable, TYPE_CHECKING

VERIFY = False
# type: bool
IN_MEMORY = False
# type: bool
CREATE_DB = False
# type: bool


def check_browse_collection(needed, archive, conn, collection_lid):
    # type: (bool, Archive, sqlite3.Connection, unicode) -> None
    lid = LID(collection_lid)
    coll = Collection(archive, lid)
    browse_coll = coll.browse_collection()
    browse_coll_exists = os.path.isdir(browse_coll.absolute_filepath())
    if needed:
        assert browse_coll_exists, \
            '%s was needed but not created' % browse_coll
        # further checks

        # TODO Check that an image product and its label was created for
        # each product with a good FITS file.

        if False:
            # Add tests once we're creating these.  (It's test-first
            # development!)
            inv_fp = browse_coll.inventory_filepath()
            assert os.path.isfile(inv_fp), 'no browse inventory at %s' % inv_fp
            label_fp = browse_coll.label_filepath()
            assert os.path.isfile(label_fp), 'no browse label at %s' % label_fp
        # TODO Any more tests?
    else:
        assert not browse_coll_exists, "%s exists but shouldn't" % browse_coll


def needs_browse_collection(collection_lid):
    # type: (unicode) -> bool
    lid = LID(collection_lid)
    prefix = re.match(Collection.DIRECTORY_PATTERN,
                      lid.collection_id).group(1)
    suffix = re.match(Collection.DIRECTORY_PATTERN,
                      lid.collection_id).group(3)
    return prefix == 'data' and suffix in RAW_SUFFIXES


def make_db_browse_collection_and_label(archive, conn, collection_lid):
    # type: (Archive, sqlite3.Connection, unicode) -> None
    needed = needs_browse_collection(collection_lid)
    if needed:
        # create the products
        make_db_collection_browse_product_images(conn, collection_lid)
        make_db_collection_browse_product_labels(archive, conn, collection_lid)
        # TODO create the label and inventory
        print ('#### TODO: Would build browse collection label ' +
               'and inventory for %s' % collection_lid)
    check_browse_collection(needed, archive, conn, collection_lid)


def make_db_documentation_collection_and_label(conn, collection_lid):
    # type: (sqlite3.Connection, unicode) -> None
    print ('**** TODO: Would build documentation collection for %s'
           % collection_lid)


class ArchiveRecursion(object):
    def __init__(self):
        # type: () -> None
        pass

    def run(self, archive):
        """Implements a bottom-up recursion through the archive."""
        # type: (Archive) -> None
        for bundle in archive.bundles():
            database_fp = os.path.join(bundle.absolute_filepath(),
                                       DATABASE_NAME)
            with closing(sqlite3.connect(database_fp)) as conn:
                with closing(conn.cursor()) as collection_cursor:
                    for (coll,) in get_bundle_collections_db(collection_cursor,
                                                             bundle.lid.lid):
                        with closing(conn.cursor()) as product_cursor:
                            prod_iter = get_good_collection_products_db(
                                product_cursor, coll)
                            for (prod,) in prod_iter:
                                self.handle_product(archive, conn, prod)
                        self.handle_collection(archive, conn, coll)
                self.handle_bundle(archive, conn, bundle.lid.lid)

    def handle_bundle(self, archive, conn, bundle_lid):
        # type: (Archive, sqlite3.Connection, unicode) -> None
        pass

    def handle_collection(self, archive, conn, collection_lid):
        # type: (Archive, sqlite3.Connection, unicode) -> None
        pass

    def handle_product(self, archive, conn, product_lid):
        # type: (Archive, sqlite3.Connection, unicode) -> None
        pass


class LabelCreationRecursion(ArchiveRecursion):
    def __init__(self):
        # type: () -> None
        ArchiveRecursion.__init__(self)

    def handle_bundle(self, archive, conn, bundle_lid):
        # type: (Archive, sqlite3.Connection, unicode) -> None
        make_db_bundle_label(conn, bundle_lid, VERIFY)

    def handle_collection(self, archive, conn, collection_lid):
        # type: (Archive, sqlite3.Connection, unicode) -> None
        make_db_collection_label_and_inventory(conn, collection_lid, VERIFY)

    def handle_product(self, archive, conn, product_lid):
        # type: (Archive, sqlite3.Connection, unicode) -> None
        make_db_product_label(conn, product_lid, VERIFY)


class FullCreationRecursion(LabelCreationRecursion):
    def __init__(self):
        # type: () -> None
        LabelCreationRecursion.__init__(self)

    def handle_collection(self, archive, conn, collection_lid):
        # type: (Archive, sqlite3.Connection, unicode) -> None
        LabelCreationRecursion.handle_collection(self, archive,
                                                 conn, collection_lid)
        make_db_browse_collection_and_label(archive, conn, collection_lid)
        make_db_documentation_collection_and_label(conn, collection_lid)


def dev():
    # type: () -> None
    archive = get_any_archive()

    if CREATE_DB:
        BundleDatabaseCreator(archive).create()

    FullCreationRecursion().run(archive)


if __name__ == '__main__':
    raise_verbosely(dev)
