#!/usr/bin/env python3
"""Lexer, parser, análisis semántico y generador Python para DeLuX."""
from __future__ import annotations

import argparse
import ast
import re
import sys
from dataclasses import dataclass
from pathlib import Path


class ErrorDeLuX(Exception):
    def __init__(self, fase: str, mensaje: str, linea: int, columna: int):
        super().__init__(mensaje)
        self.fase, self.mensaje = fase, mensaje
        self.linea, self.columna = linea, columna

    def __str__(self) -> str:
        return f"{self.fase} — Línea {self.linea}, columna {self.columna}: {self.mensaje}"


@dataclass(frozen=True)
class Token:
    tipo: str
    valor: str
    linea: int
    columna: int


PALABRAS = {
    "mostrar": "MOSTRAR", "leer": "LEER", "encender": "ENCENDER",
    "esperar": "ESPERAR", "cambiar": "CAMBIAR", "apagar": "APAGAR",
    "rojo": "COLOR", "amarillo": "COLOR", "verde": "COLOR",
    "si": "SI", "entonces": "ENTONCES", "sino": "SINO", "fin": "FIN",
    "repetir": "REPETIR", "veces": "VECES", "mientras": "MIENTRAS",
    "hacer": "HACER", "y": "Y", "o": "O", "no": "NO",
    "verdadero": "LOGICO", "falso": "LOGICO",
}
PATRON = re.compile(
    r'(?P<ESPACIO>[ \t\r]+)|(?P<TEXTO>"(?:[^"\\]|\\.)*")|'
    r'(?P<NUMERO>\d+(?:\.\d+)?)|(?P<ID>[A-Za-z_][A-Za-z0-9_]*)|'
    r'(?P<OP>==|!=|>=|<=|[=+*/()<>-])'
)


