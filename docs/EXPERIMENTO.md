# Estimación de esfuerzo en proyectos de software

Estudio del Grupo 1, Inteligencia Artificial 1INF24, 2026-2.

El objetivo es predecir Actual effort de SEERA en horas-persona. El escenario principal utiliza **siete atributos**: Development type, Application domain, Estimated effort, Object points, Product complexity, Programmers experience in programming language y Methodology. El complementario excluye solo Estimated effort y utiliza seis. Se comparan regresión lineal, árbol y KNN mediante cinco bloques externos y tres internos por organización.

## Consultar y reproducir

1. Abre el cuaderno explicado y las tablas CSV para revisar el experimento.
2. Abre `Grupo1-TA-Experimentos.ipynb`: contiene código, resultados y gráficos ejecutados. En Python 3.12 instala `requirements.txt`, selecciona el entorno en Jupyter o VS Code y ejecuta Restart Kernel → Run All.
3. El Excel se encuentra en `data/raw` y su diccionario y fórmulas en `data/docs`.
4. Ejecuta `python verificar_resultados.py` para comprobar particiones, métricas, ejecución del cuaderno y sensibilidad de los siete atributos.
5. Abre `prototipo_local.html` para consultar el modelo guardado sin conexión. La discrepancia frente al esfuerzo estimado no es un error observado.

En Windows: `py -3.12 -m venv .venv` y `.venv\Scripts\python.exe -m pip install -r requirements.txt`. En macOS/Linux: `python3 -m venv .venv` y `.venv/bin/python -m pip install -r requirements.txt`.

## Resultados e interpretación

Con siete atributos, el lineal obtiene MAE 4292,72 horas-persona y no supera B1 (esfuerzo estimado: 4018,35). Sin esfuerzo estimado, el árbol obtiene MAE 7105,26 y no supera B2 (mediana del entrenamiento: 6915,29). La hipótesis del escenario principal no recibe respaldo descriptivo.

Los controles reducidos utilizan tipo y dominio, con esfuerzo estimado (tres entradas) o sin él (dos). Se evalúan con las mismas reservas y rejillas, reajustando cada representación. `comparacion_conjuntos.csv` conserva la comparación: sin esfuerzo estimado, el conjunto completo reduce el MAE en 4,38 % (lineal), 8,98 % (árbol) y 25,67 % (KNN); con esfuerzo estimado, solo árbol mejora (1,03 %). El control lineal de tres entradas obtiene MAE 3345,04, inferior a B1 en 16,76 %. Este resultado auxiliar no respalda la hipótesis definida para siete entradas ni cambia la familia y representación del prototipo. El contraste conjunto no atribuye el efecto individual de tamaño, complejidad, experiencia y metodología.

Cada atributo se evalúa por permutación dentro de las reservas de las tres familias, con 30 repeticiones y semilla 2026. La preparación y el predictor se reutilizan sin ajustar. ΔMAE positivo indica deterioro al perturbar la columna; no mide causalidad ni aporte independiente. Las ausencias se permutan junto con su columna cruda. Esta prueba no selecciona variables ni parámetros.

La ejecución del informe es `ejecucion_20261112T210511101191Z`, identificada por `outputs/EJECUCION_DEL_INFORME.txt`. `metricas.csv` y `predicciones_externas.csv` respaldan la evaluación; `perfil_atributos.csv` caracteriza los siete campos; `sensibilidad_atributos.csv` y `sensibilidad_atributos_repeticiones.csv` conservan las 21 combinaciones atributo/modelo y las 630 mediciones. Las rejillas, particiones y auditoría permiten reproducir el protocolo. Los conjuntos reducidos se definen y analizan en el informe como controles auxiliares; no definen la hipótesis principal.

## Alcance y fuente

SEERA contiene 120 proyectos de 42 organizaciones sudanesas, recogidos en 2019–2020, con 76 columnas. La lista de siete atributos se justifica por su función conceptual y calidad de datos, sin optimalidad estadística demostrada. Los esfuerzos comparten componentes de cálculo y la disponibilidad temporal de las entradas no está certificada; la evidencia es retrospectiva y descriptiva. Se requiere validación independiente para uso operativo o transferencia geográfica.

Datos: Mustafa y Osman (2020), SEERA 1.3, https://zenodo.org/records/4312777. Publicación: https://doi.org/10.1145/3416508.3417119. Se conserva la atribución de la fuente, sin asignar otra licencia a sus datos. ChatGPT asistió en redacción, código, ejecución y verificación; la responsabilidad académica corresponde al equipo.

Repositorio experimental: https://github.com/Gabr12l/ta-ia-grupo1-estimacion-esfuerzo-seera.
