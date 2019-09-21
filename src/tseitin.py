from typing import Set, Tuple

from boolean import BooleanAlgebra, Expression, NOT, AND, OR, Symbol


def get_unique_var_name() -> Symbol:
    if not hasattr(get_unique_var_name, 'counter'):
        get_unique_var_name.counter = 1

    # Here we just hope that user doesn't use so obscure name.
    s = Symbol(f'_system_{get_unique_var_name.counter}')
    get_unique_var_name.counter += 1
    return s


def _parse_boolean_expression(expr: str) -> Expression:

    def convert_to_bin_operands(expr: Expression) -> Expression:
        expr_type = type(expr)
        if expr_type in (NOT, Symbol):
            return expr
        elif len(expr.args) == 2:
            return expr_type(
                convert_to_bin_operands(expr.args[0]),
                convert_to_bin_operands(expr.args[1])
            )
        else:
            return expr_type(convert_to_bin_operands(expr.args[0]),
                             convert_to_bin_operands(expr_type(*expr.args[1:])))

    return convert_to_bin_operands(BooleanAlgebra().parse(expr))


def _helper_tseitin(formula: Tuple[Expression, Set[Expression]])\
        -> Tuple[Expression, Set[Expression]]:

    def expr_negation(expr: Expression) -> Expression:
        if isinstance(expr, NOT):
            return expr.args[0]
        return NOT(expr)

    expr, delta = formula

    if isinstance(expr, Symbol):
        return formula
    elif isinstance(expr, NOT):
        _l, _delta = _helper_tseitin((expr.args[0], delta))
        return expr_negation(_l), _delta
    elif isinstance(expr, AND) or isinstance(expr, OR):
        _l1, _delta1 = _helper_tseitin((expr.args[0], delta))
        _l2, _delta2 = _helper_tseitin((expr.args[1], _delta1))

        p = get_unique_var_name()

        if isinstance(expr, AND):
            _delta = _delta2.union({
                OR(expr_negation(p), _l1),
                OR(expr_negation(p), _l2),
                OR(p, OR(expr_negation(_l1), expr_negation(_l2)))
            })
        else:
            _delta = _delta2.union({
                OR(expr_negation(_l1), p),
                OR(expr_negation(_l2), p),
                OR(expr_negation(p), OR(_l1, _l2))
            })

        return p, _delta
    else:
        raise TypeError(f'Tseitin transformation does not support {type(expr)} type.')


def tseitin(expr: str) -> Tuple[Set[Expression], Set[Symbol]]:
    if expr == '':
        return set(), set()
    expr = _parse_boolean_expression(expr)
    p, delta = _helper_tseitin((expr, set()))
    delta.add(p)
    return delta, expr.symbols
