from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Iterable, Optional, Callable, Any

import sympy
from sympy import Symbol
from sympy.core.sympify import SympifyError
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application
)


class ParseError(Exception):
    """Error general de parsing."""


class InvalidVariableError(ParseError):
    """Se usaron variables no permitidas."""


class EmptyExpressionError(ParseError):
    """Expresión vacía."""


class DomainWarning(Warning):
    """Advertencias relacionadas al dominio (división por cero, etc.)."""


DEFAULT_ALLOWED_FUNCTIONS: Dict[str, Any] = {
    # trigonometria
    "sin": sympy.sin,
    "cos": sympy.cos,
    "tan": sympy.tan,
    "asin": sympy.asin,
    "acos": sympy.acos,
    "atan": sympy.atan,
    # hiperbolic
    "sinh": sympy.sinh,
    "cosh": sympy.cosh,
    "tanh": sympy.tanh,
    # funciones exponenciales y logaritmicas
    "exp": sympy.exp,
    "log": sympy.log,
    "ln": sympy.log,   # alias
    "sqrt": sympy.sqrt,
    "abs": sympy.Abs,
}
DEFAULT_CONSTANTS: Dict[str, Any] = {
    "pi": sympy.pi,
    "e": sympy.E
}


@dataclass
class ParseResult:
    expr: Optional[sympy.Expr]
    variables: List[str]
    warnings: List[str]
    error: Optional[str]

    def __post_init__(self):
        self.is_valid = self.error is None

    def _symbols(self) -> List[Symbol]:
        return [sympy.Symbol(v) for v in self.variables]

    def to_callable(self, modules: Optional[List[str]] = None) -> Callable:

        if not self.is_valid or self.expr is None:
            raise ValueError(f"No se puede crear callable: {self.error}")

        if not self.variables:
            const_val = float(self.expr.evalf())
            return lambda: const_val

        modules = modules or ["math"]
        f = sympy.lambdify(self._symbols(), self.expr, modules=modules)

        def wrapped(*args):
            if len(args) != len(self.variables):
                raise ValueError(
                    f"Se esperaban {len(self.variables)} argumentos: {self.variables}, "
                    f"recibidos {len(args)}"
                )
            val = f(*args)

            if val in (sympy.zoo, sympy.oo, sympy.nan):
                raise ValueError("Resultado no definido (NaN o infinito).")
            import math
            try:
                float_val = float(val)
                if math.isnan(float_val) or math.isinf(float_val):
                    raise ValueError("Resultado no definido (NaN o infinito).")
                return float_val
            except (TypeError, ValueError):
                raise ValueError("Resultado no válido.")

        return wrapped

    def evaluate(self, **kwargs) -> float:

        if not self.is_valid or self.expr is None:
            raise ValueError(f"No se puede evaluar: {self.error}")
        missing = [v for v in self.variables if v not in kwargs]
        if missing:
            raise ValueError(f"Faltan valores para: {missing}")
        f = self.to_callable()
        ordered = [kwargs[v] for v in self.variables]
        return f(*ordered)

def _preprocess(expr_str: str) -> str:

    if not isinstance(expr_str, str):
        raise TypeError("La función debe ser cadena de texto.")

    text = expr_str.strip()
    if not text:
        raise EmptyExpressionError("La expresión no puede estar vacía.")

    replacements = {
        "^": "**",
        "√": "sqrt",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


def _validate_parentheses(expr_str: str) -> None:
    if expr_str.count("(") != expr_str.count(")"):
        raise ParseError("Paréntesis no balanceados.")


def _collect_domain_warnings(expr: sympy.Expr) -> List[str]:

    warnings: List[str] = []
    try:
        num, den = sympy.fraction(expr)  
        if den != 1:
            
            factors = sympy.factor(den)
            
            factors_list = sympy.factorint(factors) if factors.is_Mul else {factors: 1}
            seen = set()
            for factor in factors_list:
                if factor not in seen and factor != 1:
                    seen.add(factor)
                    warnings.append(f"Posible restricción de dominio: {factor} ≠ 0")
    except Exception:
        pass
    return warnings


def parse_function(
    expr_str: str,
    allowed_vars: Optional[Iterable[str]] = None,
    extra_functions: Optional[Dict[str, Any]] = None,
    simplify_expression: bool = False,
    safe: bool = True,
    implicit_multiplication: bool = True
) -> ParseResult:
    
    try:
        raw = expr_str
        _validate_parentheses(raw)
        preprocessed = _preprocess(raw)

        local_dict: Dict[str, Any] = {}
        local_dict.update(DEFAULT_ALLOWED_FUNCTIONS)
        local_dict.update(DEFAULT_CONSTANTS)
        if extra_functions:
            local_dict.update(extra_functions)
    
        transformations = standard_transformations
        if implicit_multiplication:
            transformations = standard_transformations + (implicit_multiplication_application,)

        try:
            expr = parse_expr(
                preprocessed,
                local_dict=local_dict if safe else None,
                evaluate=True,
                transformations=transformations
            )
        except SympifyError as e:
            return ParseResult(None, [], [], f"Error de sintaxis: {e}")
        except Exception as e:
            return ParseResult(None, [], [], f"No se pudo parsear: {e}")

        vars_found = sorted([str(s) for s in expr.free_symbols], key=lambda v: v)

        if allowed_vars is not None:
            allowed_set = set(allowed_vars)
            invalid = [v for v in vars_found if v not in allowed_set]
            if invalid:
                return ParseResult(
                    None,
                    [],
                    [],
                    f"Variables no permitidas: {invalid}. Permitidas: {sorted(allowed_set)}"
                )

        domain_warnings = _collect_domain_warnings(expr)

        if simplify_expression:
            try:
                expr = sympy.simplify(expr)
            except Exception:
                domain_warnings.append("No se pudo simplificar (ignorado).")

        vars_final = sorted([str(s) for s in expr.free_symbols], key=lambda v: v)

        if allowed_vars is not None:
            vars_final = [v for v in vars_final if v in allowed_vars]

        return ParseResult(expr=expr, variables=vars_final, warnings=domain_warnings, error=None)

    except EmptyExpressionError as e:
        return ParseResult(None, [], [], str(e))
    except ParseError as e:
        return ParseResult(None, [], [], str(e))
    except Exception as e:
        return ParseResult(None, [], [], f"Error inesperado: {e}")

def parse_simple_function(expr_str: str) -> Optional[sympy.Expr]:
    result = parse_function(expr_str)
    return result.expr if result.is_valid else None

#hola mundo