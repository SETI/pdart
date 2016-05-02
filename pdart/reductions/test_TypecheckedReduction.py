from pdart.exceptions.ExceptionInfo import *
from pdart.reductions.CompositeReduction import *
from pdart.reductions.TypecheckedReduction import *

if False:
    def testSanity():
        class NoneTypechecks(object):
            def check_is_archive_reduction(self, obj):
                assert obj is None

            def check_is_bundle_reduction(self, obj):
                assert obj is None

            def check_is_collection_reduction(self, obj):
                assert obj is None

            def check_is_product_reduction(self, obj):
                assert obj is None

            def check_is_fits_file_reduction(self, obj):
                assert obj is None

            def check_is_hdu_reduction(self, obj):
                assert obj is None

            def check_is_header_unit_reduction(self, obj):
                assert obj is None

            def check_is_data_unit_reduction(self, obj):
                assert obj is None

        class DeepReduction(Reduction):
            def reduce_archive(self, archive_root, get_reduced_bundles):
                get_reduced_bundles()
                return None

            def reduce_bundle(self, archive, lid, get_reduced_collections):
                get_reduced_collections()
                return None

            def reduce_collection(self, archive, lid, get_reduced_products):
                get_reduced_products()
                return None

            def reduce_product(self, archive, lid, get_reduced_fits_files):
                get_reduced_fits_files()
                return None

            def reduce_fits_file(self, file, get_reduced_hdus):
                get_reduced_hdus()
                return None

            def reduce_hdu(self, n, hdu,
                           get_reduced_header_unit,
                           get_reduced_data_unit):
                get_reduced_header_unit()
                get_reduced_data_unit()
                return None

            def reduce_header_unit(self, n, header_unit):
                return None

            def reduce_data_unit(self, n, data_unit):
                return None

        tc = NoneTypechecks()
        red = TypecheckedReduction(tc, DeepReduction())
        runner = TypecheckedReductionRunner(tc, DefaultReductionRunner())
        from pdart.pds4.Archives import get_any_archive
        arch = get_any_archive()

        try:
            runner.run_archive(red, arch)
        except CalculationException as ce:
            print ce.exception_info.to_pretty_xml()
            raise


class ComponentTypechecks(Typechecks):
    """
    Checks that a Reduction reduces an xxx to the string
    'xxx_reduction_n' where the n is an integer.
    """
    def __init__(self, index):
        assert isinstance(index, int)
        self.index = index

    def check_is_archive_reduction(self, obj):
        assert obj == ('archive_reduction_%d' % self.index)

    def check_is_bundle_reduction(self, obj):
        assert obj == ('bundle_reduction_%d' % self.index)

    def check_is_collection_reduction(self, obj):
        assert obj == ('collection_reduction_%d' % self.index)

    def check_is_product_reduction(self, obj):
        assert obj == ('product_reduction_%d' % self.index)

    def check_is_fits_file_reduction(self, obj):
        assert obj == ('fits_file_reduction_%d' % self.index)

    def check_is_hdu_reduction(self, obj):
        assert obj == ('hdu_reduction_%d' % self.index)

    def check_is_header_unit_reduction(self, obj):
        assert obj == ('header_unit_reduction_%d' % self.index)

    def check_is_data_unit_reduction(self, obj):
        assert obj == ('data_unit_reduction_%d' % self.index)


class IndexedReduction(Reduction):
    def __init__(self, index):
        assert isinstance(index, int)
        self.index = index

    def reduce_archive(self, archive_root, get_reduced_bundles):
        get_reduced_bundles()
        return ('archive_reduction_%d' % self.index)

    def reduce_bundle(self, archive, lid, get_reduced_collections):
        get_reduced_collections()
        return ('bundle_reduction_%d' % self.index)

    def reduce_collection(self, archive, lid, get_reduced_products):
        get_reduced_products()
        return ('collection_reduction_%d' % self.index)

    def reduce_product(self, archive, lid, get_reduced_fits_files):
        get_reduced_fits_files()
        return ('product_reduction_%d' % self.index)

    def reduce_fits_file(self, file, get_reduced_hdus):
        get_reduced_hdus()
        return ('fits_file_reduction_%d' % self.index)

    def reduce_hdu(self, n, hdu,
                   get_reduced_header_unit,
                   get_reduced_data_unit):
        get_reduced_header_unit()
        get_reduced_data_unit()
        return ('hdu_reduction_%d' % self.index)

    def reduce_header_unit(self, n, header_unit):
        return ('header_unit_reduction_%d' % self.index)

    def reduce_data_unit(self, n, data_unit):
        return ('data_unit_reduction_%d' % self.index)

if False:
    def test_sanity():
        tc = ComponentTypechecks(1)
        red = TypecheckedReduction(tc, IndexedReduction(1))
        runner = TypecheckedReductionRunner(tc, DefaultReductionRunner())
        from pdart.pds4.Archives import get_any_archive
        arch = get_any_archive()

        try:
            runner.run_archive(red, arch)
        except CalculationException as ce:
            print ce.exception_info.to_pretty_xml()
            raise

if False:
    def test_composite():
        tc1 = ComponentTypechecks(1)
        tc2 = ComponentTypechecks(2)
        tc12 = CompositeTypechecks([tc1, tc2])

        tr1 = IndexedReduction(1)
        tr2 = IndexedReduction(2)
        tr12 = CompositeReduction([tr1, tr2])

        red = TypecheckedReduction(tc12, tr12)
        runner = TypecheckedReductionRunner(tc12, DefaultReductionRunner())
        from pdart.pds4.Archives import get_any_archive
        arch = get_any_archive()

        try:
            runner.run_archive(red, arch)
        except CalculationException as ce:
            print ce.exception_info.to_pretty_xml()
            raise