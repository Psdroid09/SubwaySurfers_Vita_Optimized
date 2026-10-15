import sys
import zipfile
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from audit_vpk import audit, sha256_file, unsafe_member
from repack_vpk import repack
from compare_fps import summarize


def test_unsafe_members():
    assert unsafe_member('../escape')
    assert unsafe_member('dir\\escape')
    assert unsafe_member('/root/path')
    assert not unsafe_member('Media/boot.config')


def test_audit_and_repack(tmp_path):
    original = tmp_path / 'original.vpk'
    with zipfile.ZipFile(original, 'w') as z:
        z.writestr('Media/boot.config', 'old=value\n')
    report = audit(original)
    assert report['zip_crc_ok']
    assert report['missing_core_files']
    replacement = tmp_path / 'change.txt'
    replacement.write_text('new=value\n', encoding='utf-8')
    output = tmp_path / 'updated.vpk'
    result = repack(original, output, {'Media/boot.config': replacement}, sha256_file(original))
    assert output.is_file()
    assert result['sha256'] == sha256_file(output)
    with zipfile.ZipFile(output) as z:
        assert z.read('Media/boot.config') == b'new=value\n'
    with zipfile.ZipFile(original) as z:
        assert z.read('Media/boot.config') == b'old=value\n'


def test_refuse_unverified_source(tmp_path):
    original = tmp_path / 'source.vpk'
    with zipfile.ZipFile(original, 'w') as z:
        z.writestr('eboot.bin', b'fake')
    repl = tmp_path / 'binary'; repl.write_bytes(b'new')
    with pytest.raises(ValueError, match='SHA-256'):
        repack(original, tmp_path/'out.vpk', {'eboot.bin': repl}, '0'*64)
    with pytest.raises(ValueError, match='--allow-code'):
        repack(original, tmp_path/'out.vpk', {'eboot.bin': repl}, sha256_file(original))


def test_compare_profiles():
    data = [{'profile':'normal','scene':'inicio','fps':'30'},
            {'profile':'normal','scene':'inicio','fps':'25'},
            {'profile':'oc','scene':'inicio','fps':'44'}]
    result = summarize(data)
    normal = next(r for r in result if r['profile']=='normal')
    assert normal['mean_fps'] == 27.5
    assert normal['below_30_pct'] == 50.0
