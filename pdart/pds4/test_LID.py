import unittest

from pdart.pds4.LID import *


class TestLID(unittest.TestCase):
    def test_init(self):
        # sanity-check
        with self.assertRaises(Exception):
            LID(None)

        # test segments
        with self.assertRaises(Exception):
            LID('urn:nasa')
        with self.assertRaises(Exception):
            LID('urn:nasa:pds')
        LID('urn:nasa:pds:bundle')
        LID('urn:nasa:pds:bundle:container')
        LID('urn:nasa:pds:bundle:container:product')
        with self.assertRaises(Exception):
            LID('urn:nasa:pds:bundle:container:product:ingredient')

        # test prefix
        with self.assertRaises(Exception):
            LID('urn:nasa:pdddddds:bundle')

        # test length
        LID('urn:nasa:pds:%s' % ('a'*200))
        with self.assertRaises(Exception):
            LID('urn:nasa:pds:%s' % ('a'*250))

        # test characters
        with self.assertRaises(Exception):
            LID('urn:nasa:pds:foo&bar')
        with self.assertRaises(Exception):
            LID('urn:nasa:pds:fooBAR')
        with self.assertRaises(Exception):
            LID('urn:nasa:pds::foobar')

        # test fields
        lid = LID('urn:nasa:pds:bundle')
        self.assertEquals('bundle', lid.bundle_id)
        self.assertIsNone(lid.collection_id)
        self.assertIsNone(lid.product_id)
        self.assertEquals('urn:nasa:pds:bundle', lid.lid)

        lid = LID('urn:nasa:pds:bundle:collection')
        self.assertEquals('bundle', lid.bundle_id)
        self.assertEquals('collection', lid.collection_id)
        self.assertIsNone(lid.product_id)
        self.assertEquals('urn:nasa:pds:bundle:collection', lid.lid)

        lid = LID('urn:nasa:pds:bundle:collection:product')
        self.assertEquals('bundle', lid.bundle_id)
        self.assertEquals('collection', lid.collection_id)
        self.assertEquals('product', lid.product_id)
        self.assertEquals('urn:nasa:pds:bundle:collection:product', lid.lid)

    def test_eq(self):
        self.assertTrue(LID('urn:nasa:pds:bundle:collection:product') ==
                        LID('urn:nasa:pds:bundle:collection:product'))
        self.assertFalse(LID('urn:nasa:pds:bundle:collection:product') !=
                         LID('urn:nasa:pds:bundle:collection:product'))
        self.assertFalse(LID('urn:nasa:pds:bundle:collection:product') ==
                         LID('urn:nasa:pds:bundle:collection:produit'))
        self.assertTrue(LID('urn:nasa:pds:bundle:collection:product') !=
                        LID('urn:nasa:pds:bundle:collection:produit'))

    def test_str(self):
        self.assertEquals('urn:nasa:pds:bundle:collection:product',
                          str(LID('urn:nasa:pds:bundle:collection:product')))

    def test_repr(self):
        self.assertEquals("LID('urn:nasa:pds:bundle:collection:product')",
                          repr(LID('urn:nasa:pds:bundle:collection:product')))

    # TODO Write tests for is_bundle_id, etc.