"""Verifica los ocho procedimientos del informe a partir de sus datos y salidas."""
from pathlib import Path
import argparse
import hashlib
import json
import numpy as np
import pandas as pd

root=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--informe',action='store_true',help='Verifica la ejecución identificada en el Word.')
parser.add_argument('--comparar-informe',action='store_true',help='Contrasta métricas y sensibilidad con el respaldo del Word.')
args=parser.parse_args()
marker=root/'outputs'/('EJECUCION_DEL_INFORME.txt' if args.informe else 'ULTIMA_EJECUCION.txt')
out=root/'outputs'/marker.read_text().strip()
folds=pd.read_csv(out/'particiones_externas.csv')
inner=pd.read_csv(out/'particiones_internas.csv')
pred_all=pd.read_csv(out/'predicciones_externas.csv')
metrics_all=pd.read_csv(out/'metricas.csv')
# El respaldo de la ejecución citada conserva cálculos adicionales. El informe
# y el protocolo activo evalúan exclusivamente siete/seis atributos y B1/B2.
pred=pred_all[pred_all.entradas.isin([0,6,7])].copy()
metrics=metrics_all[metrics_all.entradas.isin([0,6,7])].copy()
if not args.informe:
    assert len(pred)==len(pred_all) and len(metrics)==len(metrics_all)
expected={(0,'referencia','B1'),(0,'referencia','B2')}
expected|={(n,s,f) for n,s in [(7,'con_e'),(6,'sin_e')] for f in ['lineal','arbol','knn']}
assert set(metrics[['entradas','escenario','modelo']].itertuples(index=False,name=None))==expected
assert len(folds)==120 and folds.ProjID.is_unique and folds['Organization id'].nunique()==42
assert folds.groupby('Organization id').bloque.nunique().eq(1).all()
assert folds.groupby('bloque').size().eq(24).all()
assert inner.externo.nunique()==5
for b,part in inner.groupby('externo'):
    assert len(part)==96 and part.ProjID.is_unique
    assert set(part.ProjID)==set(folds.loc[folds.bloque!=b,'ProjID'])
    assert part.groupby('Organization id').interno.nunique().eq(1).all()
    assert part.groupby('interno').size().eq(32).all()
assert len(pred)==960 and len(metrics)==8
assert not pred.duplicated(['entradas','escenario','modelo','ProjID']).any()

from seera_final import load_data, ID, ORG, Y, E, FEATURES_7
raw,data=load_data()
for r in metrics.itertuples(index=False):
    p=pred[(pred.entradas==r.entradas)&(pred.escenario==r.escenario)&(pred.modelo==r.modelo)]
    assert len(p)==120 and p.ProjID.is_unique
    aligned=data.set_index(ID).loc[p.ProjID]
    assert np.array_equal(p.y,aligned[Y])
    assert np.array_equal(p.organizacion,aligned[ORG])
    assert np.array_equal(p.bloque,folds.set_index(ID).loc[p.ProjID,'bloque'])
    errors=p.y-p.prediccion
    calculated=[abs(errors).mean(),np.sqrt((errors**2).mean()),1-(errors**2).sum()/((p.y-p.y.mean())**2).sum()]
    assert np.allclose(calculated,[r.MAE,r.RMSE,r.R2],rtol=1e-10,atol=1e-7)
    if r.modelo=='B1':assert np.array_equal(p.prediccion,aligned[E])
    if r.modelo=='B2':
        for b,g in p.groupby('bloque'):
            ids=folds.loc[folds.bloque!=b,ID]
            median=data.set_index(ID).loc[ids,Y].median()
            assert np.allclose(g.prediccion,median,rtol=0,atol=0)
audit=json.loads((out/'auditoria.json').read_text())
assert hashlib.sha256((root/'data/raw/SEERA cost estimation dataset.xlsx').read_bytes()).hexdigest()==audit['sha256_excel_ejecutado']

sens=pd.read_csv(out/'sensibilidad_atributos.csv')
rep=pd.read_csv(out/'sensibilidad_atributos_repeticiones.csv')
assert len(sens)==21 and len(rep)==630
assert not sens.duplicated(['modelo','atributo']).any()
assert not rep.duplicated(['modelo','atributo','repeticion']).any()
assert sens.groupby('modelo').atributo.apply(lambda x:set(x)==set(FEATURES_7)).all()
assert rep.groupby(['modelo','atributo']).size().eq(30).all()
for row in sens.itertuples():
    vals=rep[(rep.modelo==row.modelo)&(rep.atributo==row.atributo)]
    assert np.allclose(vals.delta_MAE,vals.MAE_permutado-vals.MAE_base)
    assert np.isclose(vals.delta_MAE.mean(),row.delta_MAE_media)
    expected_mae=metrics[(metrics.entradas==7)&(metrics.modelo==row.modelo)].MAE.iloc[0]
    assert np.isclose(row.MAE_base,expected_mae)

nb=json.loads((root/'Grupo1-TA-Experimentos.ipynb').read_text())
code=[c for c in nb['cells'] if c['cell_type']=='code']
assert len(code)==16 and all(c['execution_count'] is not None for c in code)
assert not any(o.get('output_type')=='error' for c in code for o in c['outputs'])
assert any('image/png' in o.get('data',{}) for c in code for o in c['outputs'])
if args.comparar_informe:
    report=root/'outputs'/(root/'outputs/EJECUCION_DEL_INFORME.txt').read_text().strip()
    reference=pd.read_csv(report/'metricas.csv')
    reference=reference[reference.entradas.isin([0,6,7])]
    keys=['entradas','escenario','modelo']
    a=metrics.sort_values(keys).reset_index(drop=True)
    b=reference.sort_values(keys).reset_index(drop=True)
    assert np.allclose(a[['MAE','RMSE','R2']],b[['MAE','RMSE','R2']],rtol=1e-10,atol=1e-7)
    reference_sens=pd.read_csv(report/'sensibilidad_atributos.csv')
    a=sens.sort_values(['modelo','atributo']).reset_index(drop=True)
    b=reference_sens.sort_values(['modelo','atributo']).reset_index(drop=True)
    assert np.allclose(a[['MAE_base','delta_MAE_media']],b[['MAE_base','delta_MAE_media']],rtol=1e-10,atol=1e-7)
    print('VERIFICADO: métricas y sensibilidad coinciden con el respaldo del informe.')
print('VERIFICADO: 120 proyectos; 42 organizaciones; reservas externas e internas íntegras.')
print('VERIFICADO: 960 predicciones; 8 filas de métricas recalculadas; referencias B1/B2 correctas.')
print('VERIFICADO: siete atributos, tres familias y 30 repeticiones por combinación de sensibilidad.')
print('VERIFICADO: huella del Excel y salidas ejecutadas de las 16 celdas del cuaderno.')
print('Ejecución verificada:',out.name)
