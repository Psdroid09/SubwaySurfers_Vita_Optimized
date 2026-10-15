#!/usr/bin/env python3
"""Safely apply explicitly supplied local file replacements to a VPK copy.

This is NOT an FPS patch: it makes content updates reproducible, verifiable and
reversible. It never modifies the input VPK in place.
"""
import argparse
import os
import sys
import tempfile
import zipfile
from pathlib import Path

try:
    from .audit_vpk import sha256_file, unsafe_member
except ImportError:
    from audit_vpk import sha256_file, unsafe_member

CODE_FILES = {'eboot.bin', 'Media/Modules/il2CppAssemblies.suprx'}


def repack(source, dest, replacements, expected_sha, allow_code=False):
    source = Path(source).resolve()
    dest = Path(dest).resolve()
    if source == dest:
        raise ValueError('Destination must differ from original VPK')
    actual_sha = sha256_file(source)
    if expected_sha.lower() != actual_sha.lower():
        raise ValueError('Source SHA-256 differs from --expected-sha (refusing to modify)')
    if not replacements:
        raise ValueError('At least one --replace is required')
    for name, filepath in replacements.items():
        if unsafe_member(name) or name.endswith('/'):
            raise ValueError('Invalid ZIP member name: ' + name)
        if (name in CODE_FILES or name.endswith('.suprx')) and not allow_code:
            raise ValueError('Compiled code replacement requires --allow-code: ' + name)
        if not Path(filepath).is_file():
            raise ValueError('Replacement missing: ' + str(filepath))
    dest.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.vpk-build-', suffix='.tmp', dir=dest.parent)
    os.close(fd)
    try:
        with zipfile.ZipFile(source, 'r') as zin:
            members = zin.infolist()
            names = [i.filename for i in members]
            if len(names) != len(set(names)) or any(unsafe_member(n) for n in names):
                raise ValueError('Archive has duplicate or unsafe members')
            unknown = set(replacements).difference(names)
            if unknown:
                raise ValueError('Cannot add new files without reviewing package structure: ' + repr(unknown))
            with zipfile.ZipFile(temporary, 'w', allowZip64=True) as zout:
                for item in members:
                    if item.filename in replacements:
                        payload = Path(replacements[item.filename]).read_bytes()
                    else:
                        payload = zin.read(item.filename)
                    zout.writestr(item, payload, compress_type=item.compress_type)
        with zipfile.ZipFile(temporary) as check:
            if check.testzip() is not None:
                raise ValueError('Output ZIP integrity check failed')
            if set(check.namelist()) != set(names):
                raise ValueError('Output has different member paths')
        os.replace(temporary, dest)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return {'output_path': str(dest), 'sha256': sha256_file(dest), 'replaced': sorted(replacements)}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('input_vpk')
    ap.add_argument('output_vpk')
    ap.add_argument('--expected-sha', required=True, help='SHA-256 of exact original VPK')
    ap.add_argument('--replace', action='append', metavar='ZIP_PATH=LOCAL_FILE', required=True)
    ap.add_argument('--allow-code', action='store_true', help='Explicitly allow binary executable replacement')
    args = ap.parse_args(argv)
    replacements = {}
    for entry in args.replace:
        if '=' not in entry:
            ap.error('Use --replace ZIP_PATH=LOCAL_FILE')
        name, path = entry.split('=', 1)
        if name in replacements:
            ap.error('Duplicate replacement path: ' + name)
        replacements[name] = path
    try:
        print(repack(args.input_vpk, args.output_vpk, replacements, args.expected_sha, args.allow_code))
    except (ValueError, OSError, zipfile.BadZipFile) as exc:
        ap.error(str(exc))
    return 0


if __name__ == '__main__':
    sys.exit(main())
