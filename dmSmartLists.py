#####################################################################################################
##
##      dmSmartLists.py - part of duplicatemanager, a script for comicrack
##
##      Smart-list rules that find books which are copies of the same issue,
##      using the same grouping as the Duplicates Manager itself (dmGrouping.py).
##
######################################################################################################

# Use in a smart list as: "User Scripts" -> "Duplicates: same issue".
# The rule only sees books that earlier rules in the list let through, so put
# every exclusion (paths, tags, ...) ABOVE this rule, never below it: a rule
# below would remove one copy of a pair and leave the other on its own.
#
# Books are the same issue when they share a ComicVine issue id (custom value
# comicvine_issue, or Comic Vine Scraper's CVDB tag or note) or the same series, volume and
# number; see dmGrouping.py for the details. Cover variants (1A, 1B, ...) and
# black and white editions are kept apart from the plain issue. Dates, format
# and language are ignored on purpose: the built-in "Only Duplicates" rule
# compares them exactly, so a copy with a full cover date and one with only the
# month never match.

import re

from dmGrouping import find_dupe_groups
from getcvdb import extract_issue_ref

CV_KEY = 'comicvine_issue'

_vol_suffix = re.compile(r',?\s*vol(ume)?\.?\s*\d+\s*$', re.I)
_non_alnum = re.compile(r'[^0-9a-z]+')


def _series_key(series):
    if not series:
        return ''
    series = _vol_suffix.sub('', series.lower()).replace('&', ' and ')
    return ''.join(w for w in _non_alnum.split(series) if w and w not in ('the', 'a', 'an'))


def _cv(book):
    value = book.GetCustomValue(CV_KEY)
    if value and value.strip() and value.strip() != '0':
        return value.strip()
    # the CVDB tag or note that Comic Vine Scraper writes
    return extract_issue_ref(book)


def _groups(books):
    # (series key, number, ComicVine id, ComicBook): dmGrouping reads the
    # title and black and white flag from the ComicBook, the tuple's last item.
    comics = [((_series_key(b.ShadowSeries), b.ShadowVolume), b.ShadowNumber, _cv(b) or '', b)
              for b in books if b.IsLinked]
    return [[c[-1] for c in g] for g in find_dupe_groups(comics, 0, 1, 2)]


def _widest_page(book):
    # ComicRack records page sizes only for pages it has opened or scanned; 0 when unknown.
    try:
        return max([p.ImageWidth for p in book.Pages] or [0])
    except Exception:
        return 0


def _keeper(group):
    '''The copy to keep: scraped first, then the higher resolution when it is
    known for every copy, then more pages, then the bigger file.'''
    widths = [_widest_page(b) for b in group]
    use_width = all(widths)
    ranked = [(1 if _cv(b) else 0, widths[i] if use_width else 0, b.PageCount, b.FileSize, i)
              for i, b in enumerate(group)]
    return group[max(ranked)[-1]]


#@Name	Duplicates: same issue
#@Hook	CreateBookList
#@PCount	0
#@Description	Books that are copies of the same issue (same ComicVine id, or same series/volume/number). Cover variants and B&W editions are kept apart. Put exclusion rules above this one.
def DuplicateIssues(books, a, b):
    result = []
    for g in _groups(books):
        result.extend(g)
    return result


#@Name	Duplicates: extra copies only
#@Hook	CreateBookList
#@PCount	0
#@Description	Like "Duplicates: same issue", but leaves out the copy to keep (scraped, then higher resolution, more pages, bigger file), so the list holds only the candidates to remove. A rough guide, not a quality check.
def DuplicateIssueExtras(books, a, b):
    result = []
    for g in _groups(books):
        keep = _keeper(g)
        result.extend(x for x in g if x is not keep)
    return result
