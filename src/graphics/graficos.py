import matplotlib.pyplot as plt
import math 
import sys
import os
import re

# Añadir el directorio padre al path para importar el parser
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from domain.parser import parse_function, ParseResult


def detectar_discontinuidades(parse_result, rango_x, tolerancia=0.01):

    discontinuidades = []
    
    # Extraer puntos problemáticos de los warnings
    for warning in parse_result.warnings:
        if "≠ 0" in warning:

            matches_minus = re.findall(r'x\s*-\s*(\d+(?:\.\d+)?)\s*≠', warning)
            for match in matches_minus:
                try:
                    punto = float(match)  # x - 3 = 0 -> x = 3
                    if rango_x[0] <= punto <= rango_x[1]:
                        discontinuidades.append(punto)
                except ValueError:
                    continue
            
            # Patrón para "x + número"
            matches_plus = re.findall(r'x\s*\+\s*(\d+(?:\.\d+)?)\s*≠', warning)
            for match in matches_plus:
                try:
                    punto = -float(match)  # x + 3 = 0 -> x = -3
                    if rango_x[0] <= punto <= rango_x[1]:
                        discontinuidades.append(punto)
                except ValueError:
                    continue
            
            # Patrón para expresiones más complejas, extraer usando sympy
            try:
                import sympy as sp
                from sympy import Symbol, solve
                
                # Extraer la expresión antes de "≠ 0"
                expr_str = warning.split("≠")[0].strip()
                x = Symbol('x')
                
                # Intentar parsear y resolver la expresión
                expr = sp.sympify(expr_str)
                soluciones = solve(expr, x)
                
                for sol in soluciones:
                    if sol.is_real:
                        punto = float(sol.evalf())
                        if rango_x[0] <= punto <= rango_x[1]:
                            discontinuidades.append(punto)
                            
            except Exception:
                # Si falla el parsing con sympy, continuar
                pass
    
    return sorted(list(set(discontinuidades)))  # Eliminar duplicados y ordenar


def generar_intervalos_continuos(rango_x, discontinuidades, gap=0.01):

    if not discontinuidades:
        return [rango_x]
    
    intervalos = []
    inicio = rango_x[0]
    
    for disco in discontinuidades:
        if disco > rango_x[0] and disco < rango_x[1]:
            # Agregar intervalo antes de la discontinuidad
            if inicio < disco - gap:
                intervalos.append((inicio, disco - gap))
            # Siguiente intervalo comienza después de la discontinuidad
            inicio = disco + gap
    
    # Agregar último intervalo
    if inicio < rango_x[1]:
        intervalos.append((inicio, rango_x[1]))
    
    return intervalos


def generar_puntos_mejorado(Tipofuncion, LimitInfX, LimitSupX, discontinuidades=None, PuntosGraf=1000):

    if LimitInfX >= LimitSupX:
        return [], []
    
    # Si no hay discontinuidades, usar método original
    if not discontinuidades:
        return generar_puntos(Tipofuncion, LimitInfX, LimitSupX, PuntosGraf)
    
    # Generar intervalos continuos
    intervalos = generar_intervalos_continuos((LimitInfX, LimitSupX), discontinuidades)
    
    ValoresX_total = []
    ValoresY_total = []
    
    for i, (inicio, fin) in enumerate(intervalos):
        if inicio >= fin:
            continue
            
        # Generar puntos para este intervalo
        incremento = (fin - inicio) / PuntosGraf
        x = inicio
        
        intervalo_x = []
        intervalo_y = []
        
        while x <= fin:
            intervalo_x.append(x)
            try:
                y = Tipofuncion(x)
                if isinstance(y, complex) or y == float('inf') or y == float('-inf') or y == float('nan'):
                    intervalo_y.append(None)
                else:
                    # Filtrar valores muy grandes que podrían ser cerca de asíntotas
                    if abs(y) > 1e6:
                        intervalo_y.append(None)
                    else:
                        intervalo_y.append(y)
                        
            except (ValueError, ZeroDivisionError, TypeError):
                intervalo_y.append(None)
                
            x += incremento
        
        # Agregar este intervalo a los resultados totales
        ValoresX_total.extend(intervalo_x)
        ValoresY_total.extend(intervalo_y)
        
        # Agregar separador entre intervalos (excepto el último)
        if i < len(intervalos) - 1:
            ValoresX_total.append(None)
            ValoresY_total.append(None)
    
    return ValoresX_total, ValoresY_total


