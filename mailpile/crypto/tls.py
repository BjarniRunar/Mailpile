import time
from mailpile.util import *


def create_TLS_key(PEM_path, key_name, temp_dir):
    """
    This will create a new self-signed TLS key+certificate.
    """
    return False


def update_TLS_certificate(PEM_path, cert_PEM_data, temp_dir):
    """
    Update the TLS certificate part of a PEM file (preserving the key).
    """
    pass


class TlsKeyInfo(dict):
    """
    Class describing a TLS key and certificate.
    """
    def __init__(self, cert_path):
        self.loaded = time.time()
        self.valid = False
        # FIXME: Shell out to openssl to parse the certificate


if __name__ == "__main__":
    import sys
    import doctest

    results = doctest.testmod(optionflags=doctest.ELLIPSIS)
    print '%s' % (results, )
    if results.failed:
        sys.exit(1)
