import os.path
import pprint
import sys

import FileArchives
import FitsProductFileXmlMakerD
import InstrumentXmlMakerD
import pdart.pds4.LID
import LabelMaker
import pdart.pds4.Product
import ProductDistillationProductPass
import ProductInfo
import ProductLabelProductPass
import ProductPass
import TargetIdentificationXmlMaker
import pdart.xml.Schema


class ProductLabelMakerD(LabelMaker.LabelMaker):
    def __init__(self, product):
        pp = ProductDistillationProductPass.ProductDistillationProductPass()
        ppr = ProductPass.ProductPassRunner()
        res = ppr.run_product(pp, product)
        assert res.is_success(), 'Distillation failed for %s' % self.component
        self.distillation = res.value
        assert self.distillation
        super(ProductLabelMakerD,
              self).__init__(product, ProductInfo.ProductInfo(product))

    def default_xml_name(self):
        assert False, 'ProductLabelMakerD.default_xml_name unimplemented'

    def create_xml(self):
        assert self.distillation

        product = self.component

        # At XPath '/'
        self.add_processing_instruction('xml-model',
                                        self.info.xml_model_pds_attributes())

        # At XPath '/Product_Observational'
        root = self.create_child(self.document, 'Product_Observational')

        PDS = self.info.pds_namespace_url()
        root.setAttribute('xmlns', PDS)
        root.setAttribute('xmlns:pds', PDS)
        root.setAttribute('xmlns:xsi', self.info.xsi_namespace_url())
        root.setAttribute('xsi:schemaLocation', self.info.pds4_schema_url())

        identification_area, observation_area = \
            self.create_children(root, ['Identification_Area',
                                        'Observation_Area'])

        # At XPath '/Product_Observational/Identification_Area'
        logical_identifier, version_id, title, \
            information_model_version, product_class, \
            modification_history = \
            self.create_children(identification_area, [
                'logical_identifier',
                'version_id',
                'title',
                'information_model_version',
                'product_class',
                'Modification_History'])

        self.set_text(logical_identifier, str(product.lid))
        self.set_text(version_id, self.info.version_id())
        self.set_text(title, self.info.title())
        self.set_text(information_model_version,
                      self.info.information_model_version())
        self.set_text(product_class, 'Product_Observational')

        modification_detail = self.create_child(modification_history,
                                                'Modification_Detail')
        modification_date, version_id, description = \
            self.create_children(modification_detail, ['modification_date',
                                                       'version_id',
                                                       'description'])
        self.set_text(modification_date, self.info.modification_date())
        self.set_text(version_id, self.info.version_id())
        self.set_text(description,
                      self.info.modification_history_description())

        # At XPath '/Product_Observational/Observation_Area'
        time_coordinates, investigation_area = \
            self.create_children(observation_area, ['Time_Coordinates',
                                                    'Investigation_Area'])

        # At XPath '/Product_Observational/Observation_Area/Time_Coordinates'
        start_date_time, stop_date_time = \
            self.create_children(time_coordinates, ['start_date_time',
                                                    'stop_date_time'])
        self.set_text(start_date_time, self.info.start_date_time())
        self.set_text(stop_date_time, self.info.stop_date_time())

        # At XPath '/Product_Observational/Observation_Area/Investigation_Area'
        name, type, internal_reference = \
            self.create_children(investigation_area, ['name', 'type',
                                                      'Internal_Reference'])
        self.set_text(name, self.info.investigation_area_name())
        self.set_text(type, self.info.investigation_area_type())

        # At XPath
        # '/Product_Observational/Observation_Area/Investigation_Area/Internal_Reference'
        lidvid_reference, reference_type = \
            self.create_children(internal_reference, ['lidvid_reference',
                                                      'reference_type'])
        self.set_text(lidvid_reference,
                      self.info.investigation_lidvid_reference())
        self.set_text(reference_type, self.info.internal_reference_type())

        # At XPath '/Product_Observational/Observation_Area'
        instrument = self.component.collection().instrument()
        instrument_maker = \
            InstrumentXmlMakerD.InstrumentXmlMakerD(self.document, instrument)
        instrument_maker.create_xml(observation_area)

        # At XPath '/Product_Observational/File_Area_Observational'
        file_area_observational = self.create_child(root,
                                                    'File_Area_Observational')

        # At XPath '/Product_Observational/File_Area_Observational/File'
        file = self.create_child(file_area_observational, 'File')
        file_name = self.create_child(file, 'file_name')
        self.set_text(file_name, os.path.basename(product.absolute_filepath()))

        xml_maker = FitsProductFileXmlMakerD.FitsProductFileXmlMakerD(
            self.document,
            self.distillation['File_Area_Observational']
            )
        xml_maker.create_xml(file_area_observational)

        # TODO Fix this
        target = self.distillation['target'] or 'xxxxx'
        t = TargetIdentificationXmlMaker.TargetIdentificationXmlMaker(
            self.document, target)
        t.create_xml(observation_area)


def test_synthesis():
    a = FileArchives.get_any_archive()
    fp = '/tmp/foo.xml'
    for b in a.bundles():
        for c in b.collections():
            for p in c.products():
                print p
                lm = ProductLabelMakerD(p)
                lm.write_xml_to_file(fp)
                if not (LabelMaker.xml_schema_check(fp) and
                        LabelMaker.schematron_check(fp)):
                    print '%s did not validate; aborting' % p
                    sys.exit(1)


def make_and_test_product_label(lid):
    if isinstance(lid, str):
        lid = pdart.pds4.LID.LID(lid)
    assert isinstance(lid, pdart.pds4.LID.LID)
    a = FileArchives.get_any_archive()
    p = pdart.pds4.Product.Product(a, lid)
    lm = ProductLabelMakerD(p)
    fp = '/tmp/product.xml'
    lm.write_xml_to_file(fp)
    failures = pdart.xml.Schema.xml_schema_failures(fp) or \
        pdart.xml.Schema.schematron_failures(fp)
    if failures:
        print 'Label for %s at %r did not validate.' % (p, fp)
        print failures
        sys.exit(1)


if __name__ == '__main__':
    # test_synthesis()
    # make_and_test_product_label(
    # 'urn:nasa:pds:hst_05167:data_wfpc2_cmh:visit_04')
    make_and_test_product_label(
        'urn:nasa:pds:hst_09746:data_acs_raw:j8rl25pbq_raw')