def generar_puntos(Tipofuncion, LimitInfX , LimitSupX , PuntosGraf=1000):
    
    ValoresX = []
    ValoresY = []
    
    if LimitInfX >= LimitSupX:
        return [] , []
    
    
    incremento = (LimitSupX - LimitInfX) / PuntosGraf
    
    x = LimitInfX
    
    while x <= LimitSupX:
        
        ValoresX.append(x)
        try:
            y = Tipofuncion(x)
            if isinstance(y , complex) or y == float('inf') or y == float('-inf') or y == float('nan'):
                ValoresY.append(None)
            else : 
                ValoresY.append(y)
            
        except(ValueError, ZeroDivisionError, TypeError): #comprobar error matematico: division x 0 , etc
            ValoresY.append(None)
        x += incremento
    
    return ValoresX , ValoresY


def graficar_funcion_desde_texto(expr_str, rango_x=(-10, 10), rango_y=None, intersecciones=None, punto_evaluado=None, allowed_vars=None):
    """
    Grafica una función a partir de una expresión de texto.
    
    Args:
        expr_str: Expresión matemática como string (ej: "x**2 + 2*x + 1")
        rango_x: Tupla con el rango de x (min, max)
        rango_y: Tupla con el rango de y (min, max) - opcional
        intersecciones: Lista de puntos (x, y) para marcar intersecciones
        punto_evaluado: Tupla (x, y) para marcar un punto específico
        allowed_vars: Variables permitidas (por defecto ['x'])
    
    Returns:
        tuple: (success: bool, message: str, parse_result: ParseResult)
    """
    if allowed_vars is None:
        allowed_vars = ['x']
    
    # Parsear la expresión
    parse_result = parse_function(
        expr_str, 
        allowed_vars=allowed_vars,
        simplify_expression=True
    )
    
    if not parse_result.is_valid:
        return False, f"Error al parsear la función: {parse_result.error}", parse_result
    
    # Mostrar advertencias si las hay
    if parse_result.warnings:
        print("Advertencias:")
        for warning in parse_result.warnings:
            print(f"  - {warning}")
    
    try:
        funcion_ejecutable = parse_result.to_callable(modules=['math'])
        
        # Adjuntar el parse_result a la función para detectar discontinuidades
        funcion_ejecutable._parse_result = parse_result
        
        # Detectar discontinuidades
        discontinuidades = detectar_discontinuidades(parse_result, rango_x)
        if discontinuidades:
            print(f"Discontinuidades detectadas en: {discontinuidades}")
        
        graficar_funcion(
            funcion_ejecutable, 
            expr_str, 
            intersecciones=intersecciones,
            punto_evaluado=punto_evaluado,
            rango_x=rango_x,
            rango_y=rango_y
        )
        
        return True, "Función graficada exitosamente", parse_result
        
    except Exception as e:
        return False, f"Error al graficar: {str(e)}", parse_result
        
    except Exception as e:
        return False, f"Error al graficar: {str(e)}", parse_result


def evaluar_funcion_en_punto(expr_str, x_valor, allowed_vars=None):
    """
    Evalúa una función en un punto específico.
    
    Args:
        expr_str: Expresión matemática como string
        x_valor: Valor de x donde evaluar
        allowed_vars: Variables permitidas
    
    Returns:
        tuple: (success: bool, result: float or None, message: str)
    """
    if allowed_vars is None:
        allowed_vars = ['x']
    
    parse_result = parse_function(expr_str, allowed_vars=allowed_vars)
    
    if not parse_result.is_valid:
        return False, None, f"Error: {parse_result.error}"
    
    try:
        if 'x' in parse_result.variables:
            resultado = parse_result.evaluate(x=x_valor)
        else:
            
            resultado = parse_result.evaluate()
        
        return True, resultado, f"f({x_valor}) = {resultado}"
        
    except Exception as e:
        return False, None, f"Error al evaluar: {str(e)}"


def graficar_con_analisis(expr_str, rango_x=(-10, 10), mostrar_intersecciones=True, evaluar_en=None):
    """
    Grafica una función con análisis automático de intersecciones.
    
    Args:
        expr_str: Expresión matemática como string
        rango_x: Rango para la gráfica
        mostrar_intersecciones: Si calcular y mostrar intersecciones
        evaluar_en: Valor de x donde evaluar y marcar un punto
    """
    from domain.analysis import AnalisisFuncion
    import sympy as sp
    
    
    parse_result = parse_function(expr_str, allowed_vars=['x'])
    
    if not parse_result.is_valid:
        print(f"Error: {parse_result.error}")
        return
    
    intersecciones = None
    punto_evaluado = None
    
    if mostrar_intersecciones and parse_result.expr:
        try:
            
            x = sp.Symbol('x')
            ceros = sp.solve(parse_result.expr, x)
            intersecciones = []
            
            for cero in ceros:
                if cero.is_real:
                    x_val = float(cero.evalf())
                    if rango_x[0] <= x_val <= rango_x[1]:
                        intersecciones.append((x_val, 0))
            
            try:
                y_intercept = float(parse_result.expr.subs(x, 0).evalf())
                intersecciones.append((0, y_intercept))
            except:
                pass
                
        except Exception as e:
            print(f"No se pudieron calcular intersecciones: {e}")
    
    if evaluar_en is not None:
        success, resultado, mensaje = evaluar_funcion_en_punto(expr_str, evaluar_en)
        if success:
            punto_evaluado = (evaluar_en, resultado)
            print(mensaje)
    
    # Graficar
    success, mensaje, _ = graficar_funcion_desde_texto(
        expr_str, 
        rango_x=rango_x,
        intersecciones=intersecciones,
        punto_evaluado=punto_evaluado
    )
    
    print(mensaje)


