import pprint
import traceback

import FileArchives
import pdart.pds4.LID
import pdart.pds4.Product
import ProductPass


class TargetProductPass(ProductPass.ProductPass):
    """
    Return the pair ('target_set', ts) where ts is the set of the
    values of the key 'TARGNAME' in the primary HDUs of all files in
    the product.  If it does not contain exactly one element, we have
    missing data (0) or ambiguity (>1).
    """

    def process_hdu_header(self, n, header):
        # Target names are only in the first (index=0) header; ignore
        # the rest.
        if n == 0:
            try:
                res = header['TARGNAME']
            except KeyError:
                res = None
        else:
            res = None
        return res

    def process_hdu_data(self, n, data):
        return None

    def process_hdu(self, n, hdu, h, d):
        return h

    def process_file(self, file, hdus):
        # It's found, if at all, in the first HDU
        return hdus[0]

    def process_product(self, product, targs):
        res = ('target_set',
               set([targ for targ in targs if targ is not None]))
        return res

    def __repr__(self):
        return 'TargetProductPass()'

    def __str__(self):
        return 'TargetProductPass'


BITPIX_TABLE = {
    # TODO Verify these
    8: 'UnsignedByte',
    16: 'SignedMSB2',
    32: 'SignedMSB4',
    64: 'SignedMSB8',
    -32: 'IEEE754MSBSingle',
    -62: 'IEEE754MSBDouble'
    }


AXIS_NAME_TABLE = {
    1: 'Line',
    2: 'Sample'
    # 3: 'Color'?
    }


class FileAreaProductPass(ProductPass.ProductPass):
    """
    When run, return the pair ('File_Area_Observational', dict) where
    dict is a dictionary with file basenames as keys and lists of HDU
    info as values.
    """

    def process_hdu_data(self, n, data):
        return None

    def process_hdu_header(self, n, header):
        res = {}
        res['axes'] = naxis = header['NAXIS']

        res['Axis_Array'] = \
            [{'axis_name': AXIS_NAME_TABLE[i],
              'elements': header['NAXIS%d' % i],
              'sequence_number': i} for i in range(1, naxis + 1)]

        res['data_type'] = BITPIX_TABLE[header['BITPIX']]

        try:
            res['scaling_factor'] = header['BSCALE']
        except KeyError:
            pass

        try:
            res['value_offset'] = header['BZERO']
        except KeyError:
            pass
        return res

    def process_hdu(self, n, hdu, h, d):
        # Grab the result from the hdu_header and augment with info
        # from the hdu's fileinfo()
        res = h
        info = hdu.fileinfo()
        res['header_offset'] = h_off = info['hdrLoc']
        res['data_offset'] = d_off = info['datLoc']
        res['header_size'] = d_off - h_off
        res['local_identifier'] = 'hdu_%d' % n
        return res

    def process_file(self, file, hdus):
        return hdus

    def process_product(self, product, files):
        # Tuple of HDUs' structures
        return ('File_Area_Observational', files[0])

    def __repr__(self):
        return 'FileAreaProductPass()'

    def __str__(self):
        return 'FileAreaProductPass'


class TimeProductPass(ProductPass.ProductPass):
    def process_hdu_data(self, n, data):
        return None

    def process_hdu_header(self, n, data):
        res = ('2000-01-02Z', '2000-01-02Z')
        return res

    def process_hdu(self, n, hdu, h, d):
        return h

    def process_file(self, file, hdus):
        return hdus[0]

    def process_product(self, product, files):
        time_set = set([file for file in files if file is not None])
        return ('Time', time_set)

    def __repr__(self):
        return 'TimeProductPass()'

    def __str__(self):
        return 'TimeProductPass()'


class ProductLabelProductPass(ProductPass.CompositeProductPass):
    """
    When run, produce a dictionary such that dict['target_set'] is the
    set of targets named in primary HDUs within this product,
    dict['File_Area_Observational'] is a dict of lists of HDU
    information for the product file, and dict['Time'] is a pair of
    the start and end times of the observation.
    """
    def __init__(self):
        passes = [TargetProductPass(),
                  FileAreaProductPass(),
                  TimeProductPass()]
        super(ProductLabelProductPass, self).__init__(passes)

    def process_product(self, product, files):
        res0 = super(ProductLabelProductPass,
                     self).process_product(product, files)
        try:
            res = dict(res0)
            return res
        except:
            return None

    def __str__(self):
        return 'ProductLabelProductPass'

    def __repr__(self):
        return 'ProductLabelProductPass()'

if __name__ == '__main__':
    # in visit_25
    lid = pdart.pds4.LID.LID(
        'urn:nasa:pds:hst_09746:data_acs_raw:j8rl25pbq_raw')
    product = pdart.pds4.Product.Product(FileArchives.get_any_archive(), lid)
    # pp = FileAreaProductPass()
    # pp = TargetProductPass()
    # pp = TimeProductPass()
    pp = ProductLabelProductPass()
    ppr = ProductPass.ProductPassRunner()
    print 60 * '-'
    print 8 * '-', product
    try:
        res = ppr.run_product(pp, product)
        print "SUCCESSFUL CALCULATION"
        if res.is_success():
            print pprint.PrettyPrinter(indent=2, width=78).pformat(res.value)
        else:
            print pprint.PrettyPrinter(indent=2,
                                       width=78).pformat(res.exceptions)

    except:
        print "FAILED CALCULATION"
        print traceback.format_exc()