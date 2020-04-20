"""
Importing this module appends the path for the ``pds-tools`` package
directory to the system path.  I assume that ``pds-tools`` lives in a
sibling directory.

This is a temporary hack until I figure out the correct way to
generally combine my packages with the ``pds-tools`` modules.
"""
import os.path
import sys


_PDS_TOOLS_DIR = os.path.join('../../pds-tools')

sys.path.append(_PDS_TOOLS_DIR)