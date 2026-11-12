from pathlib import Path
import json,time,sys
import numpy as np
import pandas as pd

def sensibilidad_atributos(data,out,repeticiones=30,semilla=2026):
    """Permutación en reservas; parámetros ya elegidos dentro del entrenamiento.

    La columna cruda se permuta junto con sus ausencias. La preparación se
    reutiliza sin reajustar; este análisis no selecciona variables ni parámetros.
    """
    from seera_final import blocks,fit_saved,predict_saved,FEATURES_7,ID,Y
    out=Path(out);logs=json.loads((out/'configuraciones.json').read_text())
    guardadas=pd.read_csv(out/'predicciones_externas.csv')
    outer,_=blocks(data,5);rng=np.random.default_rng(semilla)
    errores={(f,c,r):0. for f in ['lineal','arbol','knn'] for c in FEATURES_7 for r in range(repeticiones)}
    bases={f:0. for f in ['lineal','arbol','knn']};start=time.perf_counter()
    for b,(tr,te) in enumerate(outer,1):
        train,test=data.iloc[tr].reset_index(drop=True),data.iloc[te].reset_index(drop=True)
        perms=[rng.permutation(len(test)) for _ in range(repeticiones)]
        for family in bases:
            log=next(x for x in logs if x['bloque']==b and x['entradas']==7 and x['modelo']==family)
            payload=fit_saved(train,family,7,True,log['parametros'])
            baseline=predict_saved(payload,test)
            expected=guardadas.query('entradas==7 and modelo==@family and bloque==@b').set_index('ProjID').loc[test[ID],'prediccion'].to_numpy()
            assert np.allclose(baseline,expected,atol=1e-6,rtol=1e-10)
            bases[family]+=float(np.abs(test[Y].to_numpy()-baseline).sum())
            for c in FEATURES_7:
                for r,perm in enumerate(perms):
                    pert=test.copy();pert[c]=test[c].to_numpy()[perm]
                    pred=predict_saved(payload,pert)
                    errores[family,c,r]+=float(np.abs(test[Y].to_numpy()-pred).sum())
    detailed=[];summary=[]
    for f in bases:
        base=bases[f]/len(data)
        for c in FEATURES_7:
            vals=np.array([errores[f,c,r]/len(data) for r in range(repeticiones)])
            for r,value in enumerate(vals):detailed.append({'modelo':f,'atributo':c,'repeticion':r+1,'MAE_base':base,'MAE_permutado':value,'delta_MAE':value-base})
            summary.append({'modelo':f,'atributo':c,'MAE_base':base,'delta_MAE_media':float((vals-base).mean()),'desviacion_repeticiones':float(vals.std(ddof=0)),'min_delta':float((vals-base).min()),'max_delta':float((vals-base).max())})
    detail=pd.DataFrame(detailed);summ=pd.DataFrame(summary)
    summ.to_csv(out/'sensibilidad_atributos.csv',index=False)
    detail.to_csv(out/'sensibilidad_atributos_repeticiones.csv',index=False)
    (out/'sensibilidad_atributos_config.json').write_text(json.dumps({'semilla':semilla,'repeticiones':repeticiones,'bloques_externos':5,'proyectos':len(data),'columnas_crudas':FEATURES_7,'seleccion_por_esta_prueba':False,'interpretacion':'Dependencia descriptiva del predictor ante perturbaciones. No causalidad ni aporte independiente; permutar rompe asociaciones entre variables.','segundos':time.perf_counter()-start},ensure_ascii=False,indent=2))
    return summ

