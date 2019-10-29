from typing import Set, List, Generator, Dict

from boolean import Expression, NOT
from itertools import chain


class CNFFormula:

    def __init__(self, expressions: Set[Expression]):
        symbols = set(chain(*list(map(lambda x: x.symbols, expressions))))

        self.symbol_to_num = dict()
        for index, symbol in enumerate(symbols, start=1):
            self.symbol_to_num[symbol] = index

        self.clauses = []
        for expr in expressions:
            clause = set()
            for literal in expr.get_literals():
                if isinstance(literal, NOT):
                    num = -self.symbol_to_num[literal.args[0]]
                else:
                    num = self.symbol_to_num[literal]
                clause.add(num)
            self.clauses.append(frozenset(clause))

        self._model = dict()
        for clause in self.clauses:
            for prop_var in clause:
                self._model[abs(prop_var)] = False

    def update_model(self, literal: int, value: bool) -> None:
        self._model[abs(literal)] = value if literal > 0 else not value

    @property
    def model(self) -> Dict:
        model = dict()
        for symbol, num in self.symbol_to_num.items():
            model[symbol] = self._model[num]
        return model

    @property
    def literals(self) -> Set[int]:
        literals = set()

        for clause in self.clauses:
            for prop_var in clause:
                literals.add(prop_var)

        return literals

    @property
    def pure_literals(self) -> List[int]:
        res = []
        for literal in self.literals:
            if -literal not in self.literals:
                res.append(literal)
        return res

    @property
    def units(self) -> List[int]:
        res = []
        for clause in self.clauses:
            if len(clause) == 1:
                res.append(next(iter(clause)))
        return res

    def empty(self) -> bool:
        return not bool(self.clauses) or all(not clause for clause in self.clauses)

    def contains_empty_clause(self) -> bool:
        units = self.units
        return any(-unit in units for unit in units)
