"""
The module provides instances of
:class:`pdart.reductions.Reduction.Reduction` s that log archive
components as they are processed.  Intended to be used as part of a
:class:`pdart.reductions.CompositeReduction.CompositeReduction`.
"""
import sys

from pdart.reductions.Reduction import *


class LogBundlesReduction(Reduction):
    def reduce_archive(self, archive_root, get_reduced_bundles):
        get_reduced_bundles()

    def reduce_bundle(self, archive, lid, get_reduced_collections):
        print 'Bundle', str(lid)
        sys.stdout.flush()


class LogCollectionsReduction(Reduction):
    def reduce_archive(self, archive_root, get_reduced_bundles):
        get_reduced_bundles()

    def reduce_bundle(self, archive, lid, get_reduced_collections):
        get_reduced_collections()

    def reduce_collection(self, archive, lid, get_reduced_products):
        print 'Collection', str(lid)
        sys.stdout.flush()


class LogProductsReduction(Reduction):
    def reduce_archive(self, archive_root, get_reduced_bundles):
        get_reduced_bundles()

    def reduce_bundle(self, archive, lid, get_reduced_collections):
        get_reduced_collections()

    def reduce_collection(self, archive, lid, get_reduced_products):
        get_reduced_products()

    def reduce_product(self, archive, lid, get_reduced_products):
        print 'Product', str(lid)
        sys.stdout.flush()