def analizar_lexico(texto: str) -> list[Token]:
    tokens: list[Token] = []
    for num_linea, linea in enumerate(texto.splitlines(), 1):
        i = 0
        while i < len(linea):
            if linea[i] == "#":
                break
            coincidencia = PATRON.match(linea, i)
            if not coincidencia:
                raise ErrorDeLuX("Error léxico", f"carácter no reconocido {linea[i]!r}", num_linea, i + 1)
            valor = coincidencia.group()
            tipo = coincidencia.lastgroup
            if tipo != "ESPACIO":
                if tipo == "ID":
                    tipo = PALABRAS.get(valor, "ID")
                elif tipo == "OP":
                    tipo = {"=": "IGUAL", "+": "MAS", "-": "MENOS", "*": "POR", "/": "DIV",
                            "(": "PAR_IZQ", ")": "PAR_DER", ">": "MAYOR", "<": "MENOR",
                            ">=": "MAYOR_IGUAL", "<=": "MENOR_IGUAL", "==": "IGUAL_IGUAL",
                            "!=": "DIFERENTE"}[valor]
                tokens.append(Token(tipo, valor, num_linea, i + 1))
            i = coincidencia.end()
        tokens.append(Token("NL", "\n", num_linea, len(linea) + 1))
    tokens.append(Token("EOF", "", max(1, len(texto.splitlines()) + 1), 1))
    return tokens


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens, self.i = tokens, 0

    @property
    def actual(self) -> Token:
        return self.tokens[self.i]

    def tomar(self, *tipos: str, mensaje: str | None = None) -> Token:
        token = self.actual
        if token.tipo not in tipos:
            esperados = " o ".join(t.lower().replace("_", " ") for t in tipos)
            recibido = "fin de archivo" if token.tipo == "EOF" else repr(token.valor)
            raise ErrorDeLuX("Error sintáctico", mensaje or f"se esperaba {esperados}; se encontró {recibido}", token.linea, token.columna)
        self.i += 1
        return token

    def saltar_lineas(self) -> None:
        while self.actual.tipo == "NL":
            self.i += 1

    def programa(self, cierres: tuple[str, ...] = ("EOF",)) -> None:
        self.saltar_lineas()
        while self.actual.tipo not in cierres:
            if self.actual.tipo == "EOF":
                self.tomar(*cierres)
            self.sentencia()
            if self.actual.tipo not in ("NL", *cierres):
                t = self.actual
                raise ErrorDeLuX("Error sintáctico", "se esperaba fin de línea", t.linea, t.columna)
            self.saltar_lineas()

    def bloque(self, *cierres: str) -> None:
        self.programa((*cierres, "EOF"))

    def sentencia(self) -> None:
        t = self.actual
        if t.tipo == "ID":
            self.tomar("ID"); self.tomar("IGUAL"); self.expr(); return
        if t.tipo in ("MOSTRAR", "ESPERAR"):
            self.tomar(t.tipo); self.expr(); return
        if t.tipo == "LEER":
            self.tomar("LEER"); self.tomar("ID"); return
        if t.tipo == "ENCENDER":
            self.tomar("ENCENDER"); self.tomar("COLOR"); return
        if t.tipo in ("CAMBIAR", "APAGAR"):
            self.tomar(t.tipo); return
        if t.tipo == "SI":
            self.tomar("SI"); self.expr(); self.tomar("ENTONCES", mensaje="se esperaba 'entonces' después de la condición")
            self.tomar("NL", mensaje="se esperaba un salto de línea después de 'entonces'"); self.saltar_lineas()
            self.bloque("SINO", "FIN")
            if self.actual.tipo == "SINO":
                self.tomar("SINO"); self.tomar("NL", mensaje="se esperaba un salto de línea después de 'sino'"); self.saltar_lineas()
                self.bloque("FIN")
            self.tomar("FIN", mensaje="se esperaba 'fin' para cerrar 'si'"); return
        if t.tipo in ("REPETIR", "MIENTRAS"):
            tipo = self.tomar(t.tipo).tipo
            self.expr()
            self.tomar("VECES" if tipo == "REPETIR" else "HACER",
                       mensaje="se esperaba 'veces'" if tipo == "REPETIR" else "se esperaba 'hacer'")
            self.tomar("NL", mensaje="se esperaba un salto de línea después de la cabecera"); self.saltar_lineas()
            self.bloque("FIN"); self.tomar("FIN", mensaje="se esperaba 'fin' para cerrar el bloque"); return
        raise ErrorDeLuX("Error sintáctico", "se esperaba una instrucción", t.linea, t.columna)

    def expr(self) -> None: self.disyuncion()
    def disyuncion(self) -> None:
        self.conjuncion()
        while self.actual.tipo == "O": self.tomar("O"); self.conjuncion()
    def conjuncion(self) -> None:
        self.negacion()
        while self.actual.tipo == "Y": self.tomar("Y"); self.negacion()
    def negacion(self) -> None:
        if self.actual.tipo == "NO": self.tomar("NO"); self.negacion()
        else: self.comparacion()
    def comparacion(self) -> None:
        self.suma()
        if self.actual.tipo in ("MAYOR", "MENOR", "MAYOR_IGUAL", "MENOR_IGUAL", "IGUAL_IGUAL", "DIFERENTE"):
            self.i += 1; self.suma()
            if self.actual.tipo in ("MAYOR", "MENOR", "MAYOR_IGUAL", "MENOR_IGUAL", "IGUAL_IGUAL", "DIFERENTE"):
                t = self.actual
                raise ErrorDeLuX("Error sintáctico", "no se pueden encadenar comparaciones", t.linea, t.columna)
    def suma(self) -> None:
        self.producto()
        while self.actual.tipo in ("MAS", "MENOS"): self.i += 1; self.producto()
    def producto(self) -> None:
        self.unario()
        while self.actual.tipo in ("POR", "DIV"): self.i += 1; self.unario()
    def unario(self) -> None:
        if self.actual.tipo == "MENOS": self.tomar("MENOS"); self.unario()
        else: self.primario()
    def primario(self) -> None:
        if self.actual.tipo in ("NUMERO", "TEXTO", "LOGICO", "ID"):
            self.i += 1; return
        if self.actual.tipo == "PAR_IZQ":
            self.tomar("PAR_IZQ"); self.expr(); self.tomar("PAR_DER"); return
        t = self.actual
        raise ErrorDeLuX("Error sintáctico", "se esperaba un número, texto, valor lógico, variable o expresión entre paréntesis", t.linea, t.columna)


@dataclass
class Nodo:
    tipo: str
    token: Token
    valor: str | None = None
    hijos: list[Nodo] | None = None


