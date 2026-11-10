"""Experimento final reproducible de 3 y 7 entradas en SEERA 1.3.

Selección por contenido y auditoría de entradas, no por correlaciones con y.
No busca un subconjunto óptimo mirando las reservas externas.
"""
from pathlib import Path
from itertools import product
import hashlib
import json
import platform
import time
import numpy as np
import pandas as pd
import sklearn
from sklearn.tree import DecisionTreeRegressor

ROOT = Path(__file__).resolve().parent
RAW = ROOT / 'data/raw/SEERA cost estimation dataset.xlsx'
ID, ORG, Y, E = 'ProjID', 'Organization id', 'Actual effort', 'Estimated effort'
TYPE, DOMAIN, METHOD = 'Development type', 'Application domain', 'Methodology'
SIZE, COMPLEXITY = 'Object points', 'Product complexity'
EXPERIENCE = 'Programmers experience in programming language'
SHA256 = 'e4d22e7e8f9f7e2452f8e97500082e3c1ec7c7c087a7ad70a191c3c5fe79f225'
CODES = {TYPE: [1,2,3,4], DOMAIN: [1,2,3,5,6,7], METHOD: [1,2,3,4,6,7]}
NEW = [SIZE, COMPLEXITY, EXPERIENCE, METHOD]
FEATURES_7 = [TYPE, DOMAIN, E] + NEW
SELECTION = {
    'entradas_principal': FEATURES_7,
    'entradas_complementario': [c for c in FEATURES_7 if c != E],
    'criterio': 'Cobertura de tamaño, dificultad, experiencia técnica y proceso; verificación del diccionario y ausencias. No selección por y.',
    'no_optimo_estadistico_demostrado': True,
    'codificacion_ordinal': {COMPLEXITY:'1 a 4, dificultad creciente', EXPERIENCE:'1 a 5, experiencia decreciente; códigos, no años'},
    'limitacion_ordinal': 'Se usan puntuaciones ordinales; la separación uniforme entre niveles es un supuesto, no una medida física. Evaluar codificación nominal como sensibilidad futura.',
    'K':5, 'K_interno':3, 'semilla_arbol':2026,
}
GRIDS = {
    'lineal':[{}],
    'arbol':[dict(max_depth=d,min_samples_leaf=l) for d,l in product([2,3,4,5,None],[2,5,10])],
    'knn':[dict(q=q,weights=w) for q,w in product([3,5,7,9],['uniform','distance'])],
}

def load_data(path=None, strict=True):
    path=Path(path or RAW)
    if not path.is_file():
        raise FileNotFoundError(f"No se encontró el Excel: {path.resolve()}")
    if strict and hashlib.sha256(path.read_bytes()).hexdigest()!=SHA256:
        raise ValueError("El Excel difiere de la fuente del informe. Revise el archivo o desactive strict conscientemente.")
    raw = pd.read_excel(path, sheet_name='SEERA dataset', header=1, keep_default_na=False)
    raw.columns = raw.columns.str.strip()
    data = raw[[ID,ORG,Y]+FEATURES_7].apply(pd.to_numeric, errors='coerce')
    assert data[ID].is_unique and data[ID].notna().all()
    if strict: assert len(data)==120 and data[ORG].nunique()==42
    for c in [SIZE, COMPLEXITY, EXPERIENCE]:
        invalid=data[c].isna() & ~raw[c].isin(['?', ''])
        if invalid.any(): raise ValueError(f"Valor no numérico no reconocido en {c}")
    assert data[[ID,ORG,Y,E,TYPE,DOMAIN,METHOD]].notna().all().all()
    assert (data[Y]>0).all() and (data[E]>=0).all()
    for c,levels in CODES.items(): assert data[c].isin(levels).all()
    for c,levels in [(COMPLEXITY,[1,2,3,4]),(EXPERIENCE,[1,2,3,4,5])]:
        assert data[c].dropna().isin(levels).all()
    assert (data[SIZE].dropna()>=0).all()
    return raw, data.sort_values(ID).reset_index(drop=True)

def blocks(data,k):
    sizes=data.groupby(ORG).size().reset_index(name='n').sort_values(['n',ORG],ascending=[False,True])
    loads=[0]*k; mapping={}
    for o,n in sizes.itertuples(index=False,name=None):
        b=min(range(k),key=lambda j:(loads[j],j)); mapping[o]=b; loads[b]+=n
    b=data[ORG].map(mapping).to_numpy()
    splits=[]
    for j in range(k):
        tr,te=np.flatnonzero(b!=j),np.flatnonzero(b==j)
        assert len(tr) and len(te) and set(data.iloc[tr][ORG]).isdisjoint(data.iloc[te][ORG])
        splits.append((tr,te))
    return splits,b

