import argparse
import os
import sys

sys.path.append(os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..', 'src'
))
import sat_solver


def _create_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='The program to find the maximum '
                                                 'size of a clique graph which '
                                                 'can be colored with K colors so '
                                                 'there are not triangles of edges '
                                                 'colored to only one color.\n'
                                                 'If you specify optional parameter -n, '
                                                 'then the program will check whether '
                                                 'it is possible to color n-clique graph '
                                                 'with k colors.')
    parser.add_argument('-k', type=int, help='number of colors', required=True)
    parser.add_argument('-n', type=int, help='number of nodes in the clique', default=None)
    return parser


def generate_bool_expr(n: int, colors_num: int) -> str:
    visited_triangles = set()
    visited_edges = set()
    triangles = []
    edges = []

    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            for k in range(n):
                triangle = frozenset({i, j, k})
                if k == i or k == j or triangle in visited_triangles:
                    continue

                visited_triangles.add(triangle)
                a, b, c = sorted(triangle)

                triangle_expr = []
                for color in range(colors_num):
                    # The triangle's edges don't have the same color.
                    triangle_expr.append(f'~(_{color}_{a}_{b}_ & '
                                         f'_{color}_{a}_{c}_ & _{color}_{b}_{c}_)')
                triangles.append(' & '.join(triangle_expr))

                for s, e in [(a, b), (a, c), (b, c)]:
                    if (s, e) in visited_edges:
                        continue
                    visited_edges.add((s, e))
                    edge_expr = []
                    # The edge is colored with just one color.
                    for color in range(colors_num):
                        other_colors = ' & '.join([f'~_{c}_{s}_{e}_' for c in range(colors_num) if c != color])
                        edge_expr.append(f'(_{color}_{s}_{e}_ & {other_colors})')
                    edges.append('(' + ' | '.join(edge_expr) + ')')

    return ' & '.join(triangles) + ' & ' + ' & '.join(edges)


if __name__ == '__main__':
    args = _create_arg_parser().parse_args()

    if args.n is not None:
        sat_solver.solve(generate_bool_expr(args.n, args.k))
    else:
        n = 2
        is_sat = True
        while is_sat:
            n += 1
            is_sat, _ = sat_solver.solve(generate_bool_expr(n, args.k), silent=True)

        print(f'Maximum size = {n - 1}')
