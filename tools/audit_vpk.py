#!/usr/bin/env python3
"""Static, read-only audit of a Vita .vpk (ZIP). Python 3.9+, no dependencies."""
import argparse
import hashlib
import json
import re
import struct
import sys
import zipfile
from collections import Counter
from pathlib import Path, PurePosixPath


def parse_sfo(data):
    """Parse the standard PSF/SFO index, returning string/integer fields."""
    if len(data) < 20 or data[:4] != b'\0PSF':
        raise ValueError('SFO header missing/invalid')
    _, version, keytable, valtable, num = struct.unpack_from('<5I', data)
    if num > 1024 or 20 + 16 * num > len(data):
        raise ValueError('SFO index out of range')
    fields = {}
    for i in range(num):
        ko, fmt, length, maxlen, vo = struct.unpack_from('<HHIII', data, 20 + i * 16)
        kstart = keytable + ko
        if kstart >= len(data):
            raise ValueError('SFO key out of range')
        kend = data.find(b'\0', kstart)
        if kend < 0:
            raise ValueError('Unterminated SFO key')
        key = data[kstart:kend].decode('utf-8', errors='replace')
        value = data[valtable + vo:valtable + vo + length]
        if len(value) != length:
            raise ValueError('SFO value out of range')
        if fmt == 0x204:
            fields[key] = value.rstrip(b'\0').decode('utf-8', errors='replace')
        elif fmt == 0x404 and length == 4:
            fields[key] = struct.unpack('<I', value)[0]
    return fields


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as fp:
        for chunk in iter(lambda: fp.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def unsafe_member(name):
    if not name or '\\' in name or name.startswith('/'):
        return True
    parts = PurePosixPath(name).parts
    return '..' in parts or '.' in parts or ':' in name


def audit(path, check_crc=True):
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(path)
    report = {'filename': path.name, 'archive_bytes': path.stat().st_size,
              'sha256': sha256_file(path), 'problems': []}
    with zipfile.ZipFile(path) as z:
        entries = z.infolist()
        names = [item.filename for item in entries]
        duplicates = [name for name, count in Counter(names).items() if count > 1]
        unsafe = sorted(set(filter(unsafe_member, names)))
        encrypted = [item.filename for item in entries if item.flag_bits & 1]
        if duplicates: report['problems'].append('Duplicate ZIP members: ' + ', '.join(duplicates[:10]))
        if unsafe: report['problems'].append('Unsafe member paths: ' + ', '.join(unsafe[:10]))
        if encrypted: report['problems'].append('Encrypted members: ' + ', '.join(encrypted[:10]))
        report['entries'] = len(entries)
        report['uncompressed_bytes'] = sum(i.file_size for i in entries)
        report['compressed_bytes'] = sum(i.compress_size for i in entries)
        report['compression_methods'] = dict(Counter(str(i.compress_type) for i in entries))
        required = ['eboot.bin', 'sce_sys/param.sfo', 'Media/globalgamemanagers',
                    'Media/Modules/il2CppAssemblies.suprx']
        report['missing_core_files'] = [p for p in required if p not in names]
        if report['missing_core_files']:
            report['problems'].append('Missing core files: ' + ', '.join(report['missing_core_files']))
        if 'sce_sys/param.sfo' in names:
            try:
                sfo = parse_sfo(z.read('sce_sys/param.sfo'))
                report['title_id'] = sfo.get('TITLE_ID', 'unknown')
                report['title'] = sfo.get('TITLE', 'unknown')
                report['app_version'] = sfo.get('APP_VER', 'unknown')
            except (ValueError, struct.error, RuntimeError) as exc:
                report['problems'].append('SFO: ' + str(exc))
        if 'Media/globalgamemanagers' in names:
            try:
                head = z.open('Media/globalgamemanagers').read(2048)
                versions = re.findall(rb'\b20\d\d\.\d{1,2}\.\d{1,2}[a-z]\d+\b', head)
                report['unity_version'] = versions[0].decode('ascii') if versions else 'unknown'
            except Exception as exc:
                report['problems'].append('Unity header: ' + str(exc))
        if check_crc:
            bad = z.testzip()
            report['zip_crc_ok'] = bad is None
            if bad is not None:
                report['problems'].append('CRC failed for: ' + bad)
        else:
            report['zip_crc_ok'] = None
    report['ok'] = len(report['problems']) == 0
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('vpk', help='Path to local VPK; never uploaded by this script')
    parser.add_argument('--json', dest='json_path', help='Write audit JSON to a specified file')
    parser.add_argument('--skip-crc', action='store_true', help='Faster scan, does not check ZIP payloads')
    args = parser.parse_args(argv)
    try:
        report = audit(args.vpk, check_crc=not args.skip_crc)
    except (OSError, ValueError, zipfile.BadZipFile, RuntimeError) as exc:
        parser.error(str(exc))
    output = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
    print(output, end='')
    if args.json_path:
        Path(args.json_path).write_text(output, encoding='utf-8')
    return 0 if report['ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
