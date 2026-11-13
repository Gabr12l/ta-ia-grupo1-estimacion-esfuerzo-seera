# Estimación de esfuerzo en proyectos de software

**Grupo 1 · Inteligencia Artificial 1INF24 · 2026-2**

Esta investigación compara regresión lineal, árbol y KNN para predecir el esfuerzo real registrado de proyectos de software, en horas-persona, mediante SEERA 1.3. El repositorio respalda el apartado experimental de **Grupo1-TA-Final.docx**, incluidas sus Tablas 5 y 6.

El escenario principal utiliza **siete atributos**: tipo, dominio, esfuerzo estimado, tamaño, complejidad, experiencia en el lenguaje y metodología. La hipótesis y el prototipo corresponden a este escenario. El análisis complementario excluye únicamente el esfuerzo estimado y utiliza seis atributos, con los mismos proyectos y particiones, para examinar la dependencia de esa entrada. Ambos responden a una misma investigación.

## Recorrido para revisar el trabajo

| Material | Qué permite revisar |
|---|---|
| [Cuaderno ejecutado](Grupo1-TA-Experimentos.ipynb) | Lectura, auditoría, preparación, validación, resultados, sensibilidad, reajuste y consulta. |
| [Documentación experimental](docs/EXPERIMENTO.md) | Definiciones de los siete atributos, algoritmos, particiones y correspondencia con el Word. |
| [Tabla 5: métricas externas](outputs/ejecucion_20261113T004606426804Z/tabla5_metricas.csv) | Tres familias con siete atributos, tres con seis y referencias B1/B2. |
| [Tabla 6: sensibilidad](outputs/ejecucion_20261113T004606426804Z/sensibilidad_atributos.csv) | Perturbación individual de los siete atributos en las tres familias. |
| [Predicciones externas](outputs/ejecucion_20261113T004606426804Z/predicciones_externas.csv) | Los 960 registros que permiten recalcular las ocho filas de métricas. |
| [Excel de SEERA](data/raw) y [documentos de la fuente](data/docs) | Dataset, códigos y fórmulas utilizados. |
| [Prototipo local](prototipo_local.html) | Consulta del modelo lineal reajustado con siete atributos. Descarga el HTML y ábrelo en tu navegador. |

## Cómo reproducir

1. Descarga el repositorio mediante **Code → Download ZIP**, extrae la carpeta completa y abre una terminal en esa carpeta.
2. Utiliza **Python 3.12** y crea un entorno con las dependencias de `requirements.txt`.

Windows:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

macOS/Linux, con Python 3.12 instalado:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

3. Abre `Grupo1-TA-Experimentos.ipynb` en VS Code con soporte para Python/Jupyter, o en una instalación de Jupyter. Selecciona el Python de `.venv` como kernel y ejecuta **Restart Kernel → Run All**. Mantén como directorio de trabajo la carpeta del repositorio.
4. El cuaderno utiliza el Excel incluido en `data/raw`, comprueba su SHA-256 y genera una carpeta de resultados con identificador propio. `outputs/ULTIMA_EJECUCION.txt` señala la ejecución más reciente.
5. Comprueba las salidas con el Python del mismo entorno:

```bash
python verificar_resultados.py --comparar-informe
```

El verificador recalcula las métricas, comprueba las referencias y la integridad de las particiones y contrasta la sensibilidad con el respaldo del Word. No vuelve a entrenar: para reproducir el entrenamiento se ejecuta el cuaderno. Si experimentas cambiando las rejillas, usa `python verificar_resultados.py` para comprobar tu ejecución; `--comparar-informe` exige además reproducir los resultados del documento.

## Resultados e interpretación

| Procedimiento | MAE | RMSE | R² |
|---|---:|---:|---:|
| Siete atributos · Lineal | 4292,72 | 6848,25 | 0,702 |
| Siete atributos · Árbol | 4347,27 | 7572,35 | 0,636 |
| Siete atributos · KNN | 5166,63 | 9229,34 | 0,459 |
| Seis atributos · Lineal | 8196,04 | 11974,14 | 0,089 |
| Seis atributos · Árbol | 7105,26 | 11962,94 | 0,091 |
| Seis atributos · KNN | 7226,49 | 11725,15 | 0,127 |
| B1 · Esfuerzo estimado | 4018,35 | 7815,75 | 0,612 |
| B2 · Mediana del entrenamiento | 6915,29 | 13261,89 | −0,117 |

MAE y RMSE se expresan en horas-persona. Los CSV conservan la precisión numérica de la ejecución; esta tabla muestra el redondeo del informe.

**Ninguna familia con siete atributos supera B1 en MAE.** El lineal presenta el menor MAE entre esas familias, pero su error es 6,83 % mayor que el de la referencia. La hipótesis no recibe respaldo descriptivo. Con seis atributos, el árbol tiene menor MAE entre los modelos y tampoco supera B2.

Un MAE de 4292,72 expresa el promedio de la magnitud del error sobre los proyectos evaluados; no equivale a un porcentaje de error ni determina el error de cada consulta. R² tampoco representa porcentaje de acierto. Los resultados permiten comparar procedimientos, pero no acreditan una mejora operativa respecto de la estimación registrada.

La sensibilidad permuta cada columna cruda, incluidas sus ausencias, dentro de las reservas externas: 30 repeticiones, semilla 2026 y 21 combinaciones atributo/familia. No selecciona variables ni modelos y no establece causalidad o aporte independiente.

## Fuente, alcance y trazabilidad

SEERA contiene **120 proyectos de 42 organizaciones sudanesas y 76 columnas**, recogidos en 2019–2020. Cada fila es un proyecto. `Actual effort` es exclusivamente el objetivo; `Organization id` agrupa y `ProjID` permite trazabilidad y desempates de vecinos. Ninguno de estos tres campos es predictor.

La selección de atributos cubre naturaleza, contexto, estimación, volumen, dificultad, experiencia técnica y proceso. No se demuestra que sea un conjunto estadísticamente óptimo ni que cada atributo mejore todos los modelos. El estudio es retrospectivo: la disponibilidad previa no está certificada y los esfuerzos estimado y real comparten componentes de cálculo. La reserva de organizaciones no valida cronología ni transferencia a otros países.

`outputs/EJECUCION_DEL_INFORME.txt` identifica el respaldo de las cifras y los tiempos citados en el Word. La ejecución activa reproduce las ocho filas reportadas y la sensibilidad. [La guía de salidas](outputs/README.md) explica cómo distinguir ambos registros y consultar los archivos históricos.

Datos: Mustafa y Osman (2020), [SEERA 1.3](https://zenodo.org/records/4312777). Publicación: https://doi.org/10.1145/3416508.3417119. Se conserva la atribución de la fuente sin asignar otra licencia a sus datos.

ChatGPT asistió en redacción, código, ejecución y verificación. La responsabilidad académica corresponde al equipo. La validación del formulario comprueba cálculo y eventos mediante Node VM; no incluye una revisión visual en navegador.
