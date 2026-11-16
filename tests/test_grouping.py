import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))

from dmGrouping import find_dupe_groups  # noqa: E402


class Book(object):
    def __init__(self, title):
        self.Title = title


def comic(series, number, cvdb='', name=None, title=''):
    # Same layout as the tuples ProcessDuplicates builds (constants.py):
    # SERIES, NUMBER, VOLUME, FILENAME, PAGECOUNT, FILESIZE, ID, CVDB_ID,
    # FILEPATH, TAGS, NOTES, FILETYPE, SCAN, BOOK
    name = name or '%s %s %s' % (series, number, cvdb)
    return (series, number, '', name, 20, 1.0, name, cvdb, name, '', '', 'cbz', '', Book(title))


def names(groups):
    return sorted(sorted(c[3] for c in g) for g in groups)


class FindDupeGroupsTest(unittest.TestCase):

    def test_same_series_and_number(self):
        groups = find_dupe_groups([comic('batman', '1'), comic('batman', '1', name='b'), comic('batman', '2')])
        self.assertEqual(names(groups), [['b', 'batman 1 ']])

    def test_same_comicvine_id_under_different_series(self):
        # a renamed series: only the ComicVine id says these are one issue
        groups = find_dupe_groups([comic('countdown', '6', '111', 'a'), comic('countdown final crisis', '6', '111', 'b')])
        self.assertEqual(names(groups), [['a', 'b']])

    def test_unscraped_copy_joins_scraped_one(self):
        groups = find_dupe_groups([comic('x men', '5', '333', 'a'), comic('x men', '5', '', 'b')])
        self.assertEqual(names(groups), [['a', 'b']])

    def test_different_ids_never_joined_by_name(self):
        groups = find_dupe_groups([comic('slingers', '1', '1', 'a'), comic('slingers', '1', '2', 'b')])
        self.assertEqual(groups, [])

    def test_unscraped_copies_stay_apart_from_ambiguous_ids(self):
        groups = find_dupe_groups([
            comic('slingers', '1', '1', 'a'), comic('slingers', '1', '2', 'b'),
            comic('slingers', '1', '', 'c'), comic('slingers', '1', '', 'd'),
        ])
        self.assertEqual(names(groups), [['c', 'd']])

    def test_id_and_name_links_chain(self):
        # a and b share an id, b and c share a name: one group of three
        groups = find_dupe_groups([
            comic('old name', '3', '9', 'a'), comic('new name', '3', '9', 'b'), comic('new name', '3', '', 'c'),
        ])
        self.assertEqual(names(groups), [['a', 'b', 'c']])

    def test_zero_and_blank_ids_are_not_ids(self):
        groups = find_dupe_groups([comic('a', '1', '0', 'a'), comic('b', '2', '0', 'b'), comic('c', '3', None, 'c')])
        self.assertEqual(groups, [])

    def test_unnumbered_comics_need_the_same_title(self):
        groups = find_dupe_groups([
            comic('gallery folio', '', name='a', title='Sable Covers'),
            comic('gallery folio', '', name='b', title='The Vision vs Mantis'),
            comic('gallery folio', '', name='c', title='sable covers '),
        ])
        self.assertEqual(names(groups), [['a', 'c']])

    def test_unnumbered_comics_still_group_by_comicvine_id(self):
        groups = find_dupe_groups([comic('x', '', '5', 'a', 'One'), comic('y', '', '5', 'b', 'Two')])
        self.assertEqual(names(groups), [['a', 'b']])


if __name__ == '__main__':
    unittest.main()
