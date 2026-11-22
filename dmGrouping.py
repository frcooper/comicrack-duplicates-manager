#####################################################################################################
##
##      dmGrouping.py - part of duplicatemanager, a script for comicrack
##
##      Finds the groups of duplicated comics. Plain Python (no ComicRack or .NET
##      imports), so tests can run it outside ComicRack.
##
######################################################################################################

# Two comics are the same issue when:
#   - they carry the same ComicVine issue id, or
#   - they have the same series key and number, and at most one ComicVine id is
#     involved. An unscraped copy joins the scraped one; comics with different
#     ComicVine ids are never joined by name (a renamed series, a variant cover
#     scraped to its own id, ...).
# When several different ids share a series key and number, only the unscraped
# copies are grouped with each other, since nothing says which issue they are.
# Comics without a number also need the same title to be grouped by name.
# Two things keep apart comics that would otherwise match:
#   - a cover variant: a number with a letter suffix (1A, 1B, ...) is often
#     scraped to the plain issue's ComicVine id, so the id only joins comics
#     whose numbers carry the same suffix;
#   - a black and white edition only matches another black and white copy.
# A scan of a print copy and the digital release are never duplicates: the
# custom value Medium (Physical or Digital, set by the Data Manager rule) keeps
# them in separate groups. A comic with no Medium can join either side, but never
# links a Physical copy to a Digital one.

import re

_number_parts = re.compile(r'^(-?)0*(\d+)(?:\.0+)?(.*)$')

# Positions in the comic tuples built by ProcessDuplicates (see constants.py).
SERIES, NUMBER, CVDB_ID = 0, 1, 7


def _cvdb(comic, cvdb_index):
    value = comic[cvdb_index]
    if value is None:
        return None
    value = ('%s' % value).strip()
    if not value or value == '0':
        return None
    return value


def _number_key(number):
    '''Normalised number: "01" and "1.0" are "1", "1A" is "1a".'''
    number = ('%s' % (number or '')).strip().lower()
    m = _number_parts.match(number)
    if m:
        return m.group(1) + m.group(2) + m.group(3).strip()
    return number


def _variant(number):
    '''The suffix that marks a cover variant: "a" for "1A", "" for "1" or no number.'''
    m = _number_parts.match(_number_key(number))
    return m.group(3) if m else ''


def _bw(comic):
    # The ComicBook's BlackAndWhite is a YesNo enum: Unknown, No or Yes.
    return '%s' % getattr(comic[-1], 'BlackAndWhite', '') == 'Yes'


def _medium(comic):
    '''The custom value Medium, lower case: "physical", "digital" or "" when unknown.'''
    get = getattr(comic[-1], 'GetCustomValue', None)
    value = get('Medium') if get else None
    return ('%s' % (value or '')).strip().lower()


def _name_key(comic, series_index, number_index):
    # Without a number, series alone says little (folios, artbooks and one-shots
    # filed under a folder name all share it), so the title must match too.
    # The ComicBook is the tuple's last item.
    number = _number_key(comic[number_index])
    if number:
        return (comic[series_index], number, _bw(comic))
    title = getattr(comic[-1], 'Title', None) or ''
    return (comic[series_index], '', title.strip().lower(), _bw(comic))


def find_dupe_groups(comics, series_index=SERIES, number_index=NUMBER, cvdb_index=CVDB_ID):
    '''Returns a sorted list of groups (lists of comic tuples) with more than one comic.'''
    comics = list(comics)
    parent = list(range(len(comics)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    medium = [_medium(c) for c in comics]

    def union(i, j):
        '''Joins the groups of i and j unless one is Physical and the other Digital.'''
        ri, rj = find(i), find(j)
        if ri == rj:
            return True
        if medium[ri] and medium[rj] and medium[ri] != medium[rj]:
            return False
        parent[ri] = rj
        medium[rj] = medium[rj] or medium[ri]
        return True

    def join(members):
        # Each member joins the first group it may: a Physical and a Digital copy
        # each start their own, and later copies join the group of their medium.
        anchors = []
        for j in members:
            for a in anchors:
                if union(a, j):
                    break
            else:
                anchors.append(j)

    ids = [_cvdb(c, cvdb_index) for c in comics]
    by_id = {}
    by_name = {}
    for i, comic in enumerate(comics):
        if ids[i]:
            key = (ids[i], _variant(comic[number_index]), _bw(comic))
            by_id.setdefault(key, []).append(i)
        by_name.setdefault(_name_key(comic, series_index, number_index), []).append(i)

    for members in by_id.values():
        join(members)

    for members in by_name.values():
        if len(members) < 2:
            continue
        if len(set(ids[i] for i in members if ids[i])) <= 1:
            joined = members
        else:
            joined = [i for i in members if not ids[i]]
        join(joined)

    groups = {}
    for i in range(len(comics)):
        groups.setdefault(find(i), []).append(i)

    # Sort by position, not by the tuples: a tuple's last item is the ComicBook.
    result = [[comics[i] for i in sorted(members, key=lambda i: comics[i][:-1])]
              for members in groups.values() if len(members) > 1]
    result.sort(key=lambda group: group[0][:-1])
    return result
