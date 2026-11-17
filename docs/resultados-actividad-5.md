# Resultados de pruebas - Actividad 5

Comando: `python analizador.py <archivo.dlx>` con Python 3. Cada archivo pasa primero por el lexer; el parser se ejecuta cuando el analisis lexico termina correctamente.

| Programa | Resultado esperado | Resultado obtenido |
|---|---|---|
| `ejemplos/correctos/ciclo.dlx` | Correcto | `ejemplos\correctos\ciclo.dlx: análisis léxico y sintáctico correcto.` |
| `ejemplos/correctos/ciclos.dlx` | Correcto | `ejemplos\correctos\ciclos.dlx: análisis léxico y sintáctico correcto.` |
| `ejemplos/correctos/cruce_peatonal.dlx` | Correcto | `ejemplos\correctos\cruce_peatonal.dlx: análisis léxico y sintáctico correcto.` |
| `ejemplos/correctos/decisiones.dlx` | Correcto | `ejemplos\correctos\decisiones.dlx: análisis léxico y sintáctico correcto.` |
| `ejemplos/correctos/semaforo_nocturno.dlx` | Correcto | `ejemplos\correctos\semaforo_nocturno.dlx: análisis léxico y sintáctico correcto.` |
| `ejemplos/correctos/trafico.dlx` | Correcto | `ejemplos\correctos\trafico.dlx: análisis léxico y sintáctico correcto.` |
| `ejemplos/errores/error_lexico.dlx` | Error esperado | `Error léxico — Línea 2, columna 12: carácter no reconocido '@'` |
| `ejemplos/errores/error_semantico.dlx` | Correcto | `ejemplos\errores\error_semantico.dlx: análisis léxico y sintáctico correcto.` |
| `ejemplos/errores/error_sintactico.dlx` | Error esperado | `Error sintáctico — Línea 3, columna 9: se esperaba color; se encontró '\n'` |

El programa `error_semantico.dlx` se acepta en esta actividad porque el identificador es valido y su uso tiene sintaxis correcta. La existencia de variables se comprobara en el analisis semantico de la Actividad 7.

Prueba separada del lexer: `python analizador.py ejemplos/correctos/ciclo.dlx --solo-lexico` imprime tokens con tipo, linea y columna. `--tokens` imprime los tokens y el resultado sintactico.
