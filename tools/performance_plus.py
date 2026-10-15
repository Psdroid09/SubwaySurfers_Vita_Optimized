#!/usr/bin/env python3
"""Parche Rendimiento Plus (experimental) para el port de Subway Surfers Vita.

Solo acepta el VPK Ultra Ligero pre2 verificado. No modifica ejecutables.
La mejora de FPS NO está comprobada; generar solo con archivos propios.
"""
import argparse
import hashlib
import json
import struct
import zipfile
from pathlib import Path

BASE_SHA = '322f95262b4fc9fcd9f3dcfdcaa3ba5a6a9296009b4f4907bf812e8866849c93'
MEMBER = 'Media/globalgamemanagers'
FILE_SIZE = 682224
QUALITY_START = 58112


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def modify_globalgamemanagers(raw):
    if len(raw) != FILE_SIZE:
        raise ValueError('Unsupported Unity asset size')
    p = QUALITY_START
    if raw[p:p+16] != b'\0\0\0\0\1\0\0\0\4\0\0\0Good':
        raise ValueError('Unknown QualitySettings layout')
    check = {
        'pixelLightCount': ('<i',16,0),
        'shadows': ('<i',20,0),
        'textureQuality': ('<i',68,2),
        'anisotropicTextures': ('<i',72,0),
        'antiAliasing': ('<i',76,0),
        'vSyncCount': ('<i',84,0),
        'lodBias': ('<f',88,0.5),
        'particleRaycastBudget': ('<i',96,32),
    }
    for key,(fmt,offset,expected) in check.items():
        got = struct.unpack_from(fmt, raw, p+offset)[0]
        if abs(got - expected) > 0.00001:
            raise ValueError(f'Unexpected {key}: {got}, expected {expected}')
    if raw[p+80:p+84] != bytes([0,1,0,0]):
        raise ValueError('Unexpected soft particle/vegetation/reflector/billboard flags')
    out = bytearray(raw)
    out[p+81] = 0  # softVegetation: desactivar pase extra si se usa
    struct.pack_into('<i',out,p+96,16)  # particle raycast budget: 32 -> 16
    changed = [i for i,(x,y) in enumerate(zip(raw,out)) if x!=y]
    if not changed or not set(changed).issubset({p+81,p+96,p+97,p+98,p+99}):
        raise AssertionError('Unintended QualitySettings bytes modified')
    return bytes(out),changed


def build(source,destination):
    source = Path(source).resolve()
    destination = Path(destination).resolve()
    if source == destination or destination.exists():
        raise ValueError('Use a new output file; original cannot be overwritten')
    if sha256_file(source) != BASE_SHA:
        raise ValueError('Input VPK does not match verified Ultra Ligero SHA-256')
    with zipfile.ZipFile(source,'r') as zin:
        names = zin.namelist()
        if zin.testzip() is not None or len(names) != 44 or len(names) != len(set(names)) or MEMBER not in names:
            raise ValueError('Original ZIP invalid or unexpected entries')
        updated,changed = modify_globalgamemanagers(zin.read(MEMBER))
        destination.parent.mkdir(parents=True,exist_ok=True)
        try:
            with zipfile.ZipFile(destination,'x') as zout:
                for member in zin.infolist():
                    data = updated if member.filename == MEMBER else zin.read(member.filename)
                    zout.writestr(member,data,compress_type=member.compress_type)
            with zipfile.ZipFile(destination) as znew:
                if znew.testzip() is not None or znew.namelist() != names:
                    raise ValueError('Output ZIP failed verification')
                for name in names:
                    if name != MEMBER and (znew.getinfo(name).CRC != zin.getinfo(name).CRC or znew.getinfo(name).file_size != zin.getinfo(name).file_size):
                        raise ValueError(f'Unexpected modification of {name}')
                if znew.read(MEMBER) != updated:
                    raise ValueError('Settings payload mismatch')
        except Exception:
            destination.unlink(missing_ok=True)
            raise
    return dict(mode='Rendimiento Plus experimental',input_sha256=BASE_SHA,
                output_sha256=sha256_file(destination),changed_file=MEMBER,
                changed_byte_offsets=changed,
                changes={'softVegetation':{'old':1,'new':0},
                         'particleRaycastBudget':{'old':32,'new':16}},
                fps_measured=False,vita_hardware_tested=False,
                warning='No demonstrated FPS increase; may alter vegetation shading or particle collisions')


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('ultraligero_vpk',type=Path)
    ap.add_argument('output_vpk',type=Path)
    ap.add_argument('--report',type=Path)
    args=ap.parse_args()
    try:
        result=build(args.ultraligero_vpk,args.output_vpk)
    except (ValueError,OSError,zipfile.BadZipFile) as exc:
        ap.error(str(exc))
    txt=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    print(txt)
    if args.report:
        args.report.write_text(txt,encoding='utf-8')


if __name__=='__main__':
    main()
