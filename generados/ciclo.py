# Código generado por DeLuX. La espera se registra en terminal y puede animarse en la interfaz.
def _notificar(accion, valor, linea):
    callback = globals().get("_delux_evento")
    if callback is not None: callback(accion, valor, linea)

class _Semaforo:
    ciclo = ("verde", "amarillo", "rojo")
    def __init__(self): self.color = None
    def encender(self, color, linea):
        self.color = color
        _notificar("encender", color, linea)
        print(f"ENCENDER {color}  # línea {linea}")
    def esperar(self, segundos, linea):
        if not isinstance(segundos, (int, float)) or segundos <= 0:
            raise ValueError(f"Línea {linea}: Regla S2: esperar requiere un número mayor que cero")
        if self.color is None:
            raise ValueError(f"Línea {linea}: Regla S5: encienda una luz antes de esperar")
        _notificar("esperar", segundos, linea)
        print(f"ESPERAR {segundos}  # línea {linea}")
    def cambiar(self, linea):
        if self.color is None:
            raise ValueError(f"Línea {linea}: Regla S5: cambiar requiere una luz encendida")
        self.color = self.ciclo[(self.ciclo.index(self.color) + 1) % len(self.ciclo)]
        _notificar("cambiar", self.color, linea)
        print(f"CAMBIAR a {self.color}  # línea {linea}")
    def apagar(self, linea):
        self.color = None
        _notificar("apagar", None, linea)
        print(f"APAGAR  # línea {linea}")

def _leer_numero(linea):
    callback = globals().get("_delux_leer")
    if callback is not None: return callback(linea)
    valor = input(f"Línea {linea} - Ingrese un número: ")
    try: return float(valor) if "." in valor else int(valor)
    except ValueError: raise ValueError(f"Línea {linea}: Regla S4: la entrada debe ser numérica")

def _repetir(cantidad, linea):
    if not isinstance(cantidad, (int, float)) or int(cantidad) != cantidad or cantidad < 0:
        raise ValueError(f"Línea {linea}: Regla S3: repetir requiere un entero no negativo")
    return range(int(cantidad))

def _dividir(a, b, linea):
    if b == 0: raise ValueError(f"Línea {linea}: Regla S4: no se puede dividir por cero")
    return a / b

semaforo = _Semaforo()
# DeLuX linea 2
semaforo.encender('verde', 2)
# DeLuX linea 3
semaforo.esperar(30, 3)
# DeLuX linea 4
semaforo.cambiar(4)
# DeLuX linea 5
semaforo.esperar(5, 5)
# DeLuX linea 6
semaforo.cambiar(6)
# DeLuX linea 7
semaforo.esperar(25, 7)
# DeLuX linea 8
semaforo.apagar(8)
