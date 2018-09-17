from pdart.xml.Pds4Version import HST_SHORT_VERSION, PDS4_SHORT_VERSION

_PDS4_SCHEMA_LOCATION = "http://pds.nasa.gov/pds4/pds/v1"

_VERSIONED_PDS4_SCHEMA_LOCATION = \
    "https://pds.nasa.gov/pds4/pds/v1/PDS4_PDS_%s.xsd" % \
    (PDS4_SHORT_VERSION,)

_VERSIONED_PDS4_SCHEMATRON_LOCATION = \
    "https://pds.nasa.gov/pds4/pds/v1/PDS4_PDS_%s.sch" % \
    (PDS4_SHORT_VERSION,)

_HST_SCHEMA_LOCATION = "http://pds.nasa.gov/pds4/mission/hst/v1"

_VERSIONED_HST_SCHEMA_LOCATION = \
    "https://pds.nasa.gov/pds4/mission/hst/v1/PDS4_HST_%s.xsd" % \
    (HST_SHORT_VERSION,)

_VERSIONED_HST_SCHEMATRON_LOCATION = \
    "https://pds.nasa.gov/pds4/mission/hst/v1/PDS4_HST_%s.sch" % \
    (HST_SHORT_VERSION,)

############################################################


_PDS4_NAMESPACE = 'xmlns="http://pds.nasa.gov/pds4/pds/v1"'  # type: str

_HST_NAMESPACE = \
    'xmlns:hst="http://pds.nasa.gov/pds4/mission/hst/v1"'  # type: str

_PDS_NAMESPACE = 'xmlns:pds="http://pds.nasa.gov/pds4/pds/v1"'  # type: str

_XSI_NAMESPACE = \
    'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'  # type: str


############################################################

def make_namespaces(*parts):
    return ' '.join(parts)


def make_schema_locations(*args):
    return 'xsi:schemaLocation="%s"' % ' '.join(args)


############################################################

BUNDLE_NAMESPACES = make_namespaces(_PDS4_NAMESPACE,
                                    _PDS_NAMESPACE)

BROWSE_PRODUCT_NAMESPACES = \
    make_namespaces(_PDS4_NAMESPACE,
                    _PDS_NAMESPACE,
                    _XSI_NAMESPACE,
                    make_schema_locations(_VERSIONED_PDS4_SCHEMA_LOCATION))

COLLECTION_NAMESPACES = make_namespaces(_PDS4_NAMESPACE,
                                        _PDS_NAMESPACE)

DOCUMENT_PRODUCT_NAMESPACES = make_namespaces(
    _PDS4_NAMESPACE,
    _PDS_NAMESPACE,
    _HST_NAMESPACE,
    _XSI_NAMESPACE,
    make_schema_locations(
        _PDS4_SCHEMA_LOCATION,
        _VERSIONED_PDS4_SCHEMA_LOCATION))

FITS_PRODUCT_NAMESPACES = make_namespaces(
    _PDS4_NAMESPACE,
    _PDS_NAMESPACE,
    _HST_NAMESPACE,
    _XSI_NAMESPACE,
    make_schema_locations(
        _PDS4_SCHEMA_LOCATION,
        _VERSIONED_PDS4_SCHEMA_LOCATION,
        _HST_SCHEMA_LOCATION,
        _VERSIONED_HST_SCHEMA_LOCATION))


############################################################

def make_xml_model(href):
    return '<?xml-model href="%s" \
schematypens="http://purl.oclc.org/dsdl/schematron"?>' % href


PDS4_XML_MODEL = make_xml_model(_VERSIONED_PDS4_SCHEMATRON_LOCATION)

HST_XML_MODEL = make_xml_model(_VERSIONED_HST_SCHEMATRON_LOCATION)