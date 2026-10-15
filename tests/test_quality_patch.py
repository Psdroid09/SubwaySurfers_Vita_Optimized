"""Synthetic fixtures: no protected game bytes in this repository."""
import struct
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from quality_patch import FIELDS, EXPECTED, MODES, find_quality_profile, patch_settings, read_settings


def fake_unity_file():
    quality = bytearray(136)
    quality[:16] = b"\0\0\0\0\1\0\0\0\4\0\0\0Good"
    for name, value in EXPECTED.items():
        offset, fmt = FIELDS[name]
        struct.pack_into(fmt, quality, offset, value)
    meta = bytearray(b"2018.2.19f1\0")
    meta += struct.pack("<iBi", 30, 0, 1)
    meta += struct.pack("<ibh", 47, 0, -1) + bytes(16)
    meta += struct.pack("<i", 1)
    meta += bytes(-len(meta) % 4)
    meta += struct.pack("<qIII", 1, 0, 136, 0)
    data = bytearray(4096+136)
    struct.pack_into(">IIII", data, 0, len(meta)+20, len(data), 17, 4096)
    data[20:20+len(meta)] = meta
    data[4096:] = quality
    return bytes(data)


def test_quality_location():
    data = fake_unity_file()
    assert find_quality_profile(data) == 4096
    assert read_settings(data) == EXPECTED


@pytest.mark.parametrize("mode", ["equilibrado", "ligero"])
def test_quality_patch(mode):
    data = fake_unity_file()
    modified, change_log, changed = patch_settings(data, mode)
    assert 0 < len(changed) < 15 and len(data) == len(modified)
    assert change_log["texture_quality"]["antes"] == 0
    assert read_settings(modified)["v_sync_count"] == 0
    assert read_settings(modified)["anti_aliasing"] == 0
    for field, value in MODES[mode].items():
        assert abs(read_settings(modified)[field]-value) < 0.00001
    with pytest.raises(ValueError):
        patch_settings(modified, mode)


def test_unknown_engine_refused():
    with pytest.raises(ValueError, match="Unity version"):
        patch_settings(fake_unity_file().replace(b"2018.2.19f1", b"2020.2.19f1", 1))


def test_unsupported_settings_refused():
    data = bytearray(fake_unity_file())
    struct.pack_into("<i", data, 4096+FIELDS["texture_quality"][0], 3)
    with pytest.raises(ValueError, match="texture_quality"):
        patch_settings(bytes(data))