class ConstructorAST(Parser):
    """Construye el árbol que consumen las fases semántica y de generación."""
    def programa_ast(self, cierres: tuple[str, ...] = ("EOF",)) -> list[Nodo]:
        resultado: list[Nodo] = []
        self.saltar_lineas()
        while self.actual.tipo not in cierres:
            if self.actual.tipo == "EOF":
                self.tomar(*cierres)
            resultado.append(self.sentencia_ast())
            if self.actual.tipo not in ("NL", *cierres):
                t = self.actual
                raise ErrorDeLuX("Error sintáctico", "se esperaba fin de línea", t.linea, t.columna)
            self.saltar_lineas()
        return resultado

    def bloque_ast(self, *cierres: str) -> list[Nodo]:
        return self.programa_ast((*cierres, "EOF"))

    def sentencia_ast(self) -> Nodo:
        t = self.actual
        if t.tipo == "ID":
            nombre = self.tomar("ID"); self.tomar("IGUAL")
            return Nodo("asignar", nombre, nombre.valor, [self.expr_ast()])
        if t.tipo in ("MOSTRAR", "ESPERAR"):
            op = self.tomar(t.tipo)
            return Nodo(t.tipo.lower(), op, hijos=[self.expr_ast()])
        if t.tipo == "LEER":
            op = self.tomar("LEER"); nombre = self.tomar("ID")
            return Nodo("leer", op, nombre.valor)
        if t.tipo == "ENCENDER":
            op = self.tomar("ENCENDER"); color = self.tomar("COLOR")
            return Nodo("encender", op, color.valor)
        if t.tipo in ("CAMBIAR", "APAGAR"):
            op = self.tomar(t.tipo)
            return Nodo(t.tipo.lower(), op)
        if t.tipo == "SI":
            op = self.tomar("SI"); condicion = self.expr_ast()
            self.tomar("ENTONCES", mensaje="se esperaba 'entonces' después de la condición")
            self.tomar("NL", mensaje="se esperaba un salto de línea después de 'entonces'"); self.saltar_lineas()
            verdadero = self.bloque_ast("SINO", "FIN")
            falso: list[Nodo] = []
            if self.actual.tipo == "SINO":
                self.tomar("SINO"); self.tomar("NL", mensaje="se esperaba un salto de línea después de 'sino'"); self.saltar_lineas()
                falso = self.bloque_ast("FIN")
            self.tomar("FIN", mensaje="se esperaba 'fin' para cerrar 'si'")
            return Nodo("si", op, hijos=[condicion, *verdadero, Nodo("sino", op, hijos=falso)])
        if t.tipo in ("REPETIR", "MIENTRAS"):
            op = self.tomar(t.tipo); cantidad_o_condicion = self.expr_ast()
            self.tomar("VECES" if t.tipo == "REPETIR" else "HACER",
                       mensaje="se esperaba 'veces'" if t.tipo == "REPETIR" else "se esperaba 'hacer'")
            self.tomar("NL", mensaje="se esperaba un salto de línea después de la cabecera"); self.saltar_lineas()
            cuerpo = self.bloque_ast("FIN")
            self.tomar("FIN", mensaje="se esperaba 'fin' para cerrar el bloque")
            return Nodo("repetir" if t.tipo == "REPETIR" else "mientras", op,
                        hijos=[cantidad_o_condicion, *cuerpo])
        raise ErrorDeLuX("Error sintáctico", "se esperaba una instrucción", t.linea, t.columna)

    def expr_ast(self) -> Nodo:
        return self.disyuncion_ast()

    def binaria(self, siguiente, operadores: dict[str, str]) -> Nodo:
        izquierda = siguiente()
        while self.actual.tipo in operadores:
            op = self.actual; self.i += 1
            derecha = siguiente()
            izquierda = Nodo("binaria", op, operadores[op.tipo], [izquierda, derecha])
        return izquierda

    def disyuncion_ast(self) -> Nodo:
        return self.binaria(self.conjuncion_ast, {"O": "or"})

    def conjuncion_ast(self) -> Nodo:
        return self.binaria(self.negacion_ast, {"Y": "and"})

    def negacion_ast(self) -> Nodo:
        if self.actual.tipo == "NO":
            op = self.tomar("NO")
            return Nodo("unaria", op, "not", [self.negacion_ast()])
        return self.comparacion_ast()

    def comparacion_ast(self) -> Nodo:
        izquierda = self.suma_ast()
        ops = {"MAYOR": ">", "MENOR": "<", "MAYOR_IGUAL": ">=", "MENOR_IGUAL": "<=",
               "IGUAL_IGUAL": "==", "DIFERENTE": "!="}
        if self.actual.tipo in ops:
            op = self.actual; self.i += 1
            derecha = self.suma_ast()
            if self.actual.tipo in ops:
                raise ErrorDeLuX("Error sintáctico", "no se pueden encadenar comparaciones", self.actual.linea, self.actual.columna)
            return Nodo("binaria", op, ops[op.tipo], [izquierda, derecha])
        return izquierda

    def suma_ast(self) -> Nodo:
        return self.binaria(self.producto_ast, {"MAS": "+", "MENOS": "-"})

    def producto_ast(self) -> Nodo:
        return self.binaria(self.unario_ast, {"POR": "*", "DIV": "/"})

    def unario_ast(self) -> Nodo:
        if self.actual.tipo == "MENOS":
            op = self.tomar("MENOS")
            return Nodo("unaria", op, "-", [self.unario_ast()])
        return self.primario_ast()

    def primario_ast(self) -> Nodo:
        t = self.actual
        if t.tipo in ("NUMERO", "TEXTO", "LOGICO", "ID"):
            self.i += 1
            return Nodo("literal" if t.tipo != "ID" else "variable", t, t.tipo)
        if t.tipo == "PAR_IZQ":
            self.tomar("PAR_IZQ"); expresion = self.expr_ast(); self.tomar("PAR_DER")
            return expresion
        raise ErrorDeLuX("Error sintáctico", "se esperaba un número, texto, valor lógico, variable o expresión entre paréntesis", t.linea, t.columna)


