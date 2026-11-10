# Bitácora del proyecto DeLuX

Registro de las decisiones del grupo: qué se decidió, por qué y cuándo. Las entradas más recientes van primero.

**Integrantes:** Deiner David Bello González · Luvis Yorfari Correa Mosquera
**Curso:** Compiladores — Fundación Universitaria Claretiana, 2026

---

## 2026-11-10 — Organización del repositorio

- Los documentos de cada actividad van en `docs/actividad-N/`.
- Los programas de prueba van en `ejemplos/correctos/` y `ejemplos/errores/`, porque la Actividad 5 pide volver a probar con ellos.
- La versión inicial (SEMA) se conserva en `docs/historial/` para que quede el registro del cambio.

## 2026-11-10 — Cambio a lenguaje de propósito general: DeLuX

**Contexto.** En la revisión, el docente indicó que el lenguaje no debía servir solo para un semáforo. Debía ser de propósito general, como Python, que se usa en inteligencia artificial sin haber sido hecho solo para eso. También pidió no incluir funciones para no complicar demasiado el compilador.

**Decisiones:**

| Decisión | Por qué |
| --- | --- |
| El lenguaje se llama **DeLuX** y sus archivos usan la extensión `.dlx` | Nombre definido por el grupo |
| Palabras clave en español (`mostrar`, `leer`, `si`, `mientras`) | Los programas se leen casi como instrucciones normales |
| Tres tipos de datos: número, texto y lógico | Es lo mínimo para escribir programas útiles de uso general |
| Los bloques se cierran con `fin`, no con sangría | La estructura es más fácil de revisar en el análisis sintáctico |
| Dos repeticiones: `repetir N veces` y `mientras … hacer` | Una cubre la cantidad fija y la otra la condicional |
| Sin funciones | Indicación del docente, para mantener un tamaño manejable |
| La salida del compilador es una traducción a Python | Es una de las opciones de la Actividad 7 y permite ejecutar los programas sin construir una máquina propia |

**Reglas semánticas previstas para la Actividad 7:**

1. No se puede usar una variable antes de definirla.
2. No se permiten operaciones aritméticas entre texto y números (sí se pueden unir textos con `+`).
3. `repetir` no acepta una cantidad negativa.

## 2026-11-08 — Diseño inicial: SEMA (descartado)

- La primera versión fue **SEMA**, un lenguaje solo para programar el ciclo de luces de un semáforo (`verde`, `amarillo`, `rojo`, `parpadear`…).
- Se reemplazó el 2026-11-10 por el cambio descrito arriba.
