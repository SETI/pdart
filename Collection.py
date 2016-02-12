import os.path
import re

import ArchiveComponent
import LID
import Product

class Collection(ArchiveComponent.ArchiveComponent):
    DIRECTORY_PATTERN = '\Adata_([a-z0-9]+)_([a-z0-9_]+)\Z'

    def __init__(self, arch, lid):
        ArchiveComponent.ArchiveComponent.__init__(self, arch, lid)

    def __repr__(self):
        return 'Collection(%s, %s)' % (repr(self.archive), repr(self.lid))
                                                   
    def directoryFilepath(self):
        return os.path.join(self.archive.root, 
                            self.lid.bundleID, self.lid.collectionID)

    def products(self):
        dirFP = self.directoryFilepath()
        for subdir in os.listdir(dirFP):
            if re.match(Product.Product.DIRECTORY_PATTERN, subdir):
                productLID = LID.LID('%s:%s' % (self.lid.LID, subdir))
                yield Product.Product(self.archive, productLID)
        