def valor_constante(nodo: Nodo, variables: dict[str, tuple[bool, object]] | None = None):
    """Devuelve (es_constante, valor); no evalúa variables ni expresiones peligrosas."""
    if nodo.tipo == "literal":
        if nodo.valor == "NUMERO": return True, float(nodo.token.valor) if "." in nodo.token.valor else int(nodo.token.valor)
        if nodo.valor == "TEXTO": return True, ast.literal_eval(nodo.token.valor)
        return True, nodo.token.valor == "verdadero"
    if nodo.tipo == "variable" and variables is not None:
        return variables.get(nodo.token.valor, (False, None))
    if nodo.tipo == "unaria":
        ok, valor = valor_constante(nodo.hijos[0], variables)
        if ok:
            return True, (not valor) if nodo.valor == "not" else -valor
    if nodo.tipo == "binaria":
        a_ok, a = valor_constante(nodo.hijos[0], variables); b_ok, b = valor_constante(nodo.hijos[1], variables)
        if a_ok and b_ok:
            try:
                return True, {"+": lambda: a + b, "-": lambda: a - b, "*": lambda: a * b,
                              "/": lambda: a / b, ">": lambda: a > b, "<": lambda: a < b,
                              ">=": lambda: a >= b, "<=": lambda: a <= b, "==": lambda: a == b,
                              "!=": lambda: a != b, "and": lambda: a and b, "or": lambda: a or b}[nodo.valor]()
            except (ArithmeticError, TypeError):
                return False, None
    return False, None


