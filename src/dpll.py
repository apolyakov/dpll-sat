from typing import Set, FrozenSet, Tuple, Dict, Union
from copy import deepcopy
import random

from cnf_formula import CNFFormula


def eliminate_pure_literal(s: Set[FrozenSet[int]],
                           literal: int,
                           from_unit_propagate: bool = False) -> Set[FrozenSet[int]]:
    if from_unit_propagate:
        return set(
            map(lambda x: x.difference(frozenset({literal})) if literal in x else x, s)
        )
    return set(filter(lambda x: literal not in x, s))


def unit_propagate(s: Set[FrozenSet[int]], literal: int) -> Set[FrozenSet[int]]:
    return eliminate_pure_literal(
        set(filter(lambda x: literal not in x, s)),
        -literal,
        from_unit_propagate=True
    )


def dpll(cnf: CNFFormula) -> Tuple[bool, Dict]:

    def get_extended_cnf(new_cnf: CNFFormula, literal: int) -> CNFFormula:
        new_cnf = deepcopy(new_cnf)

        new_cnf.clauses.add(frozenset({literal}))
        new_cnf.update_model(literal, True)

        return new_cnf

    def get_cnf_status(cnf: CNFFormula) -> Union[None, Tuple[bool, Dict]]:
        if cnf.empty:
            return True, cnf.model
        if cnf.contains_empty_clause:
            return False, cnf.model
        return None

    # Unit propagate
    while True:
        status = get_cnf_status(cnf)
        if status is not None:
            return status

        units = cnf.units
        if not units:
            break
        cnf.clauses = unit_propagate(cnf.clauses, units[0])
        cnf.update_model(units[0], True)

    # Eliminate pure literals
    while True:
        status = get_cnf_status(cnf)
        if status is not None:
            return status

        units = cnf.pure_literals
        if not units:
            break
        cnf.clauses = eliminate_pure_literal(cnf.clauses, units[0])
        cnf.update_model(units[0], True)

    # Choose literal
    literal = random.sample(cnf.literals, 1)[0]
    is_sat, model = dpll(get_extended_cnf(cnf, literal))

    if is_sat:
        return True, model
    else:
        return dpll(get_extended_cnf(cnf, -literal))
