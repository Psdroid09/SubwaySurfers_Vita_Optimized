import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from fps_compare_v12 import analyze,to_markdown

def test_profiles_separated_and_stutter_metric():
    rows=[{'perfil':'Ultra','escena':'corriendo','fps':str(x)} for x in [40,31,29,20]]
    rows += [{'perfil':'Plus','escena':'corriendo','fps':'40'}]
    stats=analyze(rows)
    ultra=next(x for x in stats if x['perfil']=='Ultra')
    assert ultra['muestras']==4
    assert ultra['promedio']==30
    assert ultra['bajo30']==50
    assert '| Ultra |' in to_markdown(stats)

def test_invalid_values_rejected():
    for f in ['nan','-30','200','inf']:
        with pytest.raises(ValueError):
            analyze([{'perfil':'Plus','escena':'corriendo','fps':f}])

def test_missing_column_rejected():
    with pytest.raises(ValueError):
        analyze([{'perfil':'Ultra'}])