class AnalizadorSemantico:
    REGLAS = {
        "S1": "toda variable debe definirse antes de usarse",
        "S2": "esperar requiere un tiempo numerico mayor que cero",
        "S3": "repetir requiere una cantidad entera no negativa",
        "S4": "las operaciones y condiciones deben respetar sus tipos",
        "S5": "esperar y cambiar requieren una luz encendida",
    }

    def __init__(self):
        self.simbolos: dict[str, str] = {}
        self.constantes: dict[str, tuple[bool, object]] = {}
        self.luz: str | None = None

    def error(self, regla: str, token: Token, detalle: str) -> None:
        raise ErrorDeLuX("Error semántico", f"Regla {regla} ({self.REGLAS[regla]}): {detalle}", token.linea, token.columna)

    def tipo_expr(self, nodo: Nodo) -> str:
        if nodo.tipo == "literal":
            return {"NUMERO": "numero", "TEXTO": "texto", "LOGICO": "logico"}[nodo.valor]
        if nodo.tipo == "variable":
            if nodo.token.valor not in self.simbolos:
                self.error("S1", nodo.token, f"la variable '{nodo.token.valor}' no está definida")
            return self.simbolos[nodo.token.valor]
        if nodo.tipo == "unaria":
            t = self.tipo_expr(nodo.hijos[0])
            if nodo.valor == "not" and t == "logico": return "logico"
            if nodo.valor == "-" and t == "numero": return "numero"
            self.error("S4", nodo.token, f"el operador '{nodo.valor}' no acepta el tipo {t}")
        if nodo.tipo == "binaria":
            izq = self.tipo_expr(nodo.hijos[0]); der = self.tipo_expr(nodo.hijos[1]); op = nodo.valor
            if op in ("and", "or") and izq == der == "logico": return "logico"
            if op in ("+", "-", "*", "/"):
                if izq == der == "numero":
                    if op == "/":
                        conocido, denominador = valor_constante(nodo.hijos[1], self.constantes)
                        if conocido and denominador == 0:
                            self.error("S4", nodo.token, "no se puede dividir por cero")
                    return "numero"
                if op == "+" and izq == der == "texto": return "texto"
                self.error("S4", nodo.token, f"'{op}' no puede combinar {izq} con {der}")
            if op in (">", "<", ">=", "<=") and izq == der == "numero": return "logico"
            if op in ("==", "!=") and izq == der: return "logico"
            self.error("S4", nodo.token, f"comparación incompatible entre {izq} y {der}")
        raise AssertionError(f"Nodo de expresión inesperado: {nodo.tipo}")

    def constante_numero(self, nodo: Nodo) -> tuple[bool, float | int | None]:
        if self.tipo_expr(nodo) != "numero":
            self.error("S4", nodo.token, "el tiempo de 'esperar' debe ser numérico")
        conocido, valor = valor_constante(nodo, self.constantes)
        return conocido, valor

    def bloque(self, sentencias: list[Nodo]) -> None:
        for nodo in sentencias:
            if nodo.tipo == "asignar":
                tipo = self.tipo_expr(nodo.hijos[0]); self.simbolos[nodo.valor] = tipo
                self.constantes[nodo.valor] = valor_constante(nodo.hijos[0], self.constantes)
            elif nodo.tipo == "leer":
                self.simbolos[nodo.valor] = "numero"
                self.constantes[nodo.valor] = (False, None)
            elif nodo.tipo == "mostrar":
                self.tipo_expr(nodo.hijos[0])
            elif nodo.tipo == "esperar":
                conocido, valor = self.constante_numero(nodo.hijos[0])
                if conocido and valor <= 0:
                    self.error("S2", nodo.token, f"esperar recibió {valor}; el tiempo debe ser mayor que cero")
                if self.luz is None or self.luz == "desconocido":
                    self.error("S5", nodo.token, "encienda una luz antes de esperar")
            elif nodo.tipo == "encender":
                self.luz = nodo.valor
            elif nodo.tipo == "cambiar":
                if self.luz is None or self.luz == "desconocido":
                    self.error("S5", nodo.token, "encienda una luz antes de cambiar")
                ciclo = ("verde", "amarillo", "rojo")
                self.luz = ciclo[(ciclo.index(self.luz) + 1) % len(ciclo)]
            elif nodo.tipo == "apagar":
                self.luz = None
            elif nodo.tipo == "si":
                if self.tipo_expr(nodo.hijos[0]) != "logico":
                    self.error("S4", nodo.token, "la condición de 'si' debe ser lógica")
                antes = self.simbolos.copy()
                constantes_antes = self.constantes.copy()
                luz_antes = self.luz
                rama_si = nodo.hijos[1:-1]
                rama_sino = nodo.hijos[-1].hijos or []
                self.simbolos = antes.copy(); self.constantes = constantes_antes.copy(); self.luz = luz_antes
                self.bloque(rama_si); simbolos_si = self.simbolos.copy(); constantes_si = self.constantes.copy(); luz_si = self.luz
                self.simbolos = antes.copy(); self.constantes = constantes_antes.copy(); self.luz = luz_antes
                self.bloque(rama_sino); simbolos_sino = self.simbolos.copy(); constantes_sino = self.constantes.copy(); luz_sino = self.luz
                comunes = set(simbolos_si) & set(simbolos_sino)
                self.simbolos = {k: simbolos_si[k] for k in comunes if simbolos_si[k] == simbolos_sino[k]}
                self.constantes = {k: constantes_si[k] for k in self.simbolos
                                   if constantes_si.get(k) == constantes_sino.get(k)}
                self.luz = luz_si if luz_si == luz_sino else "desconocido"
            elif nodo.tipo == "repetir":
                cantidad = nodo.hijos[0]
                if self.tipo_expr(cantidad) != "numero":
                    self.error("S3", nodo.token, "la cantidad de repeticiones debe ser numérica")
                conocido, valor = valor_constante(cantidad, self.constantes)
                if conocido and (valor < 0 or int(valor) != valor):
                    self.error("S3", nodo.token, f"la cantidad {valor} debe ser un entero no negativo")
                antes = self.simbolos.copy(); constantes_antes = self.constantes.copy(); luz_antes = self.luz
                self.bloque(nodo.hijos[1:]); despues = self.simbolos.copy(); constantes_despues = self.constantes.copy(); luz_despues = self.luz
                self.simbolos = antes; self.constantes = constantes_antes
                self.luz = luz_antes if luz_antes == luz_despues else "desconocido"
                if conocido and valor > 0:
                    self.simbolos.update({k: v for k, v in despues.items() if k in antes and antes[k] == v})
                    for k in antes:
                        if constantes_despues.get(k) != constantes_antes.get(k):
                            self.constantes[k] = (False, None)
            elif nodo.tipo == "mientras":
                if self.tipo_expr(nodo.hijos[0]) != "logico":
                    self.error("S4", nodo.token, "la condición de 'mientras' debe ser lógica")
                antes = self.simbolos.copy(); constantes_antes = self.constantes.copy(); luz_antes = self.luz
                self.bloque(nodo.hijos[1:]); constantes_despues = self.constantes.copy(); luz_despues = self.luz
                self.simbolos = antes; self.constantes = constantes_antes
                for k in antes:
                    if constantes_despues.get(k) != constantes_antes.get(k):
                        self.constantes[k] = (False, None)
                self.luz = luz_antes if luz_antes == luz_despues else "desconocido"


