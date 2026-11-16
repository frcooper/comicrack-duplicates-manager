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


def _name_key(comic, series_index, number_index):
    # Without a number, series alone says little (folios, artbooks and one-shots
    # filed under a folder name all share it), so the title must match too.
    # The ComicBook is the tuple's last item.
    number = comic[number_index]
    if number:
        return (comic[series_index], number)
    title = getattr(comic[-1], 'Title', None) or ''
    return (comic[series_index], '', title.strip().lower())


def find_dupe_groups(comics, series_index=SERIES, number_index=NUMBER, cvdb_index=CVDB_ID):
    '''Returns a sorted list of groups (lists of comic tuples) with more than one comic.'''
    comics = list(comics)
    parent = list(range(len(comics)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i, j):
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[ri] = rj

    ids = [_cvdb(c, cvdb_index) for c in comics]
    by_id = {}
    by_name = {}
    for i, comic in enumerate(comics):
        if ids[i]:
            by_id.setdefault(ids[i], []).append(i)
        by_name.setdefault(_name_key(comic, series_index, number_index), []).append(i)

    for members in by_id.values():
        for j in members[1:]:
            union(members[0], j)

    for members in by_name.values():
        if len(members) < 2:
            continue
        if len(set(ids[i] for i in members if ids[i])) <= 1:
            joined = members
        else:
            joined = [i for i in members if not ids[i]]
        for j in joined[1:]:
            union(joined[0], j)

    groups = {}
    for i in range(len(comics)):
        groups.setdefault(find(i), []).append(i)

    # Sort by position, not by the tuples: a tuple's last item is the ComicBook.
    result = [[comics[i] for i in sorted(members, key=lambda i: comics[i][:-1])]
              for members in groups.values() if len(members) > 1]
    result.sort(key=lambda group: group[0][:-1])
    return result
