import sympy as sp


x = sp.Symbol('x')

class AnalisisFuncion:
    def __init__(self, funcion):
        self.f = funcion



    def dominio(self):
        try:
            dom = sp.calculus.util.continuous_domain(self.f, x, sp.S.Reals)
            explicacion = f"Para calcular el dominio veo los valores que no sirven (divisiones por 0, etc)."
            return f"{explicacion}\nDominio: {dom}"
        except Exception as e:
            return f"No pude calcular el dominio. Error: {e}"



    def recorrido(self):
        # pruebo valores de -10 a 10
        valores = []
        pasos = "Probé valores de x entre -10 y 10:\n"
        for i in range(-10, 11):
            try:
                val = self.f.subs(x, i)
                pasos += f"f({i}) = {val}\n"
                if val.is_real:
                    valores.append(val)
            except Exception:
                pasos += f"f({i}) no se pudo calcular\n"
        if valores:
            minimo = min(valores)
            maximo = max(valores)
            return f"{pasos}El recorrido aproximado va entre {minimo} y {maximo}"
        else:
            return "No logré calcular el recorrido :("



    def intersecciones(self):
        salida = "Intersecciones:\n"
        
        try:
            ceros = sp.solve(self.f, x)
            reales = [c for c in ceros if c.is_real]
            salida += f"Con eje X: resolviendo f(x)=0 salen {reales}\n"
        except Exception as e:
            salida += f"No pude calcular intersecciones con X. Error: {e}\n"

        # con eje Y es f(0)
        try:
            y0 = self.f.subs(x, 0)
            salida += f"Con eje Y: f(0) = {y0}\n"
        except Exception as e:
            salida += f"No pude calcular intersección con Y. Error: {e}\n"

        return salida





#prueba 
if __name__ == "__main__":
    # ejemplo de función
    f = (x**2 - 1) / (x - 2)
    analisis = AnalisisFuncion(f)

    print(analisis.dominio())
    print("----")
    print(analisis.recorrido())
    print("----")
    print(analisis.intersecciones())
