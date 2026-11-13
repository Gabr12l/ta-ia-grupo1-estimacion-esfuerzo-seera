# Documentación del experimento

## 1. Pregunta y alcance

Se compara qué familia —regresión lineal, árbol o KNN— obtiene menor MAE al estimar el esfuerzo real registrado de organizaciones reservadas. La hipótesis plantea que al menos una familia con siete atributos obtiene menor MAE que el esfuerzo estimado registrado, B1. Su contraste se limita al escenario principal.

El análisis complementario excluye solo `Estimated effort`. Examina el cambio de desempeño usando el resto de las entradas, los mismos 120 proyectos y las mismas particiones. Es una condición de evaluación dentro de la misma investigación; no cambia el objetivo ni selecciona la familia del prototipo.

El alcance es retrospectivo y descriptivo. No se demuestra estimación temprana, causalidad, significación estadística ni transferencia geográfica.

## 2. Dataset y roles

Archivo: `data/raw/SEERA cost estimation dataset.xlsx`. Hoja: `SEERA dataset`. Los encabezados están en la segunda fila. Se comprueban 120 proyectos únicos, 42 organizaciones y 76 columnas. El archivo se conserva con su organización tabular de origen; cada fila representa un proyecto. El código lee y selecciona campos de esa tabla.

SHA-256: `e4d22e7e8f9f7e2452f8e97500082e3c1ec7c7c087a7ad70a191c3c5fe79f225`.

Los documentos oficiales de códigos y fórmulas se incluyen en [data/docs](../data/docs). `?` indica ausencia; `N/A`, no aplicable. Ninguno se sustituye automáticamente por cero. Las entradas utilizadas tienen seis valores ausentes en cuatro proyectos: 11, 30, 33 y 70. No se eliminan proyectos ni valores extremos.

| Atributo | Definición y función | Tipo y escala | Ausencias | Preparación |
|---|---|---|---:|---|
| `Development type` | Naturaleza del trabajo: desarrollo nuevo, actualización, modificación o personalización de software importado. | Nominal; códigos 1, 2, 3 y 4. | 0 | Indicadores por categoría. |
| `Application domain` | Contexto funcional: banca, ERP, aplicaciones móviles, financieras/administrativas, web y a medida. | Nominal; códigos 1, 2, 3, 5, 6 y 7. | 0 | Indicadores por categoría. |
| `Estimated effort` | Estimación registrada derivada de duración estimada, equipo y jornada; permite estudiar calibración y define B1. | Cuantitativo; horas-persona. | 0 | Escala numérica; KNN la estandariza. Solo está presente en el escenario principal. |
| `Object points` | Número de pantallas más reportes; aproxima volumen del producto. No equivale a puntos de función ni al método ponderado estándar de puntos objeto. | Cuantitativo; pantallas + reportes. | 2 | Mediana del entrenamiento, indicador de ausencia y estandarización solo en KNN. |
| `Product complexity` | Dificultad técnica: simple, con algunas complejidades, complejo o con algoritmos muy complejos. | Ordinal 1–4; dificultad creciente. | 3 | Moda del entrenamiento, indicador de ausencia y estandarización solo en KNN. |
| `Programmers experience in programming language` | Experiencia técnica en el lenguaje: más de 4 años; 2–3; 1–2; 6 meses–1 año; primera experiencia en el proyecto. | Ordinal 1–5; experiencia decreciente. Son códigos, no años exactos. | 1 | Moda del entrenamiento, indicador de ausencia y estandarización solo en KNN. |
| `Methodology` | Proceso de desarrollo: cascada, ágil, híbrida, ninguna, prototipado u otra. | Nominal; códigos 1, 2, 3, 4, 6 y 7, sin orden de calidad. | 0 | Indicadores por categoría. |

Las siete entradas participan en el principal; las seis distintas de `Estimated effort`, en el complementario. La selección responde a su función conceptual y calidad de datos, sin consultar correlaciones con el objetivo ni errores externos. No se declara optimalidad estadística ni beneficio uniforme.