class GeneradorPython:
    def expresion(self, nodo: Nodo) -> str:
        if nodo.tipo == "literal":
            if nodo.valor == "LOGICO": return "True" if nodo.token.valor == "verdadero" else "False"
            if nodo.valor == "TEXTO": return repr(ast.literal_eval(nodo.token.valor))
            return nodo.token.valor
        if nodo.tipo == "variable": return self.nombre(nodo.token.valor)
        if nodo.tipo == "unaria": return f"({nodo.valor} {self.expresion(nodo.hijos[0])})"
        if nodo.tipo == "binaria":
            if nodo.valor == "/":
                return f"_dividir({self.expresion(nodo.hijos[0])}, {self.expresion(nodo.hijos[1])}, {nodo.token.linea})"
            return f"({self.expresion(nodo.hijos[0])} {nodo.valor} {self.expresion(nodo.hijos[1])})"
        raise AssertionError(nodo.tipo)

    @staticmethod
    def nombre(nombre: str) -> str:
        return f"_v_{nombre}"

    def sentencias(self, nodos: list[Nodo], nivel: int = 0) -> list[str]:
        salida: list[str] = []; sangria = "    " * nivel
        for n in nodos:
            salida.append(f"{sangria}# DeLuX linea {n.token.linea}")
            if n.tipo == "asignar": salida.append(f"{sangria}{self.nombre(n.valor)} = {self.expresion(n.hijos[0])}")
            elif n.tipo == "leer": salida.append(f"{sangria}{self.nombre(n.valor)} = _leer_numero({n.token.linea})")
            elif n.tipo == "mostrar": salida.append(f"{sangria}print({self.expresion(n.hijos[0])})")
            elif n.tipo == "encender": salida.append(f"{sangria}semaforo.encender({n.valor!r}, {n.token.linea})")
            elif n.tipo == "esperar": salida.append(f"{sangria}semaforo.esperar({self.expresion(n.hijos[0])}, {n.token.linea})")
            elif n.tipo == "cambiar": salida.append(f"{sangria}semaforo.cambiar({n.token.linea})")
            elif n.tipo == "apagar": salida.append(f"{sangria}semaforo.apagar({n.token.linea})")
            elif n.tipo == "si":
                salida.append(f"{sangria}if {self.expresion(n.hijos[0])}:")
                rama_si = self.sentencias(n.hijos[1:-1], nivel + 1) or ["    " * (nivel + 1) + "pass"]
                salida.extend(rama_si)
                rama_sino = n.hijos[-1].hijos or []
                if rama_sino:
                    salida.append(f"{sangria}else:"); salida.extend(self.sentencias(rama_sino, nivel + 1))
            elif n.tipo == "repetir":
                salida.append(f"{sangria}for _ in _repetir({self.expresion(n.hijos[0])}, {n.token.linea}):")
                salida.extend(self.sentencias(n.hijos[1:], nivel + 1) or ["    " * (nivel + 1) + "pass"])
            elif n.tipo == "mientras":
                salida.append(f"{sangria}while {self.expresion(n.hijos[0])}:")
                salida.extend(self.sentencias(n.hijos[1:], nivel + 1) or ["    " * (nivel + 1) + "pass"])
        return salida

    def generar(self, nodos: list[Nodo]) -> str:
        codigo = '''# Código generado por DeLuX. La espera se registra en terminal y puede animarse en la interfaz.
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
'''
        cuerpo = self.sentencias(nodos)
        return codigo + ("\n".join(cuerpo) if cuerpo else "pass") + "\n"


