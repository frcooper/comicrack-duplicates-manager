#####################################################################################################
##
##      dmPaths.py - part of duplicatemanager, a script for comicrack
##
##      Where the user's rules file lives. Plain Python (no .NET imports), so
##      tests can run it outside ComicRack.
##
######################################################################################################

# ComicRack deletes a plugin's whole folder when it is uninstalled (KeepFiles in
# Package.ini only protects files when a new version is installed over the old
# one), so the user's dmrules.dat lives outside it, next to ComicRack's own data:
#
#   <ComicRack data>\Scripts\Duplicates Manager\     the plugin (replaced freely)
#   <ComicRack data>\PluginData\Duplicates Manager\  dmrules.dat (kept)
#
# For a normal install <ComicRack data> is %APPDATA%\cYo\ComicRack Community
# Edition; a portable copy keeps it under its own Data folder.

RULESFILENAME = 'dmrules.dat'
DATAFOLDER = 'PluginData'
PLUGINFOLDER = 'Duplicates Manager'


def _parent(path):
    path = path.rstrip('\\/')
    cut = max(path.rfind('\\'), path.rfind('/'))
    return path[:cut] if cut > 0 else ''


def _join(*parts):
    return '\\'.join(p.rstrip('\\/') for p in parts if p)


def rules_paths(script_directory):
    '''Returns (rules file, its folder, the old rules file inside the plugin folder).'''
    data_root = _parent(_parent(script_directory))
    if data_root:
        folder = _join(data_root, DATAFOLDER, PLUGINFOLDER)
    else:
        folder = script_directory.rstrip('\\/')
    return _join(folder, RULESFILENAME), folder, _join(script_directory, RULESFILENAME)


def dupes_directory(rules_lines, default):
    '''The dump folder set in the rules file ("@ DUPESDIRECTORY <path>"), or default.

    The log file goes in that folder, so it has to be known before the rules
    are read properly. Quote a path that has spaces in it.'''
    from dmParser import Parse
    found = default
    for line in Parse(rules_lines):
        if line[2] == '@':
            words = line[3:]
        elif line[2][0] == '@':
            words = [line[2][1:]] + line[3:]
        else:
            continue
        if len(words) == 2 and words[0].lower() == 'dupesdirectory' and words[1].strip():
            found = words[1].strip()
    return found
