# IDEA:
#
#   This plugin automatically maintains a dictionary of words we've seen in e-mail.
#   Maybe also phrases?
#
#   This dictionary could then be used for the following things:
#      - Allow partial word searches
#      - Discover related terms
#      - Suggest phrases?
#
# Ideas:
#
#    1. hook into the search engine keyword hooks, implement a popuplarity
#       count of keywords we see that probably aren't machine-generated.
#    2. Keep the top 100k words? Some arbitrary number.
#    3. Seed the dictionary using a known language-specific one?
#    4. Implement some sort of merging algorithm to merge words that are
#       almost but not quite identical.
#    5. If we see a word that's not on the list, but contains a substring that is
#       on the list, add the substring to the keyword list?
#    6. When searching, propose alternate terms?
#
"""
Usage examples and doctests...

"""
import re
from mailpile.i18n import gettext as _
from mailpile.i18n import ngettext as _n
from mailpile.commands import Command
from mailpile.plugins import PluginManager

KEYWORD_COUNTS = {}
NUMBERS_RE = re.compile('^\d+$')


def autodict_kw_filter(index, keywords, **kwargs):
    config = kwargs.get('config') or index.config

    # Count keywords. Processing and cleanup happens elsewhere.
    global KEYWORD_COUNTS
    new_keywords = []
    for kw in keywords:
        if (len(kw) > 3
                and (':' not in kw)
                and not NUMBERS_RE.match(kw)):
            if len(kw) > 24:
                # Long words are always "new", never recorded.
                new_keywords.append(kw)
            else:
                if kw not in KEYWORD_COUNTS:
                    new_keywords.append(kw)
                KEYWORD_COUNTS[kw] = KEYWORD_COUNTS.get(kw, 0) + 1

    # FIXME: Inject keywords?

    if new_keywords:
        print('NEW: %s' % ', '.join(new_keywords))
    return keywords


if __name__ == "__main__":
    import sys
    import doctest

    results = doctest.testmod(optionflags=doctest.ELLIPSIS)
    print '%s' % (results, )
    if results.failed:
        sys.exit(1)

else:
    _plugins = PluginManager(builtin=__file__)
    _plugins.register_keyword_filter('autodict', autodict_kw_filter)
