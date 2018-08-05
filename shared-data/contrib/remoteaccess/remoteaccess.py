# This is the Mailpile remote-access code.
#
# The basic design of a remote access method is as follows:
#
#  - Each RemoteAccessWorker provides:
#      - A method for requesting a public address
#      - A method for generating a TLS certificate (or equivalent)
#      - A method for checking availability status (incl. logs?)
#      - A method for (re)connecting
#  - Internally, each RemoteAccessWorker is responsible for spawning
#    any necessary external (or internal) processes and configuring and
#    running dedicated HTTP daemon for each one.
#
import threading
import traceback

import mailpile.security as security
from mailpile.commands import Command
from mailpile.crypto.tls import *
from mailpile.httpd import HttpWorker
from mailpile.i18n import gettext as _
from mailpile.i18n import ngettext as _n
from mailpile.util import *

import mailpile.plugins.remoteaccess.acme_tiny as acme_tiny

try:
    import pagekite
    import pagekite.pk as pk
    import pagekite.logging as logging
except:
    pagekite = None


# We only want one of each of these per Mailpile
SHARED_PAGEKITE_MANAGER = None
SHARED_TOR_MANAGER = None


##[ Configuration ]##########################################################

class RemoteAccessStatus(dict):
    def __init__(self):
        pass


class RemoteAccessWorker(HttpWorker):
    def __init__(self, session):
        HttpWorker.__init__(self, session)
        self.config_changed = False
        self.address = None
        self.tls_key_info = None
        self.tls_PEM_filename = None

    def _default_tls_PEM_filename(self):
        return os.path.join(self.session.config.workdir, 
                            (self.address or 'default') + '.pem')

    def _tls_PEM_mtime(self):
        try:
             return os.stat(self.tls_PEM_filename).mtime
        except (OSError, IOError, AttributeError):
             return 0

    def _update_configuration(self, ra_cfg):
        changed = []
        if self.address != ra_cfg.address:
            self.address = ra_cfg.address
            changed.append('address')

        current_tls_PEM_filename = (
            ra_cfg.tls_PEM_filename or self._default_tls_PEM_filename())
        if self.tls_PEM_filename != current_tls_PEM_filename:
            self.tls_PEM_filename = current_tls_PEM_filename
            changed.append('tls_PEM_filename')

        if os.path.exists(self.tls_PEM_filename):
            if ((not self.tls_key_info) or
                    self.tls_key_info.loaded < self._tls_PEM_mtime()):
                self.tls_key_info = TlsCertInfo(self.tls_PEM_filename)
                changed.append('tls_key_info')
        elif self.tls_key_info:
            self.tls_key_info = None
            changed.append('tls_key_info')

        return changed

    def get_address(self, create_new=False):
        if self.address is None and create_new:
            self.address = self._create_address(create_new)
        return self.address

    def _create_address(self, request):
        raise NotImplemented('Please override _create_address in %s' % self)

    def get_tls_cert(self, create_new=False):
        if self.tls_key_info is None and create_new:
            self.tls_key_info = self._create_tls_key(create_new)
        return self.tls_cert_info

    def _create_tls_key(self, request):
        if request is True:
            request = self.address
        self.tls_PEM_filename = self._tls_PEM_filename()
        if create_TLS_key(self.tls_cert_filename, request,
                          temp_dir=self.session.config.tempfile_dir()):
            return TlsCertInfo(self.tls_cert_filename)
        return None

    def connect(self, disconnect=False):
        raise NotImplemented('Please override connect in %s' % self)

    def status(self):
        raise NotImplemented('Please override get_status in %s' % self)

    def notify_config_changed(self):
        # FIXME: Subclasses should be smarter about this!
        self._config_changed = True

    def idle_tick(self):
        if self._config_changed:
            self._reconfigure()

    def run(self):
        if self._setup():
            try:
                return HttpWorker.run(self)
            finally:
                self._cleanup()

    def _setup(self):
        return False  # Subclasses must override this or nothing happens

    def _restart_httpd(self):
        old_httpd = self.httpd
        old_httpd.server_close()
        self._create_httpd()  # FIXME
        old_httpd.shutdown()

    def _reconfigure(self):
        pass

    def _cleanup(self):
        pass


class LanRemoteAccess(RemoteAccessWorker):
    pass


class PageKiteRemoteAccess(RemoteAccessWorker):
    def __init__(self, session):
        RemoteAccessWorker.__init__(self, session)
        self.kitename = None
        self.kitesecret = None

    def _setup(self):
        return True

    def _cleanup(self):
        pass


class OnionRemoteAccess(RemoteAccessWorker):

    def _create_tls_cert(self, request):
        """Onions do not use TLS."""
        return None


class RemoteAccessManager(threading.Thread):
    def __init__(self, session):
        threading.Thread.__init__(self)
        self.daemon = True
        self.session = session
        self.ra_workers = {}

    def notify_config_changed(self):
        # FIXME: Should we be shutting something down?

        for raw in self.ra_workers.values():
            raw.notify_config_changed()

        # FIXME: Check if we should spin up a new worker

    def quit(self, join=False):
        for raw in self.ra_workers.values():
            raw.quit(join=join)

    def run(self):
        print('FIXME: STARTED RemoteAccessManager')
