"""
Pretty-printing functionality.
"""
from pdart.xml.Schema import run_subprocess, verify_label_or_raise


def pretty_print(str: bytes) -> bytes:
    """Reformat XML using xmllint --format."""
    (exit_code, stderr, stdout) = run_subprocess(["xmllint", "--format", "-"], str)
    if exit_code == 0:
        return stdout
    else:
        # ignore stdout
        raise Exception("pretty_print failed")


def pretty_and_verify(label: bytes, verify: bool) -> bytes:
    assert label[:6] == b"<?xml ", "Not XML"
    label = pretty_print(label)

    assert label[:6] == b"<?xml ", "Not XML"
    if verify:
        verify_label_or_raise(label)
    return label
