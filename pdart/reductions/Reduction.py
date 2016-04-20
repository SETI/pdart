from pdart.exceptions.Combinators import parallel_list


class Reduction(object):
    """
    A collection of methods to reduce PDS4 and FITS structure into a
    new form.
    """
    def reduce_archive(self, archive_root, get_reduced_bundles):
        pass

    def reduce_bundle(self, archive, lid, get_reduced_collections):
        pass

    def reduce_collection(self, archive, lid, get_reduced_products):
        pass

    def reduce_product(self, archive, lid, get_reduced_fits_files):
        pass

    def reduce_fits_file(self, file, get_reduced_hdus):
        pass

    def reduce_hdu(self, n, hdu,
                   get_reduced_header_unit,
                   get_reduced_data_unit):
        pass

    def reduce_header_unit(self, n, get_header_unit):
        pass

    def reduce_data_unit(self, n, get_data_unit):
        pass


class ReductionRunner(object):
    """
    An algorithm to recursively reduce PDS4 and FITS structures
    according to a :class:`Reduction` instance.

    You don't have to understand how this works to use it.
    """
    def run_archive(self, reduction, archive):
        def get_reduced_bundles():
            bundles = list(archive.bundles())
            return parallel_list('run_archive',
                                 [lambda: self.run_bundle(reduction, bundle)
                                  for bundle in bundles])

        return reduction.reduce_archive(archive.root, get_reduced_bundles)

    def run_bundle(self, reduction, bundle):
        def get_reduced_collections():
            collections = list(bundle.collections())
            return parallel_list('run_bundle',
                                 [lambda: self.run_collection(reduction,
                                                              collection)
                                  for collection in collections])

        return reduction.reduce_bundle(bundle.archive, bundle.lid,
                                       get_reduced_collections)

    def run_collection(self, reduction, collection):
        def get_reduced_products():
            products = list(collection.products())
            return parallel_list('run_collection',
                                 [lambda: self.run_product(reduction, product)
                                  for product in products])

        return reduction.reduce_collection(collection.archive,
                                           collection.lid,
                                           get_reduced_products)

    def run_product(self, reduction, product):
        def get_reduced_fits_files():
            files = list(product.files())
            return parallel_list('run_product',
                                 [lambda: self.run_fits_file(reduction, file)
                                  for file in files])

        return reduction.reduce_product(product.archive, product.lid,
                                        get_reduced_fits_files)

    def run_fits_file(self, reduction, file):
        def get_reduced_hdus():
            fits = pyfits.open(file.full_filepath())
            try:
                return parallel_list('run_fits_file',
                                     [lambda: self.run_hdu(self, reduction,
                                                           (n, hdu))
                                      for n, hdu in enumerate(fits)])
            finally:
                fits.close()

        return reduction.reduce_fits_file(file, get_reduced_hdus)

    def run_hdu(self, reduction, (n, hdu)):
        def get_reduced_header_unit():
            return reduction.reduce_header_unit(n, lambda: hdu.header)

        def get_reduced_data_unit():
            return reduction.reduce_data_unit(n, lambda: hdu.data)

        return reduction.reduce_hdu(n, hdu,
                                    get_reduced_header_unit,
                                    get_reduced_data_unit)

    def run_header_unit(self, reduction, n, hu):
        return reduction.reduce_header_unit(n, get_header_unit)

    def run_data_unit(self, reduction, n, du):
        return reduction.reduce_data_unit(n, get_data_unit)


def run_reduction(reduction, archive):
    """
    Run a :class:`Reduction` on an :class:`Archive` using the default
    recursion.
    """
    return ReductionRunner().run_archive(reduction, archive)