class Preparation:
    def fit(self,data,family,pack,with_e):
        self.family,self.pack,self.with_e=family,pack,with_e
        self.cat=[TYPE,DOMAIN]+([METHOD] if pack==7 else [])
        self.newnum=[SIZE,COMPLEXITY,EXPERIENCE] if pack==7 else []
        self.num=([E] if with_e else [])+self.newnum
        self.fill={}
        for c in self.newnum:
            observed=data[c].dropna()
            assert len(observed)>0
            self.fill[c]=float(observed.median() if c==SIZE else observed.mode().min())
        self.means={c:float(data[c].fillna(self.fill.get(c,0)).mean()) for c in self.num}
        self.stds={c:float(data[c].fillna(self.fill.get(c,0)).std(ddof=0)) for c in self.num}
        self.names=[f'{c}={v}' for c in self.cat for v in CODES[c] if not(family=='lineal' and v==1)]
        self.names+=self.num+[f'{c}:ausente' for c in self.newnum]
        self.seen={c:sorted(data[c].unique().tolist()) for c in self.cat}
        return self

    def transform(self,data):
        parts=[]
        for c in self.cat:
            assert data[c].isin(CODES[c]).all()
            parts.extend((data[c].to_numpy()==v).astype(float) for v in CODES[c] if not(self.family=='lineal' and v==1))
        for c in self.num:
            vals=data[c].fillna(self.fill.get(c,0)).to_numpy(float)
            if self.family=='knn':
                sd=self.stds[c]; vals=(vals-self.means[c])/sd if sd>0 else np.zeros(len(vals))
            parts.append(vals)
        parts.extend(data[c].isna().to_numpy(float) for c in self.newnum)
        out=np.column_stack(parts)
        assert np.isfinite(out).all() and out.shape[1]==len(self.names)
        return out

def fit_predict(train,test,family,pack,with_e,params):
    prep=Preparation().fit(train,family,pack,with_e)
    x,z=prep.transform(train),prep.transform(test)
    y=train[Y].to_numpy(float)
    if family=='lineal':
        beta,_,rank,_=np.linalg.lstsq(np.column_stack([np.ones(len(x)),x]),y,rcond=None)
        pred=np.column_stack([np.ones(len(z)),z])@beta
    elif family=='arbol':
        model=DecisionTreeRegressor(criterion='squared_error',random_state=2026,**params).fit(x,y)
        pred=model.predict(z); rank=None
    else:
        assert params['q']<=len(train)
        ids=train[ID].to_numpy(int); pred=[]
        for row in z:
            d=np.sqrt(((x-row)**2).sum(axis=1))
            chosen=np.lexsort((ids,d))[:params['q']]
            ds,ys=d[chosen],y[chosen]
            if (ds==0).any(): val=ys[ds==0].mean()
            elif params['weights']=='uniform': val=ys.mean()
            else: val=np.average(ys,weights=1/ds)
            pred.append(val)
        pred=np.asarray(pred); rank=None
    assert np.isfinite(pred).all()
    return np.maximum(0,pred), {'columnas_transformadas':len(prep.names),'rango_lineal':int(rank) if rank is not None else None,
        'imputacion':prep.fill,'medias':prep.means,'desviaciones':prep.stds,
        'categorias_validas_no_vistas':{c:sorted(set(test[c])-set(prep.seen[c])) for c in prep.cat}}

def tie(family,p):
    if family=='arbol': return (float('inf') if p['max_depth'] is None else p['max_depth'],-p['min_samples_leaf'])
    if family=='knn': return (-p['q'],0 if p['weights']=='uniform' else 1)
    return (0,)

def metrics(y,p):
    y,p=np.asarray(y,float),np.asarray(p,float)
    den=((y-y.mean())**2).sum()
    return dict(MAE=float(np.abs(y-p).mean()),RMSE=float(np.sqrt(((y-p)**2).mean())),R2=float(1-((y-p)**2).sum()/den) if den else None)

