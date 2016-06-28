import sys

from pdart.reductions.Reduction import *
from pdart.xml.Templates import *


hst = interpret_template("""<hst:HST>
<NODE name="parameters_general"/>
<NODE name="parameters_instrument"/>
</hst:HST>""")

parameters_general = interpret_template("""<hst:Parameters_General>
  <hst:stsci_group_id><NODE name="stsci_group_id" /></hst:stsci_group_id>
  <hst:hst_proposal_id><NODE name="hst_proposal_id" /></hst:hst_proposal_id>
  <hst:hst_pi_name><NODE name="hst_pi_name" /></hst:hst_pi_name>
  <hst:hst_target_name><NODE name="hst_target_name" /></hst:hst_target_name>
  <hst:aperture_type><NODE name="aperture_type" /></hst:aperture_type>
  <hst:exposure_duration><NODE name="exposure_duration" />\
</hst:exposure_duration>
  <hst:exposure_type><NODE name="exposure_type" /></hst:exposure_type>
  <hst:filter_name><NODE name="filter_name" /></hst:filter_name>
  <hst:fine_guidance_system_lock_type>\
<NODE name="fine_guidance_system_lock_type" />\
</hst:fine_guidance_system_lock_type>
  <hst:gyroscope_mode><NODE name="gyroscope_mode" /></hst:gyroscope_mode>
  <hst:instrument_mode_id><NODE name="instrument_mode_id" />\
</hst:instrument_mode_id>
  <hst:moving_target_flag><NODE name="moving_target_flag" />\
</hst:moving_target_flag>
</hst:Parameters_General>""")

parameters_acs = interpret_template("""<hst:Parameters_ACS>
<hst:detector_id><NODE name="detector_id" /></hst:detector_id>
<hst:gain_mode_id><NODE name="gain_mode_id" /></hst:gain_mode_id>
<hst:observation_type><NODE name="observation_type" /></hst:observation_type>
<hst:repeat_exposure_count><NODE name="repeat_exposure_count" />\
</hst:repeat_exposure_count>
<hst:subarray_flag><NODE name="subarray_flag" /></hst:subarray_flag>
</hst:Parameters_ACS>""")

parameters_wfc3 = interpret_template("""<hst:Parameters_WFC3>
<hst:detector_id><NODE name="detector_id" /></hst:detector_id>
<hst:observation_type><NODE name="observation_type" /></hst:observation_type>
<hst:repeat_exposure_count><NODE name="repeat_exposure_count" />\
</hst:repeat_exposure_count>
<hst:subarray_flag><NODE name="subarray_flag" /></hst:subarray_flag>
</hst:Parameters_WFC3>""")

parameters_wfpc2 = interpret_template("""<hst:Parameters_WFPC2>
<hst:bandwidth><NODE name="bandwidth" /></hst:bandwidth>
<hst:center_filter_wavelength><NODE name="center_filter_wavelength" />\
</hst:center_filter_wavelength>
<hst:targeted_detector_id><NODE name="targeted_detector_id" />\
</hst:targeted_detector_id>
<hst:gain_mode_id><NODE name="gain_mode_id" /></hst:gain_mode_id>
<hst:pc1_flag><NODE name="pc1_flag" /></hst:pc1_flag>
<hst:wf2_flag><NODE name="wf2_flag" /></hst:wf2_flag>
<hst:wf3_flag><NODE name="wf3_flag" /></hst:wf3_flag>
<hst:wf4_flag><NODE name="wf4_flag" /></hst:wf4_flag>
</hst:Parameters_WFPC2>""")

wrapper = interpret_document_template("""<NODE name="wrapped" />""")


def get_repeat_exposure_count(product_id, instrument, header):
    return placeholder_int(product_id, 'repeat_exposure_count')


def get_subarray_flag(product_id, instrument, header):
    return placeholder(product_id, 'subarray_flag')


def get_targeted_detector_id(product_id, instrument, header):
    return placeholder(product_id, 'targeted_detector_id')


def get_pc1_flag(product_id, instrument, header):
    return placeholder_int(product_id, 'pc1_flag')


def get_wf2_flag(product_id, instrument, header):
    return placeholder_int(product_id, 'wf2_flag')


def get_wf3_flag(product_id, instrument, header):
    return placeholder_int(product_id, 'wf3_flag')


