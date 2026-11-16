import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))

from dmPaths import dupes_directory, rules_paths  # noqa: E402


class RulesPathsTest(unittest.TestCase):

    def test_installed_plugin(self):
        # constants.py builds SCRIPTDIRECTORY with a trailing backslash
        data = 'C:\\Users\\me\\AppData\\Roaming\\cYo\\ComicRack Community Edition'
        rules, folder, old = rules_paths(data + '\\Scripts\\Duplicates Manager\\')
        self.assertEqual(folder, data + '\\PluginData\\Duplicates Manager')
        self.assertEqual(rules, data + '\\PluginData\\Duplicates Manager\\dmrules.dat')
        self.assertEqual(old, data + '\\Scripts\\Duplicates Manager\\dmrules.dat')

    def test_portable_copy(self):
        rules, _, _ = rules_paths('K:\\ComicRackCE-Dev\\app\\Data\\Scripts\\Duplicates Manager\\')
        self.assertEqual(rules, 'K:\\ComicRackCE-Dev\\app\\Data\\PluginData\\Duplicates Manager\\dmrules.dat')

    def test_rules_never_inside_the_plugin_folder(self):
        script_dir = 'D:\\x\\Scripts\\DM\\'
        rules, _, old = rules_paths(script_dir)
        self.assertFalse(rules.startswith(script_dir))
        self.assertNotEqual(rules, old)

    def test_no_parent_falls_back_to_plugin_folder(self):
        rules, _, _ = rules_paths('DM\\')
        self.assertEqual(rules, 'DM\\dmrules.dat')


class DupesDirectoryTest(unittest.TestCase):

    def test_default_when_not_set(self):
        self.assertEqual(dupes_directory(['@ MOVEFILES True', 'filesize keep largest'], r'C:\d'), r'C:\d')

    def test_set_in_rules(self):
        self.assertEqual(dupes_directory([r'@ DUPESDIRECTORY H:\Sys\DupeQ  # dump'], r'C:\d'), r'H:\Sys\DupeQ')

    def test_quoted_path_with_spaces_and_no_space_after_at(self):
        self.assertEqual(dupes_directory([r'@dupesdirectory "D:\My Comics\Dupes"'], r'C:\d'), r'D:\My Comics\Dupes')

    def test_comment_and_other_lines_ignored(self):
        self.assertEqual(dupes_directory([r'# @ DUPESDIRECTORY X:\no', r'filepath keep H:\Library'], r'C:\d'), r'C:\d')

    def test_last_setting_wins(self):
        self.assertEqual(dupes_directory([r'@ DUPESDIRECTORY A:\x', r'@ DUPESDIRECTORY B:\y'], r'C:\d'), r'B:\y')


if __name__ == '__main__':
    unittest.main()