| Campo | Rol exclusivo |
|---|---|
| `Actual effort` | Objetivo: esfuerzo real registrado, en horas-persona, derivado de duración real, equipo y jornada. Nunca es entrada. |
| `Organization id` | Agrupación para reservar organizaciones completas. Nunca es entrada. |
| `ProjID` | Trazabilidad y desempate de distancias en KNN. Nunca es entrada. |

## 3. Preprocesamiento dentro del entrenamiento

En cada ajuste interno y externo se aprende una preparación nueva, usando únicamente sus registros de entrenamiento:

1. Tamaño ausente: mediana. Complejidad y experiencia ausentes: moda, con menor código ante empate.
2. Se conserva un indicador de ausencia para cada uno de esos tres atributos. La ausencia sigue siendo observable después de imputar.
3. Tipo, dominio y metodología usan el vocabulario del diccionario. El lineal omite la categoría de código 1 de cada atributo e incluye intercepto; árbol y KNN utilizan todas las categorías. Códigos inválidos se rechazan. Las categorías válidas sin ejemplos se registran en los diagnósticos y generan aviso en la consulta.
4. Complejidad y experiencia se usan como puntuaciones ordinales. La separación uniforme entre códigos es un supuesto; no representa diferencias físicas iguales ni años exactos.
5. Solo KNN estandariza las entradas numéricas después de imputar: `(valor − media del entrenamiento) / desviación poblacional del entrenamiento`. Si la desviación es cero, la componente vale cero. Los indicadores conservan 0/1.

Con siete atributos, el lineal utiliza 20 columnas más intercepto; árbol y KNN, 23. Sin esfuerzo estimado, son 19 más intercepto y 22, respectivamente. Se registra el rango lineal; las categorías ausentes o columnas constantes pueden limitar la identificación individual de coeficientes.

## 4. Modelos y configuraciones

| Familia | Implementación | Rejilla |
|---|---|---|
| Lineal | Mínimos cuadrados con intercepto, mediante `numpy.linalg.lstsq`. | Una configuración, sin regularización. |
| Árbol | CART de scikit-learn; error cuadrático en divisiones y media del objetivo en hojas. Semilla 2026. | Profundidad 2, 3, 4, 5 o sin límite; mínimo por hoja 2, 5 o 10: 15 combinaciones. |
| KNN | Distancia euclidiana y promedio uniforme o inverso a la distancia. | Vecinos 3, 5, 7 o 9; dos reglas de pesos: 8 combinaciones. |

Con distancia cero, solo se promedian los vecinos seleccionados de distancia cero. Los empates de distancia se ordenan por `ProjID`. Las predicciones se recortan a cero para obtener esfuerzo no negativo. Los coeficientes y asociaciones no se interpretan causalmente.

## 5. Validación anidada por organización

Las organizaciones se ordenan por cantidad decreciente de proyectos e identificador ante empate. Cada organización completa se asigna al bloque menos cargado; empate: menor número de bloque. Esta asignación es determinista y no depende del objetivo.

1. Cinco reservas externas: 24 proyectos por reserva, entre 7 y 10 organizaciones, y 96 proyectos de entrenamiento.
2. Dentro de cada entrenamiento externo se generan tres reservas internas de 32 proyectos, con 64 para ajustar.
3. Para cada familia, condición de entradas y configuración, se aprende preparación y predictor dentro del entrenamiento interno. Se reúnen sus errores de validación y se elige menor MAE.
4. Se reajustan preparación y predictor en los 96 proyectos y se predicen los 24 reservados.
5. Se reúne una predicción externa por proyecto y procedimiento. El MAE global pondera proyectos por igual, no organizaciones.

En empate de MAE interno, árbol prefiere menor profundidad y luego mayor mínimo por hoja; KNN, mayor número de vecinos y luego pesos uniformes. Los escenarios comparten proyectos, asignaciones y rejillas. Ningún bloque de reserva ajusta imputación, escalado o hiperparámetros.

B1 devuelve el esfuerzo estimado del proyecto. B2 devuelve la mediana del esfuerzo real en los 96 proyectos de entrenamiento externo. El esfuerzo estimado no entra al modelo de seis atributos, aunque se conserva para calcular la referencia común B1.

