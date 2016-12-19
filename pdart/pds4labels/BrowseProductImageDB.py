"""
Functionality to build a RAW browse product image using a SQLite
database.
"""
from contextlib import closing
import os.path

from pdart.pds4.LID import *
from pdart.pds4labels.BrowseProductImageReduction import ensure_directory
from pdart.pds4labels.RawSuffixes import RAW_SUFFIXES

import pdart.add_pds_tools
import picmaker

from typing import cast, Iterable, Tuple, TYPE_CHECKING
if TYPE_CHECKING:
    from pdart.pds4.Archive import Archive
    import sqlite3


def _make_browse_coll_fp(raw_coll_fp):
    # type: (str) -> str
    """
u    Given the filepath to the RAW collection, return the filepath to
    its browse collection.
    """
    # TODO Sloppy implementation: assumes only one 'data'
    res = 'browse'.join(re.split('data', raw_coll_fp))
    ensure_directory(res)
    return res


def _make_browse_image(browse_coll_fp, raw_full_filepath, visit):
    # type: (str, str, unicode) -> None
    """
    Given a filepath for the destination browse collection, a filepath
    for the source RAW file, and the product's visit code, create the
    browse image and save it.
    """
    basename = os.path.basename(raw_full_filepath)
    basename = os.path.splitext(basename)[0] + '.jpg'
    target_dir = os.path.join(browse_coll_fp, ('visit_%s' % visit))

    ensure_directory(target_dir)

    # TODO: WFPC2 gives four images, not one, so we'll have to do
    # something different here.  This probably just builds the first
    # image.
    picmaker.ImagesToPics([raw_full_filepath],
                          target_dir,
                          filter="None",
                          percentiles=(1, 99))


def make_db_browse_product_images(conn, archive):
    # type: (sqlite3.Connection, Archive) -> None
    """
    Given a database connection and an :class:`~pdart.pds4.Archive`,
    create browse images for all the RAW products.
    """

    # TODO Polish (with SQL joins?).  First, an inefficient
    # implementation.
    with closing(conn.cursor()) as cursor:
        colls = [ccbs for suff in RAW_SUFFIXES
                 for ccbs in list(cast(
                    Iterable[Tuple[unicode, str, unicode, unicode]],
                    cursor.execute(
                        """SELECT collection, full_filepath, bundle, suffix
                       FROM collections
                       WHERE prefix='data' AND suffix=?""", (suff,))))]

        for (c, c_fp, b, suffix) in colls:
            cursor.execute('SELECT proposal_id FROM bundles WHERE bundle=?',
                           (b,))
            (proposal_id,) = cursor.fetchone()
            for (p, fp, v) in cast(Iterable[Tuple[unicode, str, unicode]],
                                   cursor.execute(
                    """SELECT product, full_filepath, visit
                        FROM products
                        WHERE collection=?
                        AND product NOT IN
                            (SELECT product FROM bad_fits_files)""",
                    (c,))):
                print p
                browse_coll_fp = _make_browse_coll_fp(c_fp)
                _make_browse_image(browse_coll_fp, fp, v)