def graficar_funcion(TipoFuncion, Func_str, intersecciones=None, punto_evaluado=None, rango_x=(-10, 10), rango_y=None):
    
    if not callable(TipoFuncion):
        print("Error: la funcion proporcionada no es un objeto valido")
        return
    
    #crear figura y los ejes de la grafica
    fig, ax = plt.subplots(figsize=(10, 8))
    
    #generar los puntos de la funcion principal
    LimitInfX , LimitSupX = rango_x
    
    # Intentar detectar discontinuidades desde el contexto si está disponible
    try:
        # Si la función fue creada con parse_function, intentar acceder a los warnings
        if hasattr(TipoFuncion, '_parse_result'):
            discontinuidades = detectar_discontinuidades(TipoFuncion._parse_result, rango_x)
            ValoresX, ValoresY = generar_puntos_mejorado(TipoFuncion, LimitInfX, LimitSupX, discontinuidades)
        else:
            ValoresX, ValoresY = generar_puntos(TipoFuncion, LimitInfX, LimitSupX)
    except:
        # Fallback al método original
        ValoresX, ValoresY = generar_puntos(TipoFuncion, LimitInfX, LimitSupX)
    
    # Graficar la función principal manejando discontinuidades
    current_x = []
    current_y = []
    first_segment = True  # Para controlar el label y color
    
    for i, (x, y) in enumerate(zip(ValoresX, ValoresY)):
        if x is None or y is None:
            # Discontinuidad - graficar el segmento actual y empezar uno nuevo
            if current_x and current_y:
                if first_segment:
                    ax.plot(current_x, current_y, label=f'f(x) = {Func_str}', color='C0')
                    first_segment = False
                else:
                    ax.plot(current_x, current_y, color='C0')  # Mismo color, sin label
                current_x = []
                current_y = []
        else:
            current_x.append(x)
            current_y.append(y)
    
    # Graficar el último segmento si existe
    if current_x and current_y:
        if first_segment:
            ax.plot(current_x, current_y, label=f'f(x) = {Func_str}', color='C0')
        else:
            ax.plot(current_x, current_y, color='C0')  # Mismo color, sin label
    
    #graficar interserciones (si es k hay)
    if intersecciones:
        inter_x =[p[0] for p in intersecciones]
        inter_y = [p[1] for p in intersecciones]
        
        ax.scatter(inter_x , inter_y, color = 'red', zorder = 5 , label = 'intersecciones')
    
    #graficar punto evaluado
    if punto_evaluado:
        px , py = punto_evaluado
        ax.scatter(px, py, color='green', s=100, zorder=5, edgecolors='black', label=f'punto evaluado ({px}, {py})')
    
    
    #añadir elementos extras a la grafica
    
    #titulos
    ax.set_title(f'Gráfica de la función f(x) = {Func_str}', fontsize=16)
    ax.set_xlabel('Eje X', fontsize=12)
    ax.set_ylabel('Eje Y', fontsize=12)
    
    
    #cuadriculado
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    #ejes X e Y (lineas de 0 0)
    ax.axhline(0, color='black', linewidth=0.8)
    ax.axvline(0, color='black', linewidth=0.8)
    
    ax.legend()
    ax.set_xlim(LimitInfX, LimitSupX)
    
    # Aplicar rango Y si se proporciona
    if rango_y is not None:
        ax.set_ylim(rango_y[0], rango_y[1])
        
    plt.show()


# Función de demostración
def demo_graficador():
    """Demostración del graficador con parser integrado."""
    print("=== Demo del Graficador con Parser ===\n")
    
    # Ejemplos de funciones
    ejemplos = [
        "x**2 - 4",
        "sin(x)",
        "1/(x-2)",
        "exp(x)",
        "log(x+1)",
        "sqrt(x**2 + 1)"
    ]
    
    for expr in ejemplos:
        print(f"Probando: {expr}")
        success, mensaje, _ = graficar_funcion_desde_texto(expr, rango_x=(-5, 5))
        print(f"Resultado: {mensaje}\n")
        
        if success:
            input("Presiona Enter para continuar...")


if __name__ == "__main__":
    # Ejemplo de uso
    expr = "x**2 - 4*x + 3"
    print(f"Graficando: {expr}")
    graficar_con_analisis(expr, rango_x=(-2, 6), evaluar_en=2)





