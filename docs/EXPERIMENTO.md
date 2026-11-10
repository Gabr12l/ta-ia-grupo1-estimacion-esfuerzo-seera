# Descripción del experimento

## Datos y preparación

El Excel SEERA 1.3 contiene una fila por proyecto y los encabezados en la segunda fila. `Actual effort` es el objetivo; `Organization id` agrupa reservas; `ProjID` sirve para trazabilidad y desempates, sin entrar al predictor.

Se incorporaron Object points (pantallas más reportes), complejidad del producto, experiencia en el lenguaje y metodología. Hay seis celdas ausentes en cuatro proyectos; se conservan los 120. Tamaño se imputa con la mediana del entrenamiento; complejidad y experiencia, con la moda. Se agregan indicadores de ausencia. Tipo, dominio y metodología se codifican por indicadores; complejidad y experiencia usan puntuaciones ordinales, con la simplificación de intervalos uniformes declarada.

KNN estandariza las entradas numéricas después de imputar usando estadísticas exclusivas del entrenamiento. Los indicadores permanecen en 0/1. Lineal y árbol conservan escala numérica original.

## Modelos y rejillas

- Lineal: mínimos cuadrados con intercepto y omisión de una categoría de referencia por atributo nominal.
- Árbol: criterio cuadrático; profundidad 2, 3, 4, 5 o sin límite; mínimo por hoja 2, 5 o 10; semilla 2026.
- KNN: distancia euclidiana; 3, 5, 7 o 9 vecinos; promedio uniforme o inverso a la distancia. Si un vecino seleccionado tiene distancia cero, solo se promedian los seleccionados de distancia cero. Empates de distancia: ProjID.

Las predicciones se recortan a cero. La métrica de selección interna es MAE. En empate se prefiere menor profundidad y mayor mínimo por hoja; para KNN, mayor número de vecinos y luego peso uniforme.

## Evaluación

Se asignan organizaciones completas a cinco bloques externos. Cada reserva externa tiene 24 proyectos; el entrenamiento externo tiene 96. Los tres bloques internos separan 64 para ajustar y 32 para reservar. Todas las representaciones y familias comparten particiones. Cada proyecto recibe una predicción externa por procedimiento.

Los errores se reúnen por proyecto antes de calcular MAE, RMSE y R². B1 devuelve el esfuerzo estimado; B2, la mediana del objetivo del entrenamiento externo. MAE y RMSE están en horas-persona. R² puede ser negativo y no es un porcentaje de acierto.

El modelo ampliado de menor MAE externo se reajusta con toda la muestra para la consulta local. Elegir la familia después de observar la comparación externa puede generar optimismo; el reajuste no es un conjunto de prueba nuevo.

## Resultados y trazabilidad

Consulte las tablas del README y los archivos `metricas.csv`, `metricas_por_bloque.csv`, `predicciones_externas.csv`, `configuraciones.json` y `errores_pareados_lineal7_B1.csv` de la ejecución identificada en `outputs/EJECUCION_DEL_INFORME.txt`.

El lineal original conserva el menor MAE. Ampliar atributos mejora el escenario sin esfuerzo estimado, pero ninguno de seis entradas supera la mediana. Ninguno de siete supera el esfuerzo estimado. No se alteraron resultados para favorecer la hipótesis.