## 6. Métricas e interpretación

Se calculan MAE, RMSE y R² a partir de todas las predicciones externas. MAE es el criterio principal. MAE y RMSE están en horas-persona; R² es adimensional, puede ser negativo y no es porcentaje de acierto.

La [Tabla 5 reproducida](../outputs/ejecucion_20261113T004606426804Z/tabla5_metricas.csv) contiene ocho filas: tres familias con siete entradas, tres con seis y B1/B2. Sus 960 predicciones externas permiten recalcular las métricas sin volver a entrenar. Los CSV guardan los valores numéricos de la ejecución, sin el redondeo de visualización.

El lineal con siete atributos obtiene MAE 4292,72 y B1, 4018,35: el error del lineal es 6,83 % mayor. La hipótesis no recibe respaldo descriptivo. El lineal mejora respecto de B1 en 49 proyectos y empeora en 71. Con seis atributos, el árbol tiene MAE 7105,26 y no supera B2, 6915,29. Esto permite informar un resultado desfavorable de forma reproducible, sin presentar la calibración como mejora operativa demostrada.

El valor absoluto del MAE se interpreta considerando la escala de los proyectos y las referencias: el objetivo va de 396 a 79 200 horas-persona, con mediana 4576. El MAE no significa que todos los proyectos tengan el mismo error; tampoco debe dividirse entre esa mediana para presentarlo como porcentaje de error individual.

## 7. Sensibilidad: Tabla 6

Para cada familia se utiliza el predictor y la preparación correspondientes al entrenamiento externo, con los parámetros elegidos internamente. Se permuta cada columna cruda dentro de los 24 proyectos de su reserva, incluidas las ausencias, sin volver a ajustar. Se repite 30 veces con semilla 2026 y se reúne el MAE sobre los 120 proyectos.

`delta_MAE = MAE con la columna permutada − MAE sin perturbación`.

El [resumen](../outputs/ejecucion_20261113T004606426804Z/sensibilidad_atributos.csv) presenta 21 combinaciones de atributo y familia. Las [630 mediciones](../outputs/ejecucion_20261113T004606426804Z/sensibilidad_atributos_repeticiones.csv) conservan las repeticiones. Delta positivo indica deterioro; negativo, reducción del error. Valores nulos o negativos no prueban irrelevancia. La permutación rompe asociaciones y puede producir combinaciones poco habituales: no mide causalidad ni aporte independiente. No se utiliza para seleccionar atributos, parámetros o familias.

## 8. Reajuste y prototipo

La familia se elige por menor MAE externo entre los modelos con siete atributos; empate: lineal, árbol, KNN. Sus parámetros se revisan con tres bloques organizacionales sobre los 120 proyectos y luego se reajusta el modelo completo. Elegir la familia mediante resultados externos puede producir optimismo. Ese reajuste no constituye otra prueba de generalización.

En los resultados publicados se selecciona el lineal. `modelo_final.joblib` conserva modelo y preparación; `modelo_metadata.json` documenta las siete entradas y el reajuste. El formulario HTML contiene la representación portable del modelo publicado y funciona sin conexión. El cuaderno permite consultar el modelo generado en cada ejecución.

El formulario ofrece cinco selectores y dos entradas numéricas. Rechaza datos incompletos, negativos o inválidos y muestra horas-persona y discrepancia frente al esfuerzo estimado. Esa discrepancia compara la predicción con una estimación: el esfuerzo real de una consulta nueva todavía se desconoce. El porcentaje solo se calcula si el esfuerzo estimado es mayor que cero. La función Python acepta ausencias de tamaño, complejidad o experiencia únicamente con habilitación expresa y aviso de imputación.

Se verifica equivalencia entre HTML y Python en los 116 proyectos completos, con diferencia inferior a 10⁻⁶, además de rechazos y eventos. [El registro](validacion_formulario.json) describe las pruebas mediante Node VM; no se realizó una revisión visual en navegador. El HTML contiene un modelo fijo: cambiar rejillas o entradas del experimento no lo actualiza automáticamente. Si se cambia el modelo, hay que actualizar y verificar también su exportación.

