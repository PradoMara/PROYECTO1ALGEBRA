#!/usr/bin/env python3
"""
Demostración del sistema integrado de parser y graficador.
Este archivo muestra cómo usar las funciones de graficos.py con el parser integrado.
"""

import sys
import os

# Añadir el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from graphics.graficos import (
    graficar_funcion_desde_texto,
    graficar_con_analisis,
    evaluar_funcion_en_punto,
    demo_graficador
)
from domain.parser import parse_function


def ejemplo_basico():
    """Ejemplo básico de graficado desde texto."""
    print("=== EJEMPLO BÁSICO ===")
    
    # Función cuadrática simple
    expresion = "x**2 - 4*x + 3"
    print(f"Graficando: f(x) = {expresion}")
    
    success, mensaje, parse_result = graficar_funcion_desde_texto(
        expresion, 
        rango_x=(-1, 5)
    )
    
    print(f"Resultado: {mensaje}")
    if parse_result.warnings:
        print("Advertencias:", parse_result.warnings)
    
    return success


def ejemplo_con_intersecciones():
    """Ejemplo con análisis automático de intersecciones."""
    print("\n=== EJEMPLO CON ANÁLISIS ===")
    
    expresion = "x**3 - 2*x**2 - x + 2"
    print(f"Analizando y graficando: f(x) = {expresion}")
    
    # Usar la función que incluye análisis automático
    graficar_con_analisis(
        expresion,
        rango_x=(-2, 3),
        mostrar_intersecciones=True,
        evaluar_en=0  # Evaluar en x=0
    )


def ejemplo_funciones_trigonometricas():
    """Ejemplo con funciones trigonométricas."""
    print("\n=== FUNCIONES TRIGONOMÉTRICAS ===")
    
    funciones = [
        ("sin(x)", "Función seno"),
        ("cos(x) + sin(2*x)", "Combinación trigonométrica"),
        ("tan(x)", "Función tangente")
    ]
    
    for expr, descripcion in funciones:
        print(f"\n{descripcion}: f(x) = {expr}")
        
        success, mensaje, _ = graficar_funcion_desde_texto(
            expr,
            rango_x=(-2*3.14159, 2*3.14159)  # aproximadamente -2π a 2π
        )
        
        print(f"Estado: {mensaje}")
        
        if success:
            input("Presiona Enter para continuar...")


def ejemplo_funciones_con_restricciones():
    """Ejemplo con funciones que tienen restricciones de dominio."""
    print("\n=== FUNCIONES CON RESTRICCIONES ===")
    
    funciones_restringidas = [
        ("1/(x-2)", "Función racional con asíntota vertical"),
        ("sqrt(x)", "Raíz cuadrada (dominio x >= 0)"),
        ("log(x)", "Logaritmo natural (dominio x > 0)"),
        ("1/(x**2 - 4)", "Función con múltiples asíntotas")
    ]
    
    for expr, descripcion in funciones_restringidas:
        print(f"\n{descripcion}: f(x) = {expr}")
        
        # Parsear primero para ver las advertencias
        parse_result = parse_function(expr, allowed_vars=['x'])
        
        if parse_result.warnings:
            print("Restricciones de dominio detectadas:")
            for warning in parse_result.warnings:
                print(f"  - {warning}")
        
        success, mensaje, _ = graficar_funcion_desde_texto(
            expr,
            rango_x=(-5, 5)
        )
        
        print(f"Estado: {mensaje}")
        
        if success:
            input("Presiona Enter para continuar...")


def ejemplo_evaluacion_puntos():
    """Ejemplo de evaluación de funciones en puntos específicos."""
    print("\n=== EVALUACIÓN EN PUNTOS ===")
    
    expresion = "x**3 - 2*x + 1"
    print(f"Función: f(x) = {expresion}")
    
    puntos_a_evaluar = [-2, -1, 0, 1, 2]
    
    for x_val in puntos_a_evaluar:
        success, resultado, mensaje = evaluar_funcion_en_punto(expresion, x_val)
        
        if success:
            print(f"  {mensaje}")
        else:
            print(f"  Error evaluando en x={x_val}: {mensaje}")


def menu_interactivo():
    """Menú interactivo para probar el sistema."""
    print("\n=== MODO INTERACTIVO ===")
    print("Introduce expresiones matemáticas para graficar")
    print("Ejemplos válidos:")
    print("  - x**2 + 2*x + 1")
    print("  - sin(x) + cos(2*x)")
    print("  - 1/(x-1)")
    print("  - sqrt(x**2 + 1)")
    print("  - exp(-x**2)")
    print("\nEscribe 'salir' para terminar")
    
    while True:
        expresion = input("\nIngresa una función f(x) = ").strip()
        
        if expresion.lower() in ['salir', 'exit', 'quit']:
            break
        
        if not expresion:
            continue
        
        try:
            # Preguntar por el rango
            rango_input = input("Rango de x (formato: min,max) [default: -10,10]: ").strip()
            if rango_input:
                min_x, max_x = map(float, rango_input.split(','))
                rango_x = (min_x, max_x)
            else:
                rango_x = (-10, 10)
            
            # Preguntar si quiere análisis
            analisis = input("¿Incluir análisis de intersecciones? (s/n) [default: s]: ").strip().lower()
            if analisis in ['n', 'no']:
                success, mensaje, _ = graficar_funcion_desde_texto(expresion, rango_x=rango_x)
                print(mensaje)
            else:
                graficar_con_analisis(expresion, rango_x=rango_x)
                
        except Exception as e:
            print(f"Error: {e}")


def main():
    """Función principal con menú de opciones."""
    print("SISTEMA INTEGRADO DE PARSER Y GRAFICADOR")
    print("=" * 50)
    
    opciones = {
        '1': ("Ejemplo básico", ejemplo_basico),
        '2': ("Ejemplo con intersecciones", ejemplo_con_intersecciones),
        '3': ("Funciones trigonométricas", ejemplo_funciones_trigonometricas),
        '4': ("Funciones con restricciones", ejemplo_funciones_con_restricciones),
        '5': ("Evaluación en puntos", ejemplo_evaluacion_puntos),
        '6': ("Demo completo", demo_graficador),
        '7': ("Modo interactivo", menu_interactivo),
        '0': ("Salir", None)
    }
    
    while True:
        print("\nOpciones disponibles:")
        for key, (descripcion, _) in opciones.items():
            print(f"  {key}. {descripcion}")
        
        eleccion = input("\nSelecciona una opción: ").strip()
        
        if eleccion == '0':
            print("¡Hasta luego!")
            break
        
        if eleccion in opciones and opciones[eleccion][1]:
            try:
                opciones[eleccion][1]()
            except KeyboardInterrupt:
                print("\nOperación cancelada.")
            except Exception as e:
                print(f"Error: {e}")
        else:
            print("Opción no válida.")


if __name__ == "__main__":
    main()