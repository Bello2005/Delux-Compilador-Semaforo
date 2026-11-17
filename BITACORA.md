# Bitácora del proyecto DeLuX

Registro de las decisiones del grupo: qué se decidió, por qué y cuándo. Las entradas más recientes van primero.

**Integrantes:** Deiner David Bello González · Luvis Yorfari Correa Mosquera
**Tema asignado:** Semáforos
**Curso:** Compiladores — Fundación Universitaria Claretiana, 2026

---

## 2026-11-15 — Retroalimentación de la Actividad 3

**Observaciones del docente:**

1. El tema Semáforos no se puede cambiar. El lenguaje necesita al menos tres instrucciones propias del tema, y `mostrar` y `leer` no cuentan porque sirven para cualquier cosa.
2. En el último commit se borraron la bitácora, los archivos `.dlx` y el diagrama. Hay que volver a subirlos.
3. El lenguaje tiene bastante más de lo mínimo (texto, división, `>=`, `<=`, `!=`, `y`/`o`/`no` y `mientras`), lo que va a alargar el lexer, la gramática y el parser.
4. Todos los commits son de un solo integrante; cada uno debe hacer los suyos.
5. Lo escrito en el documento sobre el uso de Claude debe estar también en la bitácora.

**Decisiones:**

| Decisión | Por qué |
| --- | --- |
| DeLuX conserva su núcleo general y agrega cuatro instrucciones del tema: `encender color`, `esperar N`, `cambiar` y `apagar` | Cumple el tema obligatorio sin perder la parte general del lenguaje |
| `rojo`, `amarillo` y `verde` pasan a ser palabras reservadas | El analizador sintáctico puede exigir un color válido después de `encender` |
| `cambiar` avanza en el ciclo verde → amarillo → rojo → verde | Representa el comportamiento normal de un semáforo sin tener que nombrar el color |
| Los seis programas se reescribieron para usar las instrucciones del tema | Lo pidió el docente y sirven de prueba para la Actividad 5 |
| Nueva regla semántica: el tiempo de `esperar` debe ser un número mayor que cero | Un semáforo no puede esperar 0 segundos ni un tiempo negativo |
| Se restauraron la bitácora, los `.dlx` y el diagrama | Se necesitan para la Actividad 5 y la bitácora es obligatoria |
| Las extensiones del lenguaje se mantienen por ahora | El grupo revisará si recorta alguna al planear la Actividad 5 |

## 2026-11-17 — Implementación de la Actividad 5

- Se eligió Python 3 estándar para implementar el analizador sin dependencias externas.
- Se conservó el conjunto de instrucciones y operadores del diseño de la Actividad 3; se escribió la gramática formal en `docs/gramatica.ebnf`.
- Se implementaron el lexer y el parser en `analizador.py`. Los diagnósticos incluyen la fase, la línea y la columna. En ese momento, la revisión semántica quedó pendiente para la Actividad 7.
- Se agregaron tres ejemplos válidos y se guardaron los resultados de los nueve programas en `docs/resultados-actividad-5.md`.
- Asistencia de Codex (OpenAI, 2026): apoyo en la implementación del lexer/parser, redacción de la gramática y preparación de ejemplos y resultados.

## 2026-11-17 — Implementación de la Actividad 7

- Se agregó la construcción del árbol sintáctico y una tabla de símbolos con tipos para revisar variables definidas antes de usarse y operaciones compatibles.
- Se programaron S1 (variable definida antes de usar), S2 (espera numérica positiva), S3 (repetición entera no negativa), S4 (tipos compatibles) y S5 (esperar/cambiar requiere una luz encendida); los errores semánticos muestran regla, línea y columna.
- Se agregó la traducción de DeLuX a Python ejecutable, con simulación del semáforo y validación de cantidades que solo se conocen al leer datos.
- Se añadieron ejemplos de error para S2, S3 y S5, un programa generado de muestra, los resultados de ejecución y la reflexión de la actividad.
- Se añadió `simulador.py`, una interfaz Tkinter que ejecuta el Python generado y anima los cambios de luz y las esperas; las entradas de `leer` se solicitan en una ventana.
- Asistencia de Codex (OpenAI, 2026): apoyo en el árbol sintáctico, las comprobaciones semánticas, la generación a Python, las pruebas y la documentación.

## 2026-11-10 — Cambio a lenguaje de propósito general: DeLuX

- El lenguaje pasó de SEMA (solo semáforo) a **DeLuX**, un lenguaje de propósito general con palabras clave en español. Sus archivos usan la extensión `.dlx`.
- Tipos de datos: número, texto y lógico.
- Los bloques se cierran con `fin`, no con sangría, para que la estructura sea más fácil de revisar en el análisis sintáctico.
- Dos repeticiones: `repetir N veces` (cantidad fija) y `mientras … hacer` (condicional).
- Sin funciones, por indicación del docente.
- La salida del compilador será una traducción a Python, una de las opciones de la Actividad 7.

## 2026-11-08 — Diseño inicial: SEMA (descartado)

- La primera versión fue **SEMA**, un lenguaje solo para dar órdenes fijas a un semáforo (`verde 30`, `amarillo 5`, `rojo 25`, `parpadear`…).
- Se reemplazó el 2026-11-10 por DeLuX.

---

## Uso de herramientas de inteligencia artificial

- **Claude** (Anthropic, 2026), asistente de inteligencia artificial. Utilizado para organizar el documento y revisar la redacción de las explicaciones.
