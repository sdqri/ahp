import numpy as np


def input_matrix(msg, row, column, names):
    a = np.ones(shape=(row, column))
    for r in range(row):
        for c in range(r + 1, column):
            v = float(input(msg.format(names[r], names[c])))
            a[r, c] = v
            a[c, r] = 1 / v
    return a
