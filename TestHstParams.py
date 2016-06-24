from pdart.exceptions.Combinators import *
from pdart.pds4.Archives import *
from pdart.pds4labels.HstParametersReduction import *
from pdart.reductions.Reduction import *


def get_product():
    """
    Return the first product in the archive whose FITS file is
    parseable
    """
    arch = get_any_archive()
    for b in arch.bundles():
        for c in b.collections():
            for p in c.products():
                for f in p.files():
                    try:
                        filepath = f.full_filepath()
                        fits = pyfits.open(filepath)
                        fits.close()
                        return p
                    except IOError:
                        pass

if __name__ == '__main__':
    reduction = HstParametersReduction()
    runner = DefaultReductionRunner()
    p = get_product()
    print raise_verbosely(lambda: runner.run_product(reduction, p))