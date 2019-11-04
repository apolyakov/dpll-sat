import argparse
import sys

from z3 import *

# Numeric value 'a' means that there 'a' bombs near the cell.
# '?' means that a cell is unknown and could be checked for safety.
# '*' means that there is a bomb in the cell.
GAME_BOARD = [
    '01?10001?',
    '01?100011',
    '011100000',
    '000000000',
    '111110011',
    '????1001?',
    '????3101?',
    '?????211?',
    '?*???????'
]

WIDTH = len(GAME_BOARD[0])
HEIGHT = len(GAME_BOARD)
BOMB_SYMBOL = '*'
ALLOWED_NUMERIC_VALUES = {'0', '1', '2', '3', '4', '5', '6', '7', '8'}


def print_game_board() -> None:
    print('Current game board is:\n')
    for row in GAME_BOARD:
        print(' '.join(row))
    print()


def _create_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=
        "This program takes 2 parameters: the coordinates (starting from 1)\n"
        "of a point on a minesweeper board, and checks whether the point can\n"
        "be safely clicked (i.e. it does not contain a bomb).\n\n"
        "As for now, to change the board configuration you need to\n"
        "modify 'GAME_BOARD' variable inside this source file.",
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-x', type=int,
                        help='x coordinate of a point', required=True)
    parser.add_argument('-y', type=int,
                        help='y coordinate of a point', required=True)
    print_game_board()
    return parser


def check_bomb(_row: int, _col: int) -> None:
    solver = Solver()

    cells = [
        [Int(f'r{r}_c{c}') for c in range(WIDTH + 2)]
        for r in range(HEIGHT + 2)    
    ]

    # create border
    for col in range(WIDTH + 2):
        solver.add(cells[0][col] == 0)
        solver.add(cells[HEIGHT + 1][col] == 0)
    for row in range(HEIGHT + 2):
        solver.add(cells[row][0] == 0)
        solver.add(cells[row][WIDTH + 1] == 0)

    for row in range(1, HEIGHT + 1):
        for col in range(1, WIDTH + 1):
            # otherwise -1 is possible, etc
            solver.add(Or(
                cells[row][col] == 0,
                cells[row][col] == 1
            ))

            t = GAME_BOARD[row - 1][col - 1]
            if t in ALLOWED_NUMERIC_VALUES:
                solver.add(cells[row][col] == 0)

                expr = cells[row - 1][col - 1] + cells[row - 1][col] +\
                    cells[row - 1][col + 1] + cells[row][col - 1] +\
                    cells[row][col + 1] + cells[row + 1][col - 1] +\
                    cells[row + 1][col] + cells[row + 1][col + 1] == int(t)

                solver.add(expr)
            elif t == BOMB_SYMBOL:
                solver.add(cells[row][col] == 1)

    # place a bomb
    solver.add(cells[_row][_col] == 1)

    res = 'unsafe'
    if solver.check() == unsat:
        res = 'safe'
    
    print(f'Row = {_row}, column = {_col} cell is {res}')


if __name__ == "__main__":
    args = _create_arg_parser().parse_args()

    check_bomb(args.x, args.y)
