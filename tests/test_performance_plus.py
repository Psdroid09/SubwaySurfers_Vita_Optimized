import struct
import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from performance_plus import modify_globalgamemanagers, QUALITY_START, FILE_SIZE

def fixture():
    raw=bytearray(FILE_SIZE)
    p=QUALITY_START
    raw[p:p+16]=b'\0\0\0\0\1\0\0\0\4\0\0\0Good'
    raw[p+80:p+84]=bytes([0,1,0,0])
    for off,fmt,num in ((68,'<i',2),(88,'<f',.5),(96,'<i',32)):
        struct.pack_into(fmt,raw,p+off,num)
    return bytes(raw)

def test_valid_patch_keeps_other_bytes():
    base=fixture()
    data,changed=modify_globalgamemanagers(base)
    assert len(base)==len(data)
    assert len(changed)==2
    assert set(changed)=={QUALITY_START+81,QUALITY_START+96}
    assert data[QUALITY_START+81]==0
    assert struct.unpack_from('<i',data,QUALITY_START+96)[0]==16
    with pytest.raises(ValueError):
        modify_globalgamemanagers(data)

def test_wrong_quality_layout_is_rejected():
    raw=bytearray(fixture())
    raw[QUALITY_START+68]=0
    with pytest.raises(ValueError,match='textureQuality'):
        modify_globalgamemanagers(bytes(raw))

def test_wrong_file_size_is_rejected():
    with pytest.raises(ValueError,match='size'):
        modify_globalgamemanagers(b'invalid')