def run(data,out=None):
    out=Path(out or ROOT/'outputs'); out.mkdir(exist_ok=True,parents=True)
    # Se fija la ampliación antes de calcular resultados.
    (out/'seleccion_predefinida.json').write_text(json.dumps(SELECTION,ensure_ascii=False,indent=2))
    start=time.perf_counter(); outer,labels=blocks(data,5)
    data[[ID,ORG]].assign(bloque=labels+1).to_csv(out/'particiones_externas.csv',index=False)
    preds=[]; logs=[]; inner_records=[]
    for b,(ri,ti) in enumerate(outer,1):
        train,test=data.iloc[ri].reset_index(drop=True),data.iloc[ti].reset_index(drop=True)
        inner,ilabels=blocks(train,3)
        inner_records.append(train[[ID,ORG]].assign(externo=b,interno=ilabels+1))
        for model,values in [('B1',test[E].to_numpy()),('B2',np.full(len(test),train[Y].median()))]:
            for j,p in enumerate(values):
                preds.append(dict(ProjID=int(test.iloc[j][ID]),organizacion=int(test.iloc[j][ORG]),bloque=b,entradas=0,escenario='referencia',modelo=model,y=float(test.iloc[j][Y]),prediccion=float(p)))
        for pack,with_e,family in product([3,7],[True,False],['lineal','arbol','knn']):
            model_start=time.perf_counter()
            candidates=[]
            for params in GRIDS[family]:
                errors=[]
                for a,v in inner:
                    p,_=fit_predict(train.iloc[a],train.iloc[v],family,pack,with_e,params)
                    errors.extend(np.abs(train.iloc[v][Y].to_numpy()-p))
                candidates.append((float(np.mean(errors)),params))
            score,params=min(candidates,key=lambda t:(t[0],tie(family,t[1])))
            p,diagnostics=fit_predict(train,test,family,pack,with_e,params)
            logs.append(dict(bloque=b,entradas=pack if with_e else pack-1,paquete=pack,con_e=with_e,modelo=family,
                             MAE_interno=score,parametros=params,segundos=time.perf_counter()-model_start,candidatos=[{'MAE_interno':s,'parametros':q} for s,q in candidates],**diagnostics))
            for j,value in enumerate(p):
                preds.append(dict(ProjID=int(test.iloc[j][ID]),organizacion=int(test.iloc[j][ORG]),bloque=b,entradas=pack if with_e else pack-1,
                    escenario='con_e' if with_e else 'sin_e',modelo=family,y=float(test.iloc[j][Y]),prediccion=float(value)))
        print(f'Bloque {b}/5 completado',flush=True)
    pred=pd.DataFrame(preds)
    pred['error_absoluto']=(pred.y-pred.prediccion).abs()
    rows=[]; foldrows=[]
    for (n,s,f),g in pred.groupby(['entradas','escenario','modelo'],sort=False):
        assert len(g)==len(data) and g.ProjID.is_unique
        rows.append(dict(entradas=n,escenario=s,modelo=f,**metrics(g.y,g.prediccion)))
        for b,h in g.groupby('bloque'):
            foldrows.append(dict(entradas=n,escenario=s,modelo=f,bloque=int(b),**metrics(h.y,h.prediccion)))
    summary=pd.DataFrame(rows)
    pred.to_csv(out/'predicciones_externas.csv',index=False)
    summary.to_csv(out/'metricas.csv',index=False)
    pd.DataFrame(foldrows).to_csv(out/'metricas_por_bloque.csv',index=False)
    pd.concat(inner_records).to_csv(out/'particiones_internas.csv',index=False)
    (out/'configuraciones.json').write_text(json.dumps(logs,ensure_ascii=False,indent=2))
    audit={'filas':len(data),'organizaciones':int(data[ORG].nunique()),'sha256_fuente_publicada':SHA256,
        'ausencias':{c:int(data[c].isna().sum()) for c in NEW},'proyectos_con_ausencias':int(data[NEW].isna().any(axis=1).sum()),
        'dimension_nominal_bruta':7,'variables_finales_no_es_optimo_garantizado':True,
        'plataforma':platform.platform(),'procesador':platform.processor(),'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,'sklearn':sklearn.__version__,
        'segundos':time.perf_counter()-start,'errores':0,
        'interpretacion':'Evaluación descriptiva retrospectiva. La ampliación fue fijada por contenido; no demuestra que sea el subconjunto óptimo ni utilidad temprana.'}
    (out/'auditoria.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2))
    return summary,pred,audit


def fit_saved(data, family, pack, with_e, params):
    """Ajusta un predictor. Guarda preparación y parámetros, sin evaluar en entrenamiento."""
    prep=Preparation().fit(data, family, pack, with_e)
    x=prep.transform(data)
    y=data[Y].to_numpy(float)
    payload={'family':family,'pack':pack,'with_e':with_e,'params':params,
             'preparation':prep.__dict__,'n_train':len(data)}
    if family=='lineal':
        beta,_,rank,_=np.linalg.lstsq(np.column_stack([np.ones(len(x)),x]),y,rcond=None)
        payload.update(beta=beta,rank=int(rank))
    elif family=='arbol':
        payload['tree']=DecisionTreeRegressor(criterion='squared_error',random_state=2026,**params).fit(x,y)
    else:
        payload.update(x_train=x,y_train=y,ids_train=data[ID].to_numpy(int))
    return payload

def predict_saved(payload, data):
    prep=Preparation()
    prep.__dict__.update(payload['preparation'])
    z=prep.transform(data)
    if payload['family']=='lineal':
        pred=np.column_stack([np.ones(len(z)),z])@payload['beta']
    elif payload['family']=='arbol':
        pred=payload['tree'].predict(z)
    else:
        pred=[]
        for row in z:
            ds=np.sqrt(((payload['x_train']-row)**2).sum(axis=1))
            chosen=np.lexsort((payload['ids_train'],ds))[:payload['params']['q']]
            d,y=ds[chosen],payload['y_train'][chosen]
            value=y[d==0].mean() if (d==0).any() else (
                y.mean() if payload['params']['weights']=='uniform' else np.average(y,weights=1/d))
            pred.append(value)
        pred=np.array(pred)
    assert np.isfinite(pred).all()
    return np.maximum(0,pred)

def select_and_refit(data, summary, out):
    """La selección de familia usa los MAE externos: su optimismo se declara en el informe."""
    ranking=summary.query("entradas==7 and escenario=='con_e'").copy()
    ranking['orden']=ranking.modelo.map({'lineal':0,'arbol':1,'knn':2})
    family=ranking.sort_values(['MAE','orden']).iloc[0].modelo
    inner,labels=blocks(data,3)
    candidates=[]
    for params in GRIDS[family]:
        errors=[]
        for tr,te in inner:
            p,_=fit_predict(data.iloc[tr],data.iloc[te],family,7,True,params)
            errors.extend(np.abs(data.iloc[te][Y].to_numpy()-p))
        candidates.append((float(np.mean(errors)),params))
    score,params=min(candidates,key=lambda t:(t[0],tie(family,t[1])))
    payload=fit_saved(data,family,7,True,params)
    import joblib
    joblib.dump(payload,Path(out)/'modelo_ampliado.joblib')
    meta={'familia':family,'entradas':FEATURES_7,'n_entrenamiento':len(data),
          'parametros':params,'MAE_seleccion_interna_reajuste':score,
          'advertencia':'El MAE interno del reajuste no es una nueva prueba externa. La familia se eligió mirando resultados externos.'}
    if family=='lineal':
        portable={**meta,'preparacion':payload['preparation'],'beta':payload['beta'].tolist(),'rango':payload['rank']}
        (Path(out)/'modelo_lineal_portable.json').write_text(json.dumps(portable,ensure_ascii=False,indent=2))
    data[[ID,ORG]].assign(bloque_reajuste=labels+1).to_csv(Path(out)/'particiones_reajuste.csv',index=False)
    (Path(out)/'modelo_metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))
    return payload,meta

def consultar(payload, tipo, dominio, esfuerzo_estimado, object_points, complejidad,
              experiencia_lenguaje, metodologia, permitir_ausencias=False):
    """Recibe siete entradas. La discrepancia frente a e no es un error observado."""
    values={TYPE:tipo,DOMAIN:dominio,E:esfuerzo_estimado,SIZE:object_points,
            COMPLEXITY:complejidad,EXPERIENCE:experiencia_lenguaje,METHOD:metodologia}
    warnings=[]
    for c,v in values.items():
        if v is None:
            if c in [SIZE,COMPLEXITY,EXPERIENCE] and permitir_ausencias:
                warnings.append(f'{c}: se aplicará la imputación del entrenamiento')
                values[c]=np.nan
                continue
            raise ValueError(f'Falta {c}')
        if isinstance(v,bool) or not isinstance(v,(int,float,np.number)) or not np.isfinite(v):
            raise ValueError(f'{c}: debe ser numérico y finito')
        if c in CODES and v not in CODES[c]: raise ValueError(f'Código inválido en {c}')
        if c in [E,SIZE] and v<0: raise ValueError(f'{c}: no puede ser negativo')
        if c==COMPLEXITY and v not in [1,2,3,4]: raise ValueError('Complejidad debe estar entre 1 y 4')
        if c==EXPERIENCE and v not in [1,2,3,4,5]: raise ValueError('Experiencia debe estar entre 1 y 5')
        if c in [E,SIZE] and v>payload['rangos_observados'][c][1]:
            warnings.append(f'{c}: superior al máximo observado; posible extrapolación')
    for c in [TYPE,DOMAIN,METHOD]:
        if values[c] not in payload['preparation']['seen'][c]:warnings.append(f'{c}: categoría válida sin ejemplos en entrenamiento')
    yhat=float(predict_saved(payload,pd.DataFrame([values]))[0])
    return {'horas_persona_predichas':yhat,
            'diferencia_firmada_frente_a_e':yhat-esfuerzo_estimado,
            'discrepancia_absoluta_frente_a_e':abs(yhat-esfuerzo_estimado),
            'discrepancia_porcentual_frente_a_e':100*abs(yhat-esfuerzo_estimado)/esfuerzo_estimado if esfuerzo_estimado>0 else None,
            'avisos':warnings}
