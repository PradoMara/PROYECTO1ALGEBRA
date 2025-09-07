import matplotlib.pyplot as plt
import math 


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



def graficar_funcion(TipoFuncion, Func_str, intersecciones=None, punto_evaluado=None , rango_x = (-10 , 10)):
    
    if not callable(TipoFuncion):
        print("Error: la funcion proporcionada no es un objeto valido")
        return
    
    #crear figura y los ejes de la grafica
    fig, ax = plt.subplots(figsize=(10, 8))
    
    #generar los puntos de la funcion principal
    LimitInfX , LimitSupX = rango_x
    ValoresX , ValoresY = generar_puntos(TipoFuncion, LimitInfX, LimitSupX)
    
    # Graficar la función principal
    ax.plot(ValoresX, ValoresY, label=f'f(x) = {Func_str}')
    
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
    plt.show()
    
    



if __name__ == '__main__':
    print("Ejecutando pruebas para el módulo plotter.py...")

    # --- Prueba 1: Función cuadrática ---
    # Así es como los otros módulos usarían tu función `graficar_funcion`.
    
    # 1. El parser convertiría "x**2 - 4" en una función lambda.
    funcion_analizada = lambda x: x**2 - 4
    
    # 2. El módulo de análisis calcularía las intersecciones.
    intersecciones_calculadas = [
        (0, -4),  # Intersección eje Y
        (2, 0),   # Intersección eje X
        (-2, 0)   # Intersección eje X
    ]
    
    # 3. El usuario podría pedir evaluar la función en x=3.
    punto_de_evaluacion = (3, 5) # f(3) = 3**2 - 4 = 5

    # 4. Llamamos a tu función con toda la información.
    graficar_funcion(
        TipoFuncion=funcion_analizada,
        Func_str="x**2 - 4",
        intersecciones=intersecciones_calculadas,
        punto_evaluado=punto_de_evaluacion
    )

    # --- Prueba 2: Función con discontinuidad (1/x) ---
    funcion_con_discontinuidad = lambda x: 1/x
    intersecciones_con_discontinuidad = [] # No tiene intersecciones
    punto_evaluado_2 = (2, 0.5) # f(2) = 1/2 = 0.5
    
    graficar_funcion(
        TipoFuncion=funcion_con_discontinuidad,
        Func_str="1/x",
        intersecciones=intersecciones_con_discontinuidad,
        punto_evaluado=punto_evaluado_2,
        rango_x=(-5, 5) # Rango más pequeño para ver la discontinuidad en x=0
    )
    
    print("Pruebas finalizadas.")