def compilar_fuente(texto: str) -> str:
    """Ejecuta lexer, parser y análisis semántico, y devuelve Python validado."""
    tokens = analizar_lexico(texto)
    nodos = ConstructorAST(tokens).programa_ast()
    AnalizadorSemantico().bloque(nodos)
    codigo = GeneradorPython().generar(nodos)
    compile(codigo, "<programa DeLuX>", "exec")
    return codigo


def analizar(texto: str) -> tuple[list[Token], None]:
    tokens = analizar_lexico(texto)
    Parser(tokens).programa()
    return tokens, None


def main() -> int:
    cli = argparse.ArgumentParser(description="Analiza léxica y sintácticamente un programa DeLuX.")
    cli.add_argument("archivo", type=Path, help="archivo .dlx que se analizará")
    cli.add_argument("--tokens", action="store_true", help="mostrar tokens cuando el análisis léxico sea correcto")
    cli.add_argument("--solo-lexico", action="store_true", help="separar y mostrar tokens sin ejecutar el parser")
    cli.add_argument("--generar-python", type=Path, metavar="DESTINO", help="guardar la traducción Python ejecutable")
    args = cli.parse_args()
    try:
        texto = args.archivo.read_text(encoding="utf-8")
        tokens = analizar_lexico(texto)
    except OSError as exc:
        print(f"No se pudo leer el archivo: {exc}", file=sys.stderr); return 2
    except ErrorDeLuX as exc:
        print(exc); return 1
    if args.tokens or args.solo_lexico:
        for t in tokens:
            if t.tipo not in ("NL", "EOF"):
                print(f"{t.linea}:{t.columna}\t{t.tipo}\t{t.valor}")
    if args.solo_lexico:
        print(f"{args.archivo}: análisis léxico correcto.")
        return 0
    try:
        nodos = ConstructorAST(tokens).programa_ast()
        AnalizadorSemantico().bloque(nodos)
    except ErrorDeLuX as exc:
        print(exc); return 1
    print(f"{args.archivo}: análisis léxico, sintáctico y semántico correcto.")
    if args.generar_python:
        python = GeneradorPython().generar(nodos)
        try:
            compile(python, str(args.generar_python), "exec")
            args.generar_python.parent.mkdir(parents=True, exist_ok=True)
            args.generar_python.write_text(python, encoding="utf-8")
        except OSError as exc:
            print(f"No se pudo guardar el código generado: {exc}", file=sys.stderr); return 2
        print(f"Código Python generado en {args.generar_python}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
