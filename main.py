from typing import List

import typer
from typer import Option

from ahp import AHP

app = typer.Typer()

dp = None  # decision problem


@app.command()
def decide(name:str, goal: str, alternatives: List[str],
           save: bool = Option(default=False, help="Saves Decision problem graph as pdf file")):
    print("save=", save)
    global dp
    dp = AHP(goal=goal, alternatives=alternatives)
    dp.input_values()
    print("**********************")
    print("result = ", dp.decide())
    print("**********************")
    if save:
        dp.draw()
        dp.draw_result()
        dp.view(filename="graph")


if __name__ == "__main__":
    app()

import numpy as np

if __name__ == "__main__":
    alternatives = []
    while True:
        alt = input("Enter alternative or q for exit:")
        if alt == "q":
            break
        else:
            alternatives.append(alt)

    criteria = []
    while True:
        criterion = input("Enter criterion or q for exit:")
        if criterion == "q":
            break
        else:
            criteria.append(criterion)

    criteria_type = []
    for c in criteria:
        t = input(f"Is {c} a positive or negative criterion?(1 or -1):")
        criteria_type.append(float(t))

    m = len(alternatives)
    n = len(criteria)
    array = np.zeros(shape=(m, n))
    for i, r in enumerate(array):
        for j, c in enumerate(r):
            x = input(f"Please enter value of {criteria[j]}"
                      " for {alternatives[i]} = ")
        array[i, j] = float(x)

    # Normalize
    array = array / np.sqrt(np.sum(array ** 2, axis=0))

    weights = []
    for c in criteria:
        w = input(f"Please enter weight for {c} =")
        weights.append(float(w))

    weights = np.array(weights)

    # Weighted normalized
    array = array * weights

    # Calculate a_star
    maxs = array.max(axis=0)
    mins = array.min(axis=0)
    a_star = []
    a_minus = []
    for k, t in enumerate(criteria_type):
        if t > 0:
            a_star.append(maxs[k])
            a_minus.append(mins[k])
        else:
            a_star.append(mins[k])
            a_minus.append(maxs[k])

    a_star = np.array(a_star)
    a_minus = np.array(a_minus)

    # Calculate positive ideal & negative ideal
    s_star = []
    s_minus = []
    for alt in array:
        ss = np.linalg.norm(alt - a_star)
        s_star.append(ss)
        sm = np.linalg.norm(alt - a_minus)
        s_minus.append(sm)

    s_star = np.array(s_star)
    s_minus = np.array(s_minus)

    # Calculate sepration measure
    cc = s_minus / (s_star + s_minus)

    # Calculate ranks
    ranks = list(zip(alternatives, cc.tolist()))
    ranks.sort(key=lambda x: x[1], reverse=True)
    print("Ranks =", ranks)