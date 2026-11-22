import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))

from dmGrouping import find_dupe_groups  # noqa: E402


class Book(object):
    def __init__(self, title, bw='Unknown', medium=None):
        self.Title = title
        self.BlackAndWhite = bw
        self.medium = medium

    def GetCustomValue(self, key):
        return self.medium if key == 'Medium' else None


def comic(series, number, cvdb='', name=None, title='', bw='Unknown', medium=None):
    # Same layout as the tuples ProcessDuplicates builds (constants.py):
    # SERIES, NUMBER, VOLUME, FILENAME, PAGECOUNT, FILESIZE, ID, CVDB_ID,
    # FILEPATH, TAGS, NOTES, FILETYPE, SCAN, BOOK
    name = name or '%s %s %s' % (series, number, cvdb)
    return (series, number, '', name, 20, 1.0, name, cvdb, name, '', '', 'cbz', '', Book(title, bw, medium))


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

    def test_cover_variants_sharing_an_id_stay_apart(self):
        # variants are often scraped to the plain issue's id
        groups = find_dupe_groups([
            comic('slingers', '1', '7', 'a'), comic('slingers', '01', '7', 'a2'),
            comic('slingers', '1A', '7', 'b'), comic('slingers', '1a', '7', 'b2'),
            comic('slingers', '1B', '7', 'c'), comic('slingers', '1C', '7', 'd'),
        ])
        self.assertEqual(names(groups), [['a', 'a2'], ['b', 'b2']])

    def test_unnumbered_copy_still_joins_by_id(self):
        groups = find_dupe_groups([comic('x', '1', '5', 'a'), comic('x', '', '5', 'b')])
        self.assertEqual(names(groups), [['a', 'b']])

    def test_leading_zeros_and_decimal_zero_match_by_name(self):
        groups = find_dupe_groups([comic('x', '1', name='a'), comic('x', '001', name='b'), comic('x', '1.0', name='c')])
        self.assertEqual(names(groups), [['a', 'b', 'c']])

    def test_black_and_white_edition_stays_apart(self):
        groups = find_dupe_groups([
            comic('walking dead', '1', '9', 'colour'), comic('walking dead', '1', '', 'colour2'),
            comic('walking dead', '1', '9', 'bw', bw='Yes'), comic('walking dead', '1', '', 'bw2', bw='Yes'),
        ])
        self.assertEqual(names(groups), [['bw', 'bw2'], ['colour', 'colour2']])

    def test_unknown_and_no_count_as_colour(self):
        groups = find_dupe_groups([comic('x', '1', name='a', bw='No'), comic('x', '1', name='b')])
        self.assertEqual(names(groups), [['a', 'b']])

    def test_scan_and_digital_copy_stay_apart(self):
        groups = find_dupe_groups([
            comic('secret invasion', '1', '5', 'scan', medium='Physical'),
            comic('secret invasion', '1', '5', 'digital', medium='Digital'),
        ])
        self.assertEqual(groups, [])

    def test_same_medium_still_groups(self):
        # Digital first: the second scan must still find the first one
        groups = find_dupe_groups([
            comic('x', '1', '5', 'd', medium='Digital'), comic('x', '1', '5', 'p', medium='Physical'),
            comic('x', '1', '5', 'p2', medium=' physical '), comic('x', '1', '', 'd2', medium='Digital'),
        ])
        self.assertEqual(names(groups), [['d', 'd2'], ['p', 'p2']])

    def test_unknown_medium_never_bridges(self):
        # u matches both by id; it joins the first and does not link p to d
        groups = find_dupe_groups([
            comic('x', '1', '5', 'p', medium='Physical'), comic('x', '1', '5', 'u'),
            comic('x', '1', '5', 'd', medium='Digital'),
        ])
        self.assertEqual(names(groups), [['p', 'u']])

    def test_unknown_medium_groups_as_before(self):
        groups = find_dupe_groups([comic('x', '1', name='a', medium=''), comic('x', '1', name='b')])
        self.assertEqual(names(groups), [['a', 'b']])


if __name__ == '__main__':
    unittest.main()
