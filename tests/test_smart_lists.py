import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))

import dmSmartLists  # noqa: E402
from dmSmartLists import DuplicateIssueExtras, DuplicateIssues  # noqa: E402


class Page(object):
    def __init__(self, width):
        self.ImageWidth = width


class Book(object):
    # Only the ComicBook members the smart-list rules read.
    def __init__(self, name, series, number, volume=-1, cv='', notes='', title='', bw='Unknown',
                 pages=20, size=1000, widths=(), linked=True):
        self.name = name
        self.ShadowSeries = series
        self.ShadowNumber = number
        self.ShadowVolume = volume
        self.cv = cv
        self.Notes = notes
        self.Tags = ''
        self.Title = title
        self.BlackAndWhite = bw
        self.PageCount = pages
        self.FileSize = size
        self.Pages = [Page(w) for w in widths]
        self.IsLinked = linked

    def GetCustomValue(self, key):
        return self.cv if key == dmSmartLists.CV_KEY else None


def names(books):
    return sorted(b.name for b in books)


class SmartListTest(unittest.TestCase):

    def test_series_names_are_normalised(self):
        books = [Book('a', 'The Amazing Spider-Man', '1'), Book('b', 'amazing spider man, vol. 1', '01'),
                 Book('c', 'Amazing Spider-Man', '2')]
        self.assertEqual(names(DuplicateIssues(books, None, None)), ['a', 'b'])

    def test_volume_keeps_series_apart(self):
        books = [Book('a', 'Batman', '1', 1940), Book('b', 'Batman', '1', 2011)]
        self.assertEqual(DuplicateIssues(books, None, None), [])

    def test_unlinked_books_are_ignored(self):
        books = [Book('a', 'X', '1'), Book('b', 'X', '1', linked=False)]
        self.assertEqual(DuplicateIssues(books, None, None), [])

    def test_comicvine_note_joins_renamed_series(self):
        books = [Book('a', 'Countdown', '6', cv='111'), Book('b', 'Countdown to Final Crisis', '6', notes='CVDB111')]
        self.assertEqual(names(DuplicateIssues(books, None, None)), ['a', 'b'])

    def test_variants_and_bw_stay_apart(self):
        books = [Book('a', 'Slingers', '1', cv='7'), Book('b', 'Slingers', '1A', cv='7'),
                 Book('c', 'Slingers', '1B', cv='7'), Book('d', 'Slingers', '1', cv='7', bw='Yes')]
        self.assertEqual(DuplicateIssues(books, None, None), [])

    def test_extras_keep_the_scraped_copy(self):
        books = [Book('scraped', 'X', '1', cv='5', size=10), Book('big', 'X', '1', size=99)]
        self.assertEqual(names(DuplicateIssueExtras(books, None, None)), ['big'])

    def test_extras_prefer_resolution_when_known_for_all(self):
        books = [Book('wide', 'X', '1', widths=(1988, 1988), pages=20, size=10),
                 Book('more_pages', 'X', '1', widths=(1200, 1200), pages=24, size=99)]
        self.assertEqual(names(DuplicateIssueExtras(books, None, None)), ['more_pages'])

    def test_extras_ignore_resolution_when_unknown_for_one(self):
        books = [Book('wide', 'X', '1', widths=(1988,), pages=20), Book('unscanned', 'X', '1', pages=24)]
        self.assertEqual(names(DuplicateIssueExtras(books, None, None)), ['wide'])

    def test_extras_fall_back_to_file_size(self):
        books = [Book('small', 'X', '1', size=10), Book('big', 'X', '1', size=99), Book('mid', 'X', '1', size=50)]
        self.assertEqual(names(DuplicateIssueExtras(books, None, None)), ['mid', 'small'])


if __name__ == '__main__':
    unittest.main()
