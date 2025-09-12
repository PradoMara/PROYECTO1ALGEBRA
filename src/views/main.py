import sys
import os
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from tkinter import ttk
from typing import Optional

import sympy as sp

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Importar lógica de dominio y gráficos
from src.domain.parser import parse_function
from src.domain.analysis import AnalisisFuncion, x as sym_x
from src.graphics.graficos import graficar_funcion_desde_texto, evaluar_funcion_en_punto

# Configuración principal
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Analizador de Funciones - Proyecto Algebra")
        self.geometry("1100x720")
        self.minsize(950, 640)

        self.constrir_interfaz()

    # Interfaz
    def constrir_interfaz(self):
        container = ctk.CTkFrame(self)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        # Entradas
        entradas_frame = ctk.CTkFrame(container)
        entradas_frame.pack(fill="x", pady=5)

        label_funcion = ctk.CTkLabel(entradas_frame, text="f(x) =", font=("Arial", 15, "bold"))
        label_funcion.grid(row=0, column=0, padx=6, pady=8, sticky="e")

        self.entrada_funcion = ctk.CTkEntry(entradas_frame, width=500, placeholder_text="Ej: (x^2 - 1)/(x-2) + sin(x)")
        self.entrada_funcion.grid(row=0, column=1, padx=4, pady=8, sticky="w")

        label_x = ctk.CTkLabel(entradas_frame, text="x =", font=("Arial", 14))
        label_x.grid(row=0, column=2, padx=(30, 4), pady=8, sticky="e")
        self.entrada_x = ctk.CTkEntry(entradas_frame, width=100, placeholder_text="Opcional")
        self.entrada_x.grid(row=0, column=3, padx=4, pady=8)

        # rango x grafico
        label_rango_x = ctk.CTkLabel(entradas_frame, text="Rango X (Para el grafico):", font=("Arial", 14))
        label_rango_x.grid(row=1, column=0, padx=6, pady=4, sticky="e")
        self.entrada_xmin = ctk.CTkEntry(entradas_frame, width=90, placeholder_text="xmin")
        self.entrada_xmin.grid(row=1, column=1, sticky="w", padx=(4,2), pady=4)
        self.entrada_xmax = ctk.CTkEntry(entradas_frame, width=90, placeholder_text="xmax")
        self.entrada_xmax.grid(row=1, column=1, sticky="w", padx=(100,2), pady=4)

        # rango y grafico (opcional)
        label_rango_y = ctk.CTkLabel(entradas_frame, text="Rango Y (Opcional):", font=("Arial", 14))
        label_rango_y.grid(row=2, column=0, padx=6, pady=4, sticky="e")
        self.entrada_ymin = ctk.CTkEntry(entradas_frame, width=90, placeholder_text="ymin")
        self.entrada_ymin.grid(row=2, column=1, sticky="w", padx=(4,2), pady=4)
        self.entrada_ymax = ctk.CTkEntry(entradas_frame, width=90, placeholder_text="ymax")
        self.entrada_ymax.grid(row=2, column=1, sticky="w", padx=(100,2), pady=4)

        #Botones
        botones_frame = ctk.CTkFrame(container)
        botones_frame.pack(fill="x", pady=5)

        analizar_boton = ctk.CTkButton(botones_frame, text="Analizar", command=self.analizar)
        analizar_boton.pack(side="left", padx=6, pady=6)

        evaluar_boton = ctk.CTkButton(botones_frame, text="Evaluar f(x)", command=self.evaluar)
        evaluar_boton.pack(side="left", padx=6, pady=6)

        graficar_boton = ctk.CTkButton(botones_frame, text="Graficar", command=self.graficar)
        graficar_boton.pack(side="left", padx=6, pady=6)

        limpiar_boton = ctk.CTkButton(botones_frame, text="Limpiar", fg_color="gray30", command=self.clear_outputs)
        limpiar_boton.pack(side="left", padx=6, pady=6)

        # Resultados y adverttencias
        division_inferior = ctk.CTkFrame(container)
        division_inferior.pack(fill="both", expand=True)

        # lado izquierdo: resultados y advertencias
        frame_izquierda = ctk.CTkFrame(division_inferior)
        frame_izquierda.pack(side="left", fill="both", expand=True, padx=(0,5), pady=5)

        lbl_res = ctk.CTkLabel(frame_izquierda, text="Resultados y Análisis", font=("Arial", 16, "bold"))
        lbl_res.pack(anchor="w", padx=10, pady=(10,2))

        self.txt_resultados = tk.Text(frame_izquierda, wrap="word", height=20, font=("Consolas", 12))
        self.txt_resultados.pack(fill="both", expand=True, padx=10, pady=5)

        lbl_warn = ctk.CTkLabel(frame_izquierda, text="Advertencias / Mensajes", font=("Arial", 14))
        lbl_warn.pack(anchor="w", padx=10, pady=(8,2))
        self.txt_warnings = tk.Text(frame_izquierda, wrap="word", height=6, font=("Consolas", 11), fg="orange")
        self.txt_warnings.pack(fill="x", padx=10, pady=(0,10))

        # lado derecho: espacio para instrucciones
        frame_derecha = ctk.CTkFrame(division_inferior)
        frame_derecha.pack(side="left", fill="both", expand=True, padx=(5,0), pady=5)

        self.label_instrucciones = ctk.CTkLabel(frame_derecha, text="Usa 'Graficar' para mostrar la función en una ventana externa.\n\nPuedes especificar rangos X e Y personalizados para controlar mejor la visualización.", wraplength=420, font=("Arial", 14))
        self.label_instrucciones.pack(padx=20, pady=20)

        ayuda_texto = ("Formato soportado:\n"
                      " - Multiplicación implícita: 2x -> 2*x automático\n"
                      " - Potencias: usar ^ o **\n"
                      " - Funciones: sin, cos, tan, exp, log, sqrt, abs ...\n"
                      " - Constantes: pi, e\n"
                      " - Rango Y: Útil para funciones con asíntotas\n"
                      "Ejemplo: (x^2 - 1)/(x-2) + sin(x)")
        self.label_ayuda = ctk.CTkLabel(frame_derecha, text=ayuda_texto, justify="left", anchor="w")
        self.label_ayuda.pack(padx=15, pady=10, fill="x")

    # helpers
    def _get_function_text(self) -> str:
        return self.entrada_funcion.get().strip()

    def _append_result(self, text: str):
        self.txt_resultados.insert("end", text + "\n")
        self.txt_resultados.see("end")

    def _append_warning(self, text: str):
        self.txt_warnings.insert("end", text + "\n")
        self.txt_warnings.see("end")

    def clear_outputs(self):
        self.txt_resultados.delete("1.0", "end")
        self.txt_warnings.delete("1.0", "end")

    def _parse_expr(self) -> Optional[sp.Expr]:
        expr_str = self._get_function_text()
        if not expr_str:
            messagebox.showwarning("Entrada vacía", "Ingresa una función en el campo f(x).")
            return None
        result = parse_function(expr_str, allowed_vars=['x'], simplify_expression=True)
        self.txt_warnings.delete("1.0", "end")
        if not result.is_valid:
            self._append_warning(f"Error: {result.error}")
            return None
        for w in result.warnings:
            self._append_warning(w)
        return result.expr

    # Acciones de los botones
    def analizar(self):
        self._append_result("===== Análisis de función =====")
        expr = self._parse_expr()
        if expr is None:
            return
        try:
            analisis = AnalisisFuncion(expr)
            self._append_result(analisis.dominio())
            self._append_result("")
            self._append_result(analisis.recorrido())
            self._append_result("")
            self._append_result(analisis.intersecciones())
            self._append_result("---------------------------------------------")
        except Exception as e:
            self._append_warning(f"Error en análisis: {e}")

    def evaluar(self):
        expr_str = self._get_function_text()
        if not expr_str:
            messagebox.showwarning("Entrada vacía", "Ingresa una función primero.")
            return
        x_raw = self.entrada_x.get().strip()
        if not x_raw:
            messagebox.showinfo("Valor x faltante", "Ingresa un valor de x en el campo correspondiente.")
            return
        try:
            x_val = float(x_raw)
        except ValueError:
            messagebox.showerror("Valor inválido", "El valor de x debe ser numérico.")
            return
        success, resultado, mensaje = evaluar_funcion_en_punto(expr_str, x_val)
        if success:
            self._append_result(f"Evaluación: {mensaje}")
        else:
            self._append_warning(mensaje)

    def graficar(self):
        expr_str = self._get_function_text()
        if not expr_str:
            messagebox.showwarning("Entrada vacía", "Ingresa una función primero.")
            return
        
        # rango X
        xmin = self.entrada_xmin.get().strip()
        xmax = self.entrada_xmax.get().strip()
        try:
            if xmin and xmax:
                rxmin = float(xmin)
                rxmax = float(xmax)
                if rxmin >= rxmax:
                    raise ValueError("xmin debe ser menor que xmax")
                rango_x = (rxmin, rxmax)
            else:
                rango_x = (-10, 10)
        except ValueError as e:
            messagebox.showerror("Rango X inválido", f"Revisa los valores de rango X: {e}")
            return

        # rango Y (opcional)
        ymin = self.entrada_ymin.get().strip()
        ymax = self.entrada_ymax.get().strip()
        rango_y = None
        try:
            if ymin and ymax:
                rymin = float(ymin)
                rymax = float(ymax)
                if rymin >= rymax:
                    raise ValueError("ymin debe ser menor que ymax")
                rango_y = (rymin, rymax)
                self._append_result(f"Usando rango Y personalizado: [{rymin}, {rymax}]")
        except ValueError as e:
            messagebox.showerror("Rango Y inválido", f"Revisa los valores de rango Y: {e}")
            return

        # evaluar punto para resaltarlo si se ingresó
        punto = None
        x_raw = self.entrada_x.get().strip()
        if x_raw:
            try:
                x_val = float(x_raw)
                success_eval, res_eval, mensaje_eval = evaluar_funcion_en_punto(expr_str, x_val)
                if success_eval:
                    punto = (x_val, res_eval)
                    self._append_result(f"(Graficar) {mensaje_eval}")
                else:
                    self._append_warning(mensaje_eval)
            except ValueError:
                self._append_warning("No se pudo interpretar x para graficar el punto.")

        success, msg, parse_result = graficar_funcion_desde_texto(
            expr_str,
            rango_x=rango_x,
            rango_y=rango_y,  # Nuevo parámetro
            punto_evaluado=punto,
            intersecciones=None  
        )
        if not success:
            self._append_warning(msg)
        else:
            self._append_result(f"Gráfico: {msg}")


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
