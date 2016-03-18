import Targets
import XmlMaker


class TargetIdentificationXmlMaker(XmlMaker.XmlMaker):
    def __init__(self, document, targname):
        self.targname = targname
        super(TargetIdentificationXmlMaker, self).__init__(document)

    def create_xml(self, parent):
        # Move this back up
        target_identification = self.create_child(parent,
                                                  'Target_Identification')
        name_type = Targets.targname_to_target(self.targname)
        if name_type is None:
            name_type = ('Magrathea', 'Planet')
            # Placeholder information until we can better detect targets
            name, type, description, internal_reference = \
                self.create_children(target_identification,
                                     ['name', 'type', 'description',
                                      'Internal_Reference'])
            self.set_text(description, 'Home of Slartibartfast (placeholder)')
        else:
            # Real path
            name, type, internal_reference = \
                self.create_children(target_identification,
                                     ['name', 'type', 'Internal_Reference'])
        self.set_text(name, name_type[0])
        self.set_text(type, name_type[1])
        lid_reference, reference_type = \
            self.create_children(internal_reference,
                                 ['lid_reference', 'reference_type'])

        # TODO This design of the LID is not official, only
        # provisional.  Update it.
        self.set_text(lid_reference,
                      'urn:nasa:pds:context:target:%s.%s' %
                      (name_type[1].lower(), name_type[0].lower()))
        self.set_text(reference_type, 'data_to_target')
