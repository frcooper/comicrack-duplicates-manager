"""Build the Duplicates Manager .crplugin into dist/ without installing it.

    python tools/build-plugin.py [--source DIR] [--version X.Y.Z]

--source packages another checkout (the release workflow uses it to rebuild an
older tag with this script). --version is the version the package must carry,
usually the release tag; the build refuses to package when Package.ini and
constants.py disagree with it or with each other.

dmrules.dat is not shipped: the demo rules turn on MOVEFILES and REMOVEFROMLIB,
and the script must only log until the user writes their own rules file.
Package.ini lists dmrules.dat under KeepFiles, so ComicRack keeps that file
across upgrades.
"""
from pathlib import Path
import argparse
import hashlib
import re
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
NAME = "DuplicatesManager"
# Everything ComicRack loads, plus the sample rules and the changelog.
PATTERNS = ("Package.ini", "*.py", "*.png", "dmrules.dat.demo", "changelog.txt")
# Source files that are not part of the plugin.
EXCLUDED = {"duplicatesmanager.xcf"}


def versions(source):
    ini = (source / "Package.ini").read_text(encoding="utf-8-sig")
    constants = (source / "constants.py").read_text(encoding="utf-8-sig")
    find = lambda pattern, text: (re.search(pattern, text, re.M) or [None, None])[1]
    return {
        "Package.ini": find(r"^Version\s*=\s*(\S+)", ini),
        "constants.py": find(r'^VERSION\s*=\s*"([^"]+)"', constants),
    }


def check_version(source, expected):
    found = versions(source)
    version = expected or found["Package.ini"]
    if not version or not re.fullmatch(r"\d+(?:\.\d+){1,2}(?:-[0-9A-Za-z.-]+)?", version):
        sys.exit("Not a release version: " + repr(version))
    wrong = {path: value for path, value in found.items() if value != version}
    if wrong:
        sys.exit("Version mismatch with " + version + ": " + repr(wrong))
    return version


def plugin_files(source):
    files = {path for pattern in PATTERNS for path in source.glob(pattern) if path.is_file()}
    return sorted(path for path in files if path.name not in EXCLUDED)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--source", type=Path, default=ROOT)
    parser.add_argument("--version", help="required version, e.g. the release tag without a leading v")
    args = parser.parse_args()
    source = args.source.resolve()

    version = check_version(source, args.version and args.version.lstrip("v"))
    files = plugin_files(source)
    for required in ("Package.ini", "duplicatesmanager.py", "constants.py"):
        if not (source / required).is_file():
            sys.exit("Missing " + required + " in " + str(source))

    destination = ROOT / "dist" / (NAME + "-" + version + ".crplugin")
    destination.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, path.name)
    print(destination)
    print("SHA256 " + hashlib.sha256(destination.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
