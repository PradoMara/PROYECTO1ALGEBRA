from sympy import sympify, symbols, lambdify, solve, simplify
from sympy.core.sympify import SympifyError
import re
from typing import List, Optional, Union


class ParseResult:
    """
    Clase que encapsula el resultado del parsing de una función.
    """
    def __init__(self, expr=None, variables=None, error=None, warnings=None):
        self.expr = expr                    # Expresión de SymPy
        self.variables = variables or []    # Lista de variables encontradas
        self.error = error                  # Mensaje de error si hay alguno
        self.warnings = warnings or []      # Lista de advertencias
        self.is_valid = error is None       # True si el parsing fue exitoso
        
    def evaluate(self, **values):

        if not self.is_valid or not self.expr:
            raise ValueError(f"No se puede evaluar: {self.error}")
        
        missing_vars = [var for var in self.variables if var not in values]
        if missing_vars:
            raise ValueError(f"Faltan valores para las variables: {missing_vars}")
        
        try:
            result = self.expr
            for var_name, value in values.items():
                if var_name in self.variables:
                    var_symbol = symbols(var_name)
                    result = result.subs(var_symbol, value)
            

            return float(result.evalf())
            
        except Exception as e:
            raise ValueError(f"Error al evaluar la función: {str(e)}")
    
    def to_callable(self):

        if not self.is_valid or not self.expr:
            raise ValueError(f"No se puede crear función callable: {self.error}")
        
        if not self.variables:
           
            constant_value = float(self.expr.evalf())
            return lambda x: constant_value
        
        if len(self.variables) == 1:
            var_symbol = symbols(self.variables[0])
            
            def func(x):
                try:
                    result = self.expr.subs(var_symbol, x)
                    return float(result.evalf())
                except:
                    return None
            
            return func
        
        else:
            var_symbols = [symbols(var) for var in self.variables]
            
            def func(*args):
                if len(args) != len(self.variables):
                    raise ValueError(f"Se esperaban {len(self.variables)} argumentos, se recibieron {len(args)}")
                
                try:
                    result = self.expr
                    for var_symbol, value in zip(var_symbols, args):
                        result = result.subs(var_symbol, value)
                    return float(result.evalf())
                except:
                    return None
            
            return func


def preprocess_function_text(expr_str: str) -> str:

    if not isinstance(expr_str, str):
        raise TypeError("La entrada debe ser una cadena de texto")
    

    text = expr_str.strip()
    
 
    replacements = {
        '^': '**',      # Potenciación
        'ln': 'log',    # Logaritmo natural
        '√': 'sqrt',    # Raíz cuadrada
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    text = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', text)
    
    return text


def validate_function_syntax(expr_str: str) -> tuple[bool, str]:
   
    if not expr_str.strip():
        return False, "La función no puede estar vacía"
    
   
    if expr_str.count('(') != expr_str.count(')'):
        return False, "Paréntesis no balanceados"
    

    allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+-*/().,^√ ')
    if not set(expr_str).issubset(allowed_chars):
        invalid_chars = set(expr_str) - allowed_chars
        return False, f"Caracteres no permitidos: {', '.join(invalid_chars)}"
    
    return True, ""


def check_division_by_zero_risks(expr, variables: List[str]) -> List[str]:

    warnings = []
    
    try:

        denominators = []
        
        def extract_denominators(e):
            if hasattr(e, 'as_numer_denom'):
                num, den = e.as_numer_denom()
                if den != 1:
                    denominators.append(den)
            if hasattr(e, 'args'):
                for arg in e.args:
                    extract_denominators(arg)
        
        extract_denominators(expr)
        
        for denom in denominators:
            if variables:
                try:
                    var = symbols(variables[0]) 
                    critical_points = solve(denom, var)
                    if critical_points:
                        points_str = ', '.join([str(point) for point in critical_points])
                        warnings.append(f"Posible división por cero en {variables[0]} = {points_str}")
                except:
                    warnings.append("Posible división por cero detectada")
                    
    except Exception:
        pass  
    
    return warnings


def parse_function(expr_str: str, allowed_vars=("x", "y", "z", "t")) -> ParseResult:
    
    try:
        is_valid, error_msg = validate_function_syntax(expr_str)
        if not is_valid:
            return ParseResult(error=error_msg)

        processed_text = preprocess_function_text(expr_str)

        try:
            expr = sympify(processed_text)
        except SympifyError as e:
            return ParseResult(error=f"Error de sintaxis matemática: {str(e)}")
        except Exception as e:
            return ParseResult(error=f"Error al procesar la función: {str(e)}")

        found_variables = [str(symbol) for symbol in expr.free_symbols]

        invalid_vars = [var for var in found_variables if var not in allowed_vars]
        if invalid_vars:
            return ParseResult(
                error=f"Variables no permitidas: {', '.join(invalid_vars)}. "
                      f"Variables válidas: {', '.join(allowed_vars)}"
            )

        warnings = check_division_by_zero_risks(expr, found_variables)

        try:
            simplified_expr = simplify(expr)
            expr = simplified_expr
        except:
            pass  
        
        return ParseResult(
            expr=expr,
            variables=found_variables,
            warnings=warnings
        )
        
    except Exception as e:
        return ParseResult(error=f"Error inesperado: {str(e)}")


def parse_simple_function(expr_str: str) -> Union[object, None]:

    result = parse_function(expr_str)
    return result.expr if result.is_valid else None