def get_wf4_flag(product_id, instrument, header):
    return placeholder_int(product_id, 'wf4_flag')


def get_aperture_type(product_id, instrument, header):
    if instrument == 'wfpc2':
        # TODO: should be None?  But it's required.  What to do?
        return placeholder(product_id, 'aperture_type')
    else:
        try:
            return header['APERTURE']
        except KeyError:
            return placeholder(product_id, 'aperture_type')


def get_bandwidth(product_id, instrument, header):
    if instrument == 'wfpc2':
        try:
            return str(header['BANDWID'] * 1.e-4)
        except KeyError:
            return placeholder_float(product_id, 'bandwidth')


def get_center_filter_wavelength(product_id, instrument, header):
    if instrument == 'wfpc2':
        try:
            return str(header['CENTRWV'] * 1.e-4)
        except KeyError:
            return placeholder_float(product_id, 'center_filter_wavelength')


def get_detector_id(product_id, instrument, header):
    try:
        detector = header['DETECTOR']
    except KeyError:
        return placeholder(product_id, 'detector_id')

    if instrument == 'wfpc2':
        if detector == '1':
            return 'PC1'
        else:
            return 'WF' + detector
    else:
        return detector


def get_exposure_duration(product_id, instrument, header):
    try:
        return str(header['EXPTIME'])
    except KeyError:
        return placeholder_float(product_id, 'exposure_duration')


def get_exposure_type(product_id, instrument, header):
    try:
        return str(header['EXPFLAG'])
    except KeyError:
        return placeholder(product_id, 'exposure_type')


def get_filter_name(product_id, instrument, header):
    try:
        if instrument == 'wfpc2':
            filtnam1 = header['FILTNAM1'].strip()
            filtnam2 = header['FILTNAM2'].strip()
            if filtnam1 == '':
                return filtnam2
            elif filtnam2 == '':
                return filtnam1
            else:
                return '%s+%s' % (filtnam1, filtnam2)
        elif instrument == 'acs':
            filter1 = header['FILTER1']
            filter2 = header['FILTER2']
            if filter1.startswith('CLEAR'):
                if filter2.startswith('CLEAR'):
                    return 'CLEAR'
                else:
                    return filter2
            else:
                if filter2.startswith('CLEAR'):
                    return filter1
                else:
                    return '%s+%s' % (filter1, filter2)
        elif instrument == 'wfc3':
            return header['FILTER']
    except KeyError:
        return placeholder(product_id, 'filter_name')


def get_fine_guidance_system_lock_type(product_id, instrument, header):
    try:
        return header['FGSLOCK']
    except KeyError:
        return placeholder(product_id, 'fine_guidance_system_lock_type')


def get_gain_mode_id(product_id, instrument, header):
    try:
        if instrument == 'acs':
            return str(header['ATODGAIN'])
        elif instrument == 'wfpc2':
            return 'A2D' + str(int(header['ATODGAIN']))
    except KeyError:
        return placeholder(product_id, 'gain_mode_id')


def get_hst_pi_name(product_id, instrument, header):
    try:
        return '%s, %s %s' % (header['PR_INV_L'],
                              header['PR_INV_F'],
                              header['PR_INV_M'])
    except KeyError:
        return placeholder(product_id, 'hst_pi_name')


def get_hst_proposal_id(product_id, instrument, header):
    try:
        return str(header['PROPOSID'])
    except KeyError:
        return placeholder_int(product_id, 'hst_proposal_id')


def get_hst_target_name(product_id, instrument, header):
    try:
        return header['TARGNAME']
    except KeyError:
        return placeholder(product_id, 'hst_target_name')


def get_instrument_mode_id(product_id, instrument, header):
    try:
        if instrument == 'wfpc2':
            return header['MODE']
        else:
            return header['OBSMODE']
    except KeyError:
        return placeholder(product_id, 'instrument_mode_id')


def get_observation_type(product_id, instrument, header):
    if instrument != 'wfpc2':
        try:
            return header['OBSTYPE']
        except KeyError:
            return placeholder(product_id, 'observation_type')


def known_placeholder(product_id, tag):
    return '### placeholder for %s ###' % tag


def placeholder(product_id, tag):
    note_problem(product_id, tag)
    return '### placeholder for %s ###' % tag


