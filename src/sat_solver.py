import argparse

from cnf_formula import CNFFormula
from dpll import dpll
from tseitin import tseitin


def create_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Take a boolean expression "
                                                 "and determine whether it's "
                                                 "satisfiable or not.\n"
                                                 "Available operators: NOT: '~', "
                                                 "AND: '&', OR: '|'. "
                                                 "Ex.: ~(a | b & (a | c))",
                                     epilog='Note, that boolean expression '
                                            'should be passed in quotes.')
    parser.add_argument('expression', type=str, help='an expression to check')
    return parser


if __name__ == '__main__':
    args = create_arg_parser().parse_args()

    clauses, original_literals = tseitin(args.expression)
    cnf = CNFFormula(clauses)
    is_sat, model = dpll(cnf)

    if is_sat:
        model_str = '\n'.join(list(
            map(lambda key: f'{key}: {model[key]}',
                filter(lambda key: key in original_literals, model.keys()))
        ))
        print(f'SAT: {args.expression}\n'
              f'Model: \n{model_str}')
    else:
        print('UNSAT')
