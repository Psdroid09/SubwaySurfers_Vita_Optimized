#!/usr/bin/env python3
"""Parche experimental para la calidad de Unity 2018.2 en Subway Surfers Vita.

NO es una mejora de FPS comprobada; no distribuir el VPK completo.
Requiere exactamente el VPK original auditado y nunca lo sobrescribe.
"""
import argparse
import hashlib
import json
import struct
import sys
import zipfile
from pathlib import Path

SOURCE_SHA256 = "d6c330b020b960b0c2c79afafa762a1a04eb8013f081a41f380dd38b513dbb7d"
QUALITY_FILE = "Media/globalgamemanagers"
FIELDS = {
    "texture_quality": (68, "<i"),
    "anisotropic_textures": (72, "<i"),
    "anti_aliasing": (76, "<i"),
    "v_sync_count": (84, "<i"),
    "lod_bias": (88, "<f"),
    "particle_raycast_budget": (96, "<i"),
}
EXPECTED = dict(texture_quality=0, anisotropic_textures=1, anti_aliasing=0,
                v_sync_count=0, lod_bias=1.0, particle_raycast_budget=256)
MODES = {
    "equilibrado": dict(texture_quality=0, anisotropic_textures=0,
                       lod_bias=0.8, particle_raycast_budget=128),
    "ligero": dict(texture_quality=1, anisotropic_textures=0,
                  lod_bias=0.7, particle_raycast_budget=64),
}


def sha256_path(path):
    hashobj = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            hashobj.update(chunk)
    return hashobj.hexdigest()


def find_quality_profile(data):
    """Read Unity SerializedFile v17 objects and find ClassID=47 QualitySettings."""
    if len(data) < 500 or struct.unpack_from(">I", data, 8)[0] != 17:
        raise ValueError("Unsupported Unity serialized file format")
    file_size = struct.unpack_from(">I", data, 4)[0]
    data_offset = struct.unpack_from(">I", data, 12)[0]
    if file_size != len(data) or data_offset > file_size or data[16] != 0:
        raise ValueError("Invalid serialized file header/endian")
    pos = 20
    end = data.find(b"\0", pos, 100)
    if end < 0 or data[pos:end] != b"2018.2.19f1":
        raise ValueError("Unsupported Unity version")
    pos = end + 1
    platform = struct.unpack_from("<i", data, pos)[0]
    pos += 4
    has_tree = data[pos]
    pos += 1
    count = struct.unpack_from("<i", data, pos)[0]
    pos += 4
    if platform != 30 or has_tree != 0 or not 1 <= count <= 100:
        raise ValueError("Unexpected PSP2 asset metadata")
    types = []
    for _ in range(count):
        class_id, _stripped, _script_idx = struct.unpack_from("<ibh", data, pos)
        pos += 7
        if class_id == 114:
            pos += 16  # Script ID
        pos += 16  # Unity hash
        types.append(class_id)
    object_count = struct.unpack_from("<i", data, pos)[0]
    pos += 4
    if not 1 <= object_count <= 10000:
        raise ValueError("Invalid object count")
    matches = []
    for _ in range(object_count):
        pos += -pos % 4
        _path_id, relative, size, type_idx = struct.unpack_from("<qIII", data, pos)
        pos += 20
        if type_idx >= len(types):
            raise ValueError("Invalid class index")
        if types[type_idx] == 47:
            start = data_offset + relative
            if start + size > file_size:
                raise ValueError("QualitySettings extends beyond file")
            matches.append((start, size))
    if len(matches) != 1 or matches[0][1] != 136:
        raise ValueError("Unexpected QualitySettings layout")
    start = matches[0][0]
    if data[start:start+16] != b"\0\0\0\0\1\0\0\0\4\0\0\0Good":
        raise ValueError("Expected original Good quality profile")
    return start


def read_settings(data):
    start = find_quality_profile(data)
    return {name: struct.unpack_from(fmt, data, start+relative)[0]
            for name, (relative, fmt) in FIELDS.items()}


def patch_settings(data, mode="ligero"):
    if mode not in MODES:
        raise ValueError("Unrecognized mode")
    original = read_settings(data)
    for name, expected in EXPECTED.items():
        if abs(original[name] - expected) > 0.00001:
            raise ValueError("Original %s unexpectedly equals %r (expected %r)" %
                             (name, original[name], expected))
    start = find_quality_profile(data)
    result = bytearray(data)
    for name, value in MODES[mode].items():
        relative, fmt = FIELDS[name]
        struct.pack_into(fmt, result, start+relative, value)
    result = bytes(result)
    settings = read_settings(result)
    for name, value in MODES[mode].items():
        if abs(settings[name] - value) > 0.00001:
            raise ValueError("Patch verification failed")
    changed = [i for i, (a, b) in enumerate(zip(data, result)) if a != b]
    allowed = {start+relative+n for name in MODES[mode]
               for relative, fmt in [FIELDS[name]] for n in range(struct.calcsize(fmt))}
    if not changed or not set(changed).issubset(allowed):
        raise ValueError("Unexpected bytes changed")
    return result, {name: {"antes": original[name], "despues": value}
                    for name, value in MODES[mode].items()}, changed


def build_patch(source, destination, mode="ligero"):
    src, out = Path(source).resolve(), Path(destination).resolve()
    if src == out or out.exists():
        raise ValueError("Output must be new and different from original")
    if sha256_path(src) != SOURCE_SHA256:
        raise ValueError("This VPK is not the audited original; SHA-256 mismatch")
    with zipfile.ZipFile(src) as zin:
        if zin.testzip() is not None:
            raise ValueError("Original ZIP CRC error")
        names = zin.namelist()
        if len(names) != len(set(names)) or QUALITY_FILE not in names:
            raise ValueError("Invalid original ZIP member list")
        quality, changes, offsets = patch_settings(zin.read(QUALITY_FILE), mode)
        out.parent.mkdir(parents=True, exist_ok=True)
        try:
            with zipfile.ZipFile(out, "x", allowZip64=True) as zout:
                for info in zin.infolist():
                    payload = quality if info.filename == QUALITY_FILE else zin.read(info.filename)
                    zout.writestr(info, payload)
            with zipfile.ZipFile(out) as generated:
                if generated.testzip() is not None or generated.namelist() != names:
                    raise ValueError("Generated VPK integrity failure")
                if generated.read(QUALITY_FILE) != quality:
                    raise ValueError("Quality file was not written correctly")
                for name in names:
                    if name != QUALITY_FILE and generated.getinfo(name).CRC != zin.getinfo(name).CRC:
                        raise ValueError("Unexpected change in " + name)
        except Exception:
            out.unlink(missing_ok=True)
            raise
    return dict(modo=mode, salida=str(out), salida_sha256=sha256_path(out),
                archivo_modificado=QUALITY_FILE, num_bytes_cambiados=len(offsets),
                parametros=changes,
                advertencia="Solo probado como archivo ZIP; NO probado en PS Vita.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("vpk_original")
    parser.add_argument("vpk_salida")
    parser.add_argument("--modo", choices=list(MODES), default="ligero")
    parser.add_argument("--reporte", help="Path to JSON report")
    args = parser.parse_args()
    try:
        report = build_patch(args.vpk_original, args.vpk_salida, args.modo)
    except (ValueError, OSError, zipfile.BadZipFile) as exc:
        parser.error(str(exc))
    report = json.dumps(report, indent=2, ensure_ascii=False)
    print(report)
    if args.reporte:
        Path(args.reporte).write_text(report + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