def placeholder_int(product_id, tag):
    note_problem(product_id, tag)
    return '0'


def placeholder_float(product_id, tag):
    note_problem(product_id, tag)
    return '0.0'


def note_problem(product_id, tag):
    if False:
        print ('PROBLEM %s: %s' % (tag, product_id))
        sys.stdout.flush()


class HstParametersReduction(Reduction):
    def reduce_product(self, archive, lid, get_reduced_fits_files):
        # return (Doc -> Node)
        instrument = Product(archive, lid).collection().instrument()
        assert isinstance(instrument, str)
        func = get_reduced_fits_files()[0]
        res = func((lid.product_id, instrument))
        assert res
        return res

    def reduce_fits_file(self, file, get_reduced_hdus):
        # returns ((String, String) -> (Doc -> Node))
        res = get_reduced_hdus()[0]
        assert res
        return res

    def reduce_hdu(self, n, hdu,
                   get_reduced_header_unit,
                   get_reduced_data_unit):
        # returns ((String, String) -> (Doc -> Node)) or None
        if n == 0:
            def result((product_id, instrument)):
                header = hdu.header

                d = {'stsci_group_id': known_placeholder(product_id,
                                                         'stsci_group_id'),
                     'hst_proposal_id':
                         get_hst_proposal_id(product_id, instrument, header),
                     'hst_pi_name': get_hst_pi_name(product_id, instrument,
                                                    header),
                     'hst_target_name':
                         get_hst_target_name(product_id, instrument, header),
                     'aperture_type': get_aperture_type(product_id, instrument,
                                                        header),
                     'exposure_duration': get_exposure_duration(product_id,
                                                                instrument,
                                                                header),
                     'exposure_type': get_exposure_type(product_id, instrument,
                                                        header),
                     'filter_name': get_filter_name(product_id, instrument,
                                                    header),
                     'fine_guidance_system_lock_type':
                         get_fine_guidance_system_lock_type(product_id,
                                                            instrument,
                                                            header),
                     'gyroscope_mode': known_placeholder(product_id,
                                                         'gyroscope_mode'),
                     'instrument_mode_id': get_instrument_mode_id(product_id,
                                                                  instrument,
                                                                  header),
                     'moving_target_flag': 'true'}

                if instrument == 'acs':
                    parameters_instrument = parameters_acs(
                        {'detector_id': get_detector_id(product_id,
                                                        instrument, header),
                         'gain_mode_id': get_gain_mode_id(product_id,
                                                          instrument, header),
                         'observation_type':
                             get_observation_type(product_id, instrument,
                                                  header),
                         'repeat_exposure_count':
                             get_repeat_exposure_count(product_id, instrument,
                                                       header),
                         'subarray_flag':
                             get_subarray_flag(product_id, instrument,
                                               header)})
                elif instrument == 'wfpc2':
                    parameters_instrument = parameters_wfpc2(
                        {'bandwidth': get_bandwidth(product_id, instrument,
                                                    header),
                         'center_filter_wavelength':
                             get_center_filter_wavelength(product_id,
                                                          instrument,
                                                          header),
                         'targeted_detector_id':
                             get_targeted_detector_id(product_id, instrument,
                                                      header),
                         'gain_mode_id': get_gain_mode_id(product_id,
                                                          instrument, header),
                         'pc1_flag': get_pc1_flag(product_id, instrument,
                                                  header),
                         'wf2_flag': get_wf2_flag(product_id, instrument,
                                                  header),
                         'wf3_flag': get_wf3_flag(product_id, instrument,
                                                  header),
                         'wf4_flag': get_wf4_flag(product_id, instrument,
                                                  header)})
                elif instrument == 'wfc3':
                    parameters_instrument = parameters_wfc3(
                        {'detector_id': get_detector_id(product_id,
                                                        instrument,
                                                        header),
                         'observation_type':
                             get_observation_type(product_id,
                                                  instrument, header),
                         'repeat_exposure_count':
                             get_repeat_exposure_count(product_id,
                                                       instrument, header),
                         'subarray_flag':
                             get_subarray_flag(product_id,
                                               instrument, header)})
                else:
                    assert False, 'Bad instrument value: %s' % instrument

                # Wrap the fragment and return it.
                return hst({
                        'parameters_general': parameters_general(d),
                        'parameters_instrument': parameters_instrument})

            return result
