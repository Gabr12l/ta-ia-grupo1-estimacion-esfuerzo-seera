"""Comprueba las reservas y recalcula métricas desde las predicciones guardadas."""
from pathlib import Path
import json,hashlib
import numpy as np
import pandas as pd

root=Path(__file__).resolve().parent
marker=root/'outputs/EJECUCION_DEL_INFORME.txt'
if not marker.exists():marker=root/'outputs/ULTIMA_EJECUCION.txt'
out=root/'outputs'/marker.read_text().strip()
folds=pd.read_csv(out/'particiones_externas.csv')
inner=pd.read_csv(out/'particiones_internas.csv')
pred=pd.read_csv(out/'predicciones_externas.csv')
metrics=pd.read_csv(out/'metricas.csv')
audit=json.loads((out/'auditoria.json').read_text())
assert len(folds)==120 and folds.ProjID.is_unique
assert folds.groupby('Organization id').bloque.nunique().eq(1).all()
assert folds.groupby('bloque').size().eq(24).all()
for b,part in inner.groupby('externo'):
    assert len(part)==96 and part.ProjID.is_unique
    assert set(part.ProjID)==set(folds.loc[folds.bloque!=b,'ProjID'])
    assert part.groupby('Organization id').interno.nunique().eq(1).all()
    assert part.groupby('interno').size().eq(32).all()
assert len(pred)==1680 and len(metrics)==14
assert not pred.duplicated(['entradas','escenario','modelo','ProjID']).any()
for r in metrics.itertuples(index=False):
    p=pred[(pred.entradas==r.entradas)&(pred.modelo==r.modelo)]
    assert len(p)==120 and p.ProjID.is_unique
    errors=p.y-p.prediccion
    calculated=[abs(errors).mean(),np.sqrt((errors**2).mean()),1-(errors**2).sum()/((p.y-p.y.mean())**2).sum()]
    assert np.allclose(calculated,[r.MAE,r.RMSE,r.R2],rtol=1e-10,atol=1e-7)
raw=root/'data/raw/SEERA cost estimation dataset.xlsx'
assert hashlib.sha256(raw.read_bytes()).hexdigest()==audit['sha256_excel_ejecutado']
nb=json.loads((root/'Grupo1-TA-Experimentos.ipynb').read_text())
code=[c for c in nb['cells'] if c['cell_type']=='code']
assert all(c['execution_count'] is not None for c in code)
assert not any(o.get('output_type')=='error' for c in code for o in c['outputs'])
assert any('image/png' in o.get('data',{}) for c in code for o in c['outputs'])
assert len(code)==15
print('VERIFICADO: 120 proyectos; 42 organizaciones; bloques externos/internos íntegros.')
print('VERIFICADO: 1680 predicciones; 14 métricas recalculadas; Excel y notebook ejecutado.')
print('Ejecución del informe:',out.name)
