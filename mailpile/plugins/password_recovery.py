# -*- coding: utf-8 -*-
#
# 3rd Party Assisted Password Recovery (3PAPR)
#
# WARNING: THIS IS EFFECTIVELY A FORM OF KEY ESCROW. CAN OF WORMS?
#
# 3PAPR Preparation:
#
#   1. Mailpile obtains an Escrow Key (public key) for the 3rd Party. This
#      key may be the key of an individual or organization. Ideally, it is
#      single-purpose and dedicated to this user.
#   2. A Recovery Key (128-bit random password) is generated and used to
#      locally store an encrypted copy of Mailpile's master key.
#   3. A Request For Assistance (RFA) is OpenPGP encrypted to the Escrow Key,
#      containing:
#         1. The Recovery Key generated above
#         2. Optionally, a request to first verify the identity of the user
#         3. Instructions on how to communicate the Recovery Key to the user 
#   3. The RFA is stored locally until the user initiates Password Recovery
#      or disables 3PAPR.
#
# Password recovery;
#  
#   1. The user submits the RFA to the 3rd Party.
#   2. Upon receipt, the 3rd Party:
#         1. Decrypts the RFA
#         2. If requested, verifies the identity of the user, using some
#            out-of-band process.
#         3. Send the Recovery Key to the user as requested
#         4. Discards the Escrow Key (if possible)
#   3. The user inputs the Recovery Key into Mailpile, which allows Mailpile
#      to unlock the configuration and log the user in.
#   4. The user is prompted to change their password
#   5. The old RFA is discarded and 3PAPR Preparation is repeated.
#
# Disabling 3PAPR:
#
#   1. The user deletes the RFA from local storage
#   2. Optional: The user requests the 3rd Party delete the Escrow Key.
#
# Detecting Abuse:
#   
#   1. The recovery process *should* be noisy, so the user is likely to notice
#      that someone has submitted the RFA. Using multiple channels is recommended,
#      including SMS messaging.
#   2. Specialized 3rd Party providers should allow the user to query whether an
#      Escrow Key still exists (if it's gone, that may mean it has been used).
#
import mailpile.security as security
from mailpile.commands import Command
from mailpile.i18n import gettext as _
from mailpile.i18n import ngettext as _n
from mailpile.plugins import PluginManager


_plugins = PluginManager(builtin=__file__)


##[ Configuration ]###########################################################


def knownEscrowServices():
    return {
        'auto-password-reset@mailpile.is': {
             'name': _('Mailpile.is automated password reset'),
             'description': '...',
             'method': 'https://mailpile.is/password-reset',
             'public-key': ''},
        'verified-password-reset@mailpile.is': {
             'name': _('Mailpile.is verified password reset'),
             'description': '...',
             'method': 'https://mailpile.is/password-reset',
             'public-key': ''}}


##[ Commands ]################################################################

class FooFoo(Command):
   """Do a thing"""
    SYNOPSIS = (None, 'foo', 'foo', '[--flags]')
    ORDER = ('Config', 0)
    HTTP_CALLABLE = ('POST', )
    HTTP_POST_VARS = {
        'force': 'Force changes'
    }
    COMMAND_SECURITY = security.CC_CHANGE_SECURITY

    class CommandResult(Command.CommandResult):
        def as_text(self):
            if not self.result:
                return 'Failed'
            if not self.result['msg_ids']:
                return 'Nothing happened'

    def command(self, **kwargs):
        return self._success(_('I like lamp'))


_plugins.register_commands(Tag, TagAutomation, # TagLater, TagTemporarily,
                           AddTag, DeleteTag, ListTags,
                           Filter, DeleteFilter,
                           MoveFilter, ListFilters)
