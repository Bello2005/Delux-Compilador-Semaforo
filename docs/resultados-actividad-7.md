# Resultados de pruebas - Actividad 7

Comando: `python analizador.py <archivo.dlx>`. Se verificaron 13 programas: los seis ejemplos validos pasan y los siete programas con error fallan en la fase esperada. Los diagnosticos incluyen linea, columna y, para errores semanticos, regla. Pruebas ejecutadas con Python 3.12.

| Programa | Resultado esperado | Resultado obtenido |
|---|---|---|
| `ejemplos/correctos/ciclo.dlx` | Aceptado | `ejemplos\correctos\ciclo.dlx: análisis léxico, sintáctico y semántico correcto.` |
| `ejemplos/correctos/ciclos.dlx` | Aceptado | `ejemplos\correctos\ciclos.dlx: análisis léxico, sintáctico y semántico correcto.` |
| `ejemplos/correctos/cruce_peatonal.dlx` | Aceptado | `ejemplos\correctos\cruce_peatonal.dlx: análisis léxico, sintáctico y semántico correcto.` |
| `ejemplos/correctos/decisiones.dlx` | Aceptado | `ejemplos\correctos\decisiones.dlx: análisis léxico, sintáctico y semántico correcto.` |
| `ejemplos/correctos/semaforo_nocturno.dlx` | Aceptado | `ejemplos\correctos\semaforo_nocturno.dlx: análisis léxico, sintáctico y semántico correcto.` |
| `ejemplos/correctos/trafico.dlx` | Aceptado | `ejemplos\correctos\trafico.dlx: análisis léxico, sintáctico y semántico correcto.` |
| `ejemplos/errores/error_cambiar.dlx` | Error detectado | `Error semántico — Línea 1, columna 1: Regla S5 (esperar y cambiar requieren una luz encendida): encienda una luz antes de cambiar` |
| `ejemplos/errores/error_espera.dlx` | Error detectado | `Error semántico — Línea 3, columna 1: Regla S2 (esperar requiere un tiempo numerico mayor que cero): esperar recibió 0; el tiempo debe ser mayor que cero` |
| `ejemplos/errores/error_lexico.dlx` | Error detectado | `Error léxico — Línea 2, columna 12: carácter no reconocido '@'` |
| `ejemplos/errores/error_repetir.dlx` | Error detectado | `Error semántico — Línea 2, columna 1: Regla S3 (repetir requiere una cantidad entera no negativa): la cantidad -2 debe ser un entero no negativo` |
| `ejemplos/errores/error_semantico.dlx` | Error detectado | `Error semántico — Línea 2, columna 9: Regla S1 (toda variable debe definirse antes de usarse): la variable 'tiempo_rojo' no está definida` |
| `ejemplos/errores/error_sintactico.dlx` | Error detectado | `Error sintáctico — Línea 3, columna 9: se esperaba color; se encontró '\n'` |
| `ejemplos/errores/error_tipos.dlx` | Error detectado | `Error semántico — Línea 3, columna 9: Regla S4 (las operaciones y condiciones deben respetar sus tipos): el tiempo de 'esperar' debe ser numérico` |

## Generacion y ejecucion

Comando de generacion: `python analizador.py ejemplos/correctos/ciclo.dlx --generar-python generados/ciclo.py`. Luego se ejecuto `python generados/ciclo.py`; salida:

```text
ENCENDER verde  # línea 2
ESPERAR 30  # línea 3
CAMBIAR a amarillo  # línea 4
ESPERAR 5  # línea 5
CAMBIAR a rojo  # línea 6
ESPERAR 25  # línea 7
APAGAR  # línea 8
```

Comprobaciones durante la ejecucion para valores leidos:
- Entrada invalida para espera: Regla S2 en linea 3.
- Entrada invalida para repetir: Regla S3 en linea 2.
- Entrada invalida para division: Regla S4 en linea 3.

Tambien se genero `trafico.dlx` y se ejecuto con entrada `8`; la traduccion acepto la entrada, evaluo la condicion, repitio tres ciclos e imprimio el cierre del turno.

## Interfaz grafica

El programa `simulador.py` conecta eventos generados por DeLuX con una ventana Tkinter. Se verifico que el ciclo de ejemplo entrega las siete acciones esperadas al callback visual y que Tkinter 8.6 esta disponible en Python 3.12. La ventana se inicia con `python simulador.py ejemplos/correctos/ciclo.dlx`.
