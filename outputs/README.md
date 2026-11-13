# Guía de resultados

El cuaderno activo evalúa tres familias con siete atributos, tres con seis y dos referencias: ocho filas de métricas y 960 predicciones externas. La sensibilidad produce 21 filas de resumen y 630 mediciones.

| Indicador | Uso |
|---|---|
| `ULTIMA_EJECUCION.txt` | Carpeta más reciente producida por el cuaderno activo. Se actualiza al finalizar correctamente. |
| `EJECUCION_DEL_INFORME.txt` | Respaldo de las cifras y tiempos citados en Grupo1-TA-Final.docx. Se conserva sin sobrescribir. |

La ejecución activa publicada es `ejecucion_20261113T004606426804Z`. Sus métricas y sensibilidad se verificaron contra las Tablas 5 y 6 y contra el respaldo del informe. Los tiempos de una repetición se conservan por separado.

El respaldo citado es `ejecucion_20261112T210511101191Z`. Su auditoría registra 2,8318355069998233 segundos, que el Word presenta como 2,832. Ese registro conserva cálculos adicionales a los ocho procedimientos reportados; no forman parte del recorrido del estudio ni de su hipótesis. El verificador con `--informe` identifica exclusivamente las filas con siete/seis atributos y B1/B2. Las carpetas históricas no se modifican y la ejecución activa no vuelve a calcular comparaciones ajenas al informe.

## Archivos de cada ejecución activa

| Archivo | Contenido |
|---|---|
| `metricas.csv`, `tabla5_metricas.csv` | MAE, RMSE y R² de los ocho procedimientos. La segunda tabla ordena la presentación. |
| `predicciones_externas.csv` | Proyecto, organización, bloque, condición de entradas, familia, objetivo, predicción y error absoluto. |
| `metricas_por_bloque.csv` | Desempeño por reserva externa. |
| `particiones_externas.csv`, `particiones_internas.csv` | Asignaciones organizacionales externas y las internas de cada entrenamiento. |
| `particiones_reajuste.csv` | Asignación usada para revisar los parámetros antes del reajuste con todos los proyectos. |
| `configuracion_ejecucion.json`, `seleccion_predefinida.json` | Rejillas, atributos y decisiones del protocolo. |
| `configuraciones.json`, `resumen_parametros.csv` | Candidatos, parámetros ganadores, preparación, rango lineal y tiempos. |
| `auditoria.json`, `auditoria_entradas.csv`, `perfil_atributos.csv` | Integridad, ausencias, versiones, unidades y huella del Excel. |
| `sensibilidad_atributos.csv` | Resumen de las 21 combinaciones atributo/familia de la Tabla 6. |
| `sensibilidad_atributos_repeticiones.csv` | Las 630 mediciones de permutación. |
| `sensibilidad_atributos_config.json` | Semilla, repeticiones, alcance y tiempo de sensibilidad. |
| `errores_pareados_lineal7_B1.csv` | Comparación por proyecto entre el lineal principal y B1. |
| `modelo_final.joblib`, `modelo_metadata.json` | Modelo reajustado y metadatos. El nombre del archivo del modelo en registros históricos puede diferir. |
| `modelo_lineal_portable.json` | Preparación y coeficientes exportados cuando se selecciona el lineal. |
| `ejemplo_consulta.json` | Entrada hipotética y respuesta del modelo; no mide exactitud. |
| `descripcion_datos.png`, `comparacion_MAE.png` | Figuras descriptivas y comparación de errores. |
| `manifiesto.json` | Índice de archivos y fuente de la ejecución. |

`MANIFIESTO_ARCHIVOS.json`, en la raíz, identifica la entrega experimental activa y sus huellas; no pretende inventariar todas las carpetas históricas.
