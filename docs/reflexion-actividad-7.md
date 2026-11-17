# Reflexión — Actividad 7

Lo más difícil fue conectar el análisis semántico con las estructuras de control. No basta con saber que un nombre tiene forma de variable: también hay que comprobar si ya recibió un valor y si su tipo sirve en la operación. Por eso construimos un árbol sintáctico y una tabla de símbolos. En las ramas de una condición solo conservamos las variables definidas en ambos caminos; así evitamos aceptar un uso que fallaría cuando se toma la otra rama.

Para las reglas propias de DeLuX decidimos que `esperar` necesita un número positivo, `repetir` acepta solo cantidades enteras no negativas y `esperar` o `cambiar` requieren una luz encendida. Cada diagnóstico indica el código de la regla y la línea del programa. Los valores que dependen de `leer` se verifican también durante la ejecución generada.

Elegimos traducir a Python porque permite ver con claridad cómo cada instrucción DeLuX se convierte en una operación ejecutable. El semáforo simulado imprime los cambios de luz y los tiempos sin hacer pausas reales, lo cual facilita probarlo. Mantuvimos el lexer y el parser como fases separadas y agregamos el análisis semántico antes de generar el archivo. En una siguiente versión sería útil mejorar el manejo de entradas no numéricas y presentar los errores de tipos con ejemplos más específicos.
