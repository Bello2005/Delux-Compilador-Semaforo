#!/usr/bin/env python3
"""Interfaz gráfica para animar programas DeLuX con Tkinter."""
from __future__ import annotations

import queue
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk

from analizador import ErrorDeLuX, compilar_fuente


class SimuladorDeLuX:
    COLORES = {
        "rojo": ("#ef4444", "#451b22"),
        "amarillo": ("#facc15", "#493c12"),
        "verde": ("#22c55e", "#173c2a"),
    }

    def __init__(self, raiz: tk.Tk, archivo: Path | None = None):
        self.raiz = raiz
        self.raiz.title("DeLuX · Simulador de semáforo")
        self.raiz.geometry("850x610")
        self.raiz.minsize(760, 540)
        self.raiz.configure(bg="#101827")
        self.ruta: Path | None = None
        self.codigo: str | None = None
        self.eventos: queue.Queue = queue.Queue()
        self.detener = threading.Event()
        self.hilo: threading.Thread | None = None
        self.color_actual: str | None = None
        self.ocupado = False
        self.velocidad = tk.DoubleVar(value=1.0)
        self.etiqueta_velocidad: tk.Label | None = None
        self._crear_interfaz()
        self.raiz.protocol("WM_DELETE_WINDOW", self._cerrar)
        self.raiz.after(80, self._procesar_eventos)
        if archivo:
            self._cargar(archivo)

    def _crear_interfaz(self) -> None:
        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure("TButton", font=("Segoe UI", 10), padding=(12, 8))

        encabezado = tk.Frame(self.raiz, bg="#101827")
        encabezado.pack(fill="x", padx=24, pady=(20, 12))
        tk.Label(encabezado, text="DeLuX", fg="#f8fafc", bg="#101827",
                 font=("Segoe UI", 23, "bold")).pack(anchor="w")
        tk.Label(encabezado, text="Simulador visual de programas para semáforos",
                 fg="#94a3b8", bg="#101827", font=("Segoe UI", 10)).pack(anchor="w")

        controles = tk.Frame(self.raiz, bg="#101827")
        controles.pack(fill="x", padx=24, pady=(0, 14))
        self.boton_abrir = ttk.Button(controles, text="Abrir programa .dlx", command=self._elegir_archivo)
        self.boton_abrir.pack(side="left")
        self.boton_iniciar = ttk.Button(controles, text="▶  Ejecutar", command=self._iniciar, state="disabled")
        self.boton_iniciar.pack(side="left", padx=(10, 0))
        self.boton_detener = ttk.Button(controles, text="■  Detener", command=self._detener, state="disabled")
        self.boton_detener.pack(side="left", padx=(10, 0))
        tk.Label(controles, text="Velocidad", fg="#cbd5e1", bg="#101827",
                 font=("Segoe UI", 9)).pack(side="left", padx=(18, 6))
        self.control_velocidad = ttk.Scale(controles, from_=0.25, to=10.0,
                                           variable=self.velocidad, command=self._actualizar_velocidad,
                                           length=130)
        self.control_velocidad.pack(side="left")
        self.etiqueta_velocidad = tk.Label(controles, text="1x (normal)", width=13,
                                           fg="#94a3b8", bg="#101827", font=("Segoe UI", 9))
        self.etiqueta_velocidad.pack(side="left", padx=(6, 0))
        self.etiqueta_archivo = tk.Label(controles, text="Ningún archivo seleccionado",
                                         fg="#94a3b8", bg="#101827", font=("Segoe UI", 9))
        self.etiqueta_archivo.pack(side="right", padx=4)

        contenido = tk.Frame(self.raiz, bg="#101827")
        contenido.pack(fill="both", expand=True, padx=24, pady=(0, 22))
        panel_luces = tk.Frame(contenido, bg="#182337", highlightthickness=1,
                               highlightbackground="#26354d")
        panel_luces.pack(side="left", fill="y", padx=(0, 14))
        tk.Label(panel_luces, text="SEMÁFORO", fg="#a9b8cc", bg="#182337",
                 font=("Segoe UI", 9, "bold")).pack(padx=28, pady=(18, 10))
        self.canvas = tk.Canvas(panel_luces, width=190, height=330, bg="#182337", highlightthickness=0)
        self.canvas.pack(padx=15, pady=(0, 16))
        self._dibujar_semaforo()

        panel_info = tk.Frame(contenido, bg="#182337", highlightthickness=1,
                              highlightbackground="#26354d")
        panel_info.pack(side="left", fill="both", expand=True)
        tk.Label(panel_info, text="EJECUCIÓN", fg="#a9b8cc", bg="#182337",
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=18, pady=(18, 8))
        self.estado = tk.Label(panel_info, text="Abre un archivo DeLuX para comenzar.",
                               fg="#f8fafc", bg="#182337", font=("Segoe UI", 12), anchor="w")
        self.estado.pack(fill="x", padx=18, pady=(0, 4))
        self.detalle = tk.Label(panel_info, text="", fg="#94a3b8", bg="#182337",
                                font=("Consolas", 10), anchor="w")
        self.detalle.pack(fill="x", padx=18, pady=(0, 12))
        self.boton_generar = ttk.Button(panel_info, text="Generar Python",
                                        command=self._generar_python, state="disabled")
        self.boton_generar.pack(anchor="e", padx=16, pady=(0, 8))
        self.registro = tk.Text(panel_info, height=12, bg="#0d1522", fg="#cbd5e1",
                                insertbackground="#f8fafc", relief="flat", wrap="word",
                                font=("Consolas", 9), padx=12, pady=10, state="disabled")
        self.registro.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        tk.Label(self.raiz, text="Velocidad 1x = tiempo real. Ajusta el control para acelerar o ralentizar las esperas.",
                 fg="#718198", bg="#101827", font=("Segoe UI", 9)).pack(pady=(0, 12))

    def _actualizar_velocidad(self, _valor=None) -> None:
        velocidad = max(0.25, min(10.0, self.velocidad.get()))
        texto = "1x (normal)" if abs(velocidad - 1.0) < 0.03 else f"{velocidad:.1f}x"
        if self.etiqueta_velocidad:
            self.etiqueta_velocidad.configure(text=texto)

    def _dibujar_semaforo(self) -> None:
        self.canvas.delete("all")
        self.canvas.create_rectangle(48, 15, 142, 315, fill="#111827", outline="#334155", width=3)
        for nombre, y in (("rojo", 65), ("amarillo", 165), ("verde", 265)):
            encendido = nombre == self.color_actual
            activo, apagado = self.COLORES[nombre]
            self.canvas.create_oval(67, y - 32, 123, y + 24,
                                    fill=activo if encendido else apagado,
                                    outline=activo if encendido else "#344256", width=3)
            self.canvas.create_text(95, y + 39, text=nombre.upper(),
                                    fill="#e2e8f0" if encendido else "#718198",
                                    font=("Segoe UI", 8, "bold"))

    def _elegir_archivo(self) -> None:
        nombre = filedialog.askopenfilename(
            title="Seleccionar programa DeLuX", filetypes=(("Programas DeLuX", "*.dlx"), ("Todos los archivos", "*.*"))
        )
        if nombre:
            self._cargar(Path(nombre))

    def _cargar(self, ruta: Path) -> None:
        try:
            fuente = ruta.read_text(encoding="utf-8")
            codigo = compilar_fuente(fuente)
        except (OSError, ErrorDeLuX, SyntaxError) as exc:
            messagebox.showerror("No se pudo cargar el programa", str(exc), parent=self.raiz)
            self.codigo = None
            self.boton_iniciar.configure(state="disabled")
            self.boton_generar.configure(state="disabled")
            return
        self.ruta, self.codigo = ruta, codigo
        self.etiqueta_archivo.configure(text=ruta.name, fg="#cbd5e1")
        self.estado.configure(text="Programa validado. Listo para ejecutar.")
        self.detalle.configure(text="Lexer · parser · semántico · Python")
        self.boton_iniciar.configure(state="normal")
        self.boton_generar.configure(state="normal")
        self.color_actual = None
        self._dibujar_semaforo()
        self._escribir(f"Programa cargado: {ruta.name}")

    def _generar_python(self) -> None:
        if not self.codigo:
            return
        destino = filedialog.asksaveasfilename(
            title="Guardar código Python",
            defaultextension=".py",
            initialfile=f"{self.ruta.stem if self.ruta else 'programa'}.py",
            filetypes=(("Archivos Python", "*.py"), ("Todos los archivos", "*.*")),
        )
        if not destino:
            return
        try:
            Path(destino).write_text(self.codigo, encoding="utf-8")
        except OSError as exc:
            messagebox.showerror("No se pudo guardar el código", str(exc), parent=self.raiz)
            return
        self._escribir(f"Código Python generado: {Path(destino).name}")
        messagebox.showinfo("Código generado", f"Se guardó el programa Python en:\n{destino}", parent=self.raiz)

    def _iniciar(self) -> None:
        if not self.codigo or self.ocupado:
            return
        self.detener.clear()
        self.ocupado = True
        self.color_actual = None
        self._dibujar_semaforo()
        self.estado.configure(text="Ejecutando…")
        self.detalle.configure(text="Preparando primera instrucción")
        self.boton_iniciar.configure(state="disabled")
        self.boton_abrir.configure(state="disabled")
        self.boton_detener.configure(state="normal")
        self.hilo = threading.Thread(target=self._ejecutar_codigo, daemon=True)
        self.hilo.start()

    def _ejecutar_codigo(self) -> None:
        try:
            espacio = {
                "__name__": "__main__",
                "_delux_evento": self._esperar_evento,
                "_delux_leer": self._pedir_numero,
            }
            exec(compile(self.codigo, str(self.ruta or "<programa DeLuX>"), "exec"), espacio)
            self.eventos.put(("fin", "Programa terminado correctamente."))
        except InterrupcionSimulador:
            self.eventos.put(("fin", "Ejecución detenida."))
        except Exception as exc:
            self.eventos.put(("fin", f"Ejecución detenida por un error: {exc}"))

    def _esperar_evento(self, accion: str, valor, linea: int) -> None:
        if self.detener.is_set():
            raise InterrupcionSimulador()
        respuesta = threading.Event()
        self.eventos.put(("paso", accion, valor, linea, respuesta))
        while not respuesta.wait(0.1):
            if self.detener.is_set():
                raise InterrupcionSimulador()

    def _pedir_numero(self, linea: int):
        if self.detener.is_set():
            raise InterrupcionSimulador()
        respuesta = {"evento": threading.Event(), "valor": None, "cancelado": False}
        self.eventos.put(("leer", linea, respuesta))
        while not respuesta["evento"].wait(0.1):
            if self.detener.is_set():
                raise InterrupcionSimulador()
        if respuesta["cancelado"]:
            raise InterrupcionSimulador()
        return respuesta["valor"]

    def _procesar_eventos(self) -> None:
        try:
            while True:
                evento = self.eventos.get_nowait()
                if evento[0] == "paso":
                    _, accion, valor, linea, respuesta = evento
                    self._mostrar_paso(accion, valor, linea, respuesta)
                elif evento[0] == "leer":
                    _, linea, respuesta = evento
                    self._mostrar_entrada(linea, respuesta)
                elif evento[0] == "fin":
                    self._terminar(evento[1])
        except queue.Empty:
            pass
        self.raiz.after(80, self._procesar_eventos)

    def _mostrar_paso(self, accion: str, valor, linea: int, respuesta: threading.Event) -> None:
        nombres = {"encender": f"Encender {valor}", "cambiar": f"Cambiar a {valor}",
                   "apagar": "Apagar semáforo", "esperar": f"Esperar {valor} segundos"}
        if accion in ("encender", "cambiar"):
            self.color_actual = valor
        elif accion == "apagar":
            self.color_actual = None
        self._dibujar_semaforo()
        self.estado.configure(text=nombres.get(accion, accion))
        velocidad = max(0.25, min(10.0, self.velocidad.get()))
        self.detalle.configure(text=f"Línea {linea}" + (f" · velocidad {velocidad:.1f}x" if accion == "esperar" else ""))
        self._escribir(f"Línea {linea}: {nombres.get(accion, accion)}")
        if accion == "esperar":
            try:
                demora = max(1, int(float(valor) * 1000 / velocidad))
            except (TypeError, ValueError):
                demora = max(1, int(1000 / velocidad))
        else:
            demora = 420
        self.raiz.after(demora, respuesta.set)

    def _mostrar_entrada(self, linea: int, respuesta: dict) -> None:
        while True:
            texto = simpledialog.askstring("Entrada de DeLuX", f"Línea {linea}: ingresa un número", parent=self.raiz)
            if texto is None:
                respuesta["cancelado"] = True
                break
            try:
                respuesta["valor"] = float(texto) if "." in texto else int(texto)
                break
            except ValueError:
                messagebox.showerror("Entrada inválida", f"Línea {linea}: Regla S4: la entrada debe ser numérica.", parent=self.raiz)
        respuesta["evento"].set()

    def _detener(self) -> None:
        self.detener.set()
        self.boton_detener.configure(state="disabled")
        self.estado.configure(text="Deteniendo…")

    def _terminar(self, mensaje: str) -> None:
        self.ocupado = False
        self.estado.configure(text=mensaje)
        self.detalle.configure(text=self.ruta.name if self.ruta else "")
        self.boton_iniciar.configure(state="normal" if self.codigo else "disabled")
        self.boton_abrir.configure(state="normal")
        self.boton_detener.configure(state="disabled")
        self._escribir(mensaje)

    def _escribir(self, mensaje: str) -> None:
        self.registro.configure(state="normal")
        self.registro.insert("end", mensaje + "\n")
        self.registro.see("end")
        self.registro.configure(state="disabled")

    def _cerrar(self) -> None:
        self.detener.set()
        self.raiz.destroy()


class InterrupcionSimulador(Exception):
    pass


def main() -> None:
    archivo = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    raiz = tk.Tk()
    SimuladorDeLuX(raiz, archivo)
    raiz.mainloop()


if __name__ == "__main__":
    main()
