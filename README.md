# Estimación de esfuerzo en proyectos de software

Parte experimental de la Tarea Académica del **Grupo 1 · Inteligencia Artificial 1INF24 · 2026-2**.

## Empezar a revisar

1. Abra **[Grupo1-TA-Experimentos.ipynb](Grupo1-TA-Experimentos.ipynb)** para ver el código explicado, tablas y gráficos ya ejecutados.
2. Consulte **[la descripción del experimento](docs/EXPERIMENTO.md)** para revisar datos, entradas, validación y limitaciones.
3. Revise [las métricas globales](outputs/ejecucion_20261110T001702732455Z/metricas.csv) y [las predicciones externas](outputs/ejecucion_20261110T001702732455Z/predicciones_externas.csv), correspondientes a la ejecución del informe.

GitHub permite leer las salidas guardadas. La ejecución del código requiere descargar o clonar la carpeta y abrir el cuaderno en Jupyter o VS Code.

## Formulario local

Abre **prototipo_local.html** con doble clic después de extraer la carpeta. No necesita instalar Python ni conectarse a internet. Tiene los siete campos del modelo ampliado y utiliza la preparación y los coeficientes ya guardados, sin reentrenar. Los códigos y etiquetas corresponden al diccionario oficial.

La discrepancia frente al esfuerzo estimado no es un error real. La ampliación no superó B1: esta consulta demuestra funcionamiento, sin justificar uso operativo. `docs/validacion_formulario.json` registra las pruebas de cálculo y eventos; no se realizó una revisión visual en navegador.

## Pregunta y protocolo

Comparamos regresión lineal, árbol de regresión y KNN para predecir el esfuerzo real registrado de proyectos de SEERA en horas-persona. Contrastamos el esquema original de **3 entradas** con uno ampliado de **7** y versiones complementarias sin esfuerzo estimado (**2 y 6**).

- Datos: **120 proyectos, 42 organizaciones, 76 columnas**, SEERA 1.3.
- Validación anidada: cinco bloques externos y tres internos, siempre por organización.
- Las organizaciones se reservan completas; las estadísticas de preparación se aprenden dentro de entrenamiento.
- Referencias: B1 = esfuerzo estimado registrado; B2 = mediana del objetivo en entrenamiento externo.
- Métricas: MAE (principal), RMSE y R². Resultados retrospectivos y descriptivos, sin inferencia estadística.

## Entradas y resultados

| Representación | Entradas |
| --- | --- |
| Original principal | Tipo de desarrollo, dominio y esfuerzo estimado |
| Ampliada principal | Las tres anteriores más Object points, complejidad, experiencia en el lenguaje y metodología |
| Complementarias | Las respectivas representaciones excluyendo únicamente esfuerzo estimado |

La ampliación añade dimensiones de tamaño, dificultad, experiencia técnica y proceso. Se eligió por contenido y auditoría; no demuestra un subconjunto estadísticamente óptimo.

| Modelo | MAE con 3 entradas | MAE con 7 entradas | MAE con 2 entradas | MAE con 6 entradas |
| --- | ---: | ---: | ---: | ---: |
| Lineal | 3345,04 | 4292,72 | 8571,51 | 8196,04 |
| Árbol | 4392,68 | 4347,27 | 7806,31 | 7105,26 |
| KNN | 4777,98 | 5166,63 | 9722,65 | 7226,49 |

MAE en horas-persona. B1 = **4018,35**; B2 = **6915,29**, sobre los mismos proyectos. La ampliación mejora los tres modelos sin esfuerzo estimado, pero ninguno supera B2. Con siete entradas, ningún modelo supera B1; el lineal original conserva el menor MAE. Se incluyen también resultados desfavorables.

## Reproducir en Windows

Descargue el repositorio desde **Code → Download ZIP** y extraiga la carpeta completa. Instale Python 3.12 y las extensiones Python y Jupyter de VS Code. En una terminal dentro de esa carpeta:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Abra `Grupo1-TA-Experimentos.ipynb`, seleccione el kernel `.venv` y ejecute **Restart Kernel → Run All**.

En macOS o Linux:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

El Excel ya está en `data/raw`; no es necesario descargar datos durante el experimento. Las dependencias se instalan una vez. La primera celda permite cambiar la ruta si se usa el cuaderno de forma independiente.

## Experimentar y verificar

Las rejillas se modifican en la sección 3 del cuaderno. Cada ejecución crea otra carpeta `outputs/ejecucion_...`; `EJECUCION_DEL_INFORME.txt` conserva la identificación de la utilizada en la entrega. Cambiar datos o parámetros requiere interpretar y documentar el nuevo experimento.

La sección 13 permite consultar el modelo ampliado reajustado con siete entradas. Devuelve horas-persona y discrepancia frente a la estimación, que no es un error observado. La función valida entradas y avisa si se autoriza imputación.

Para comprobar los resultados guardados:

```powershell
.venv\Scripts\python.exe verificar_resultados.py
```

Se verifica la integridad de los bloques, la huella del Excel y las métricas recalculadas desde las **1680 predicciones de 14 procedimientos**. El cuaderno se ejecutó sin errores; las métricas históricas de 3/2 entradas se reprodujeron con diferencias menores que 10⁻⁵.

## Estructura

- `Grupo1-TA-Experimentos.ipynb`: cuaderno principal explicado y ejecutado.
- `prototipo_local.html`: formulario local con el modelo ampliado guardado.
- `docs/validacion_formulario.json`: verificación de equivalencia con Python y de validaciones.
- `seera_final.py`: núcleo reutilizable de funciones, incluido también dentro del cuaderno.
- `data/raw`: Excel original sin modificar.
- `data/docs`: lectura, códigos y fórmulas oficiales de SEERA.
- `data/reference`: métricas de la representación original.
- `outputs`: particiones, predicciones, métricas, rejillas, gráficos, auditoría y modelo reajustado.
- `docs/EXPERIMENTO.md`: descripción del apartado experimental.
- `verificar_resultados.py`: comprobación reproducible de salidas guardadas.
- `requirements.txt`: dependencias.
- `MANIFIESTO_ARCHIVOS.json`: archivos incluidos y huellas SHA-256.

## Alcance y fuentes

SEERA es pequeño, retrospectivo y sudanés. Sus esfuerzos estimado y real comparten componentes de cálculo; no son mediciones independientes de horas. No se certificó disponibilidad temprana ni transferencia a otros países. La familia se elige tras comparar resultados externos, por lo que su error puede ser optimista respecto del procedimiento completo de selección. El reajuste final sirve para demostrar funcionamiento y no constituye otra prueba de generalización.

Datos y documentación: Mustafa, E. I. y Osman, R. (2020), SEERA 1.3, https://zenodo.org/records/4312777. Publicación: https://doi.org/10.1145/3416508.3417119. Se conserva la atribución de la fuente, sin asignar una licencia nueva a los datos.

Antecedentes: Wen et al. (2012), https://doi.org/10.1016/j.infsof.2011.09.002; Shepperd y MacDonell (2012), https://doi.org/10.1016/j.infsof.2011.12.008; Kitchenham et al. (2007), https://doi.org/10.1109/TSE.2007.1001; Mustafa y Osman (2024), https://doi.org/10.1016/j.infsof.2024.107413.

Preparación asistida con ChatGPT en redacción, código, auditoría, ejecución y verificación. La revisión e integración final son responsabilidad del equipo. Este repositorio documenta el apartado experimental y no reemplaza el informe ni la presentación de Paideia.
