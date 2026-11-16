import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))

from dmPaths import rules_paths  # noqa: E402


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


if __name__ == '__main__':
    unittest.main()