## 9. Correspondencia con Grupo1-TA-Final.docx

| Apartado del informe | Sección del cuaderno | Evidencia |
|---|---|---|
| 3.3 y Tabla 2: datos y atributos | 4. Lectura y auditoría; 5. Descripción | Excel, `auditoria_entradas.csv`, `perfil_atributos.csv`. |
| 3.5.1: preprocesamiento | 2. Funciones; 6. Preparación | Clase `Preparation`; diagnósticos de `configuraciones.json`. |
| 3.5.2 y Tabla 4: modelos | 2. Funciones; 3. Configuración | `fit_predict`, `GRIDS`, `configuracion_ejecucion.json`. |
| 3.5.3: referencias | 7. Evaluación | B1/B2 en `predicciones_externas.csv`. |
| 3.5.4, Figura 1 y Algoritmo 1 | 6 y 7 | Particiones externas e internas, configuraciones candidatas y ganadoras. |
| 4.1.1: setup | 1–7 | Auditoría del Excel, tamaños de bloques, versiones y rejillas. |
| 4.1.2 y Tabla 5 | 8, 9 y 11 | Métricas globales y por bloque; errores pareados frente a B1. |
| 4.1.3 y Tabla 6 | 12. Sensibilidad | Resumen, repeticiones y configuración de permutación. |
| 3.6 y demostración local | 13–15 | Modelo, metadatos, ejemplo de consulta y comprobaciones funcionales. |
| Resultados: parámetros y tiempos | 10. Parámetros y costo | `resumen_parametros.csv`, `configuraciones.json`, `auditoria.json`. |

## 10. Reproducción, experimentación y archivos

Las instrucciones de instalación están en el [README](../README.md). Se requiere Python 3.12 y las versiones de `requirements.txt`. El código del protocolo está en `seera_final.py` y se incluye también en el cuaderno, con la única adaptación de cómo obtiene el directorio raíz. La función de sensibilidad se conserva en `sensibilidad_atributos.py` y en el cuaderno.

Para experimentar, modifica las rejillas de la sección 3, reinicia el kernel y ejecuta todo. Conserva los mismos bloques y no elijas configuraciones según las reservas externas. Cambiar una rejilla puede producir resultados distintos; esto no reemplaza las cifras ya publicadas. La selección de atributos o la regularización requerirían evaluación dentro del entrenamiento.

```bash
python verificar_resultados.py
python verificar_resultados.py --comparar-informe
python verificar_resultados.py --informe
```

La primera orden comprueba la última ejecución. La segunda exige además concordancia de métricas y sensibilidad con el respaldo del Word. La tercera comprueba los ocho procedimientos reportados en ese respaldo. El verificador comprueba cálculos y registros guardados; el entrenamiento completo se reproduce ejecutando el cuaderno.

La [guía de salidas](../outputs/README.md) distingue el respaldo citado por el informe y cada repetición. Las métricas y la sensibilidad son reproducibles bajo el protocolo documentado; los tiempos dependen del equipo, de la carga y del trabajo ejecutado. Los tiempos del Word permanecen asociados a su registro de ejecución y no se atribuyen a una repetición.

## 11. Límites y fuente

La muestra es pequeña, sudanesa y retrospectiva. No se certifica disponibilidad temprana de las siete entradas. El esfuerzo estimado y el real comparten componentes de cálculo; la precisión frente al registro no acredita precisión frente a horas independientes. Una única asignación organizacional no valida cronología ni otros países. Se requiere validación independiente antes de uso operativo y revisión humana de sus recomendaciones.

Fuente: Mustafa y Osman (2020), [SEERA 1.3](https://zenodo.org/records/4312777), https://doi.org/10.1145/3416508.3417119. Los documentos de códigos y fórmulas se distribuyen con atribución a la fuente. Las referencias metodológicas están en el cuaderno y el informe. Se declara apoyo de ChatGPT en redacción, código, ejecución y verificación; la responsabilidad académica es del equipo.
