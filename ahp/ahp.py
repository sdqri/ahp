from typing import List, Optional

import numpy as np

from graphviz import Digraph

from .criterion import Criterion
from .utils import input_matrix


C_NODE_LABEL = "{}\nGlobal Priority = {:.2f}"


class AHP:
    def __init__(self, goal: str, alternatives: List[str]):
        self.goal: str = goal
        self.alternatives: List[str] = alternatives
        self.criteria: List[Criterion] = []
        self.pairwise_matrix: Optional[np.array] = None
        self.G: Digraph = Digraph(strict=True)
        self.priority_list: List[float] = []
        self.priority_names: List[str] = []
        self.alternatives_matrix: Optional[np.array] = None
        self.result_vector: Optional[np.array] = None
        self.result: list = []

    def add_criterion(self, criterion: Criterion):
        self.criteria.append(criterion)

    def update_pairwise_matrix(self, array: np.array):
        self.pairwise_matrix = array

    def get_pairwise_matrix(self):
        return self.pairwise_matrix

    def input_criteria(self):
        while True:
            criterion_name = input("Enter criterion for {} or 'q' for end:".format(self.goal))
            if criterion_name.lower() == "q":
                break
            criterion = Criterion(name=criterion_name)
            criterion.input_subcriteria()
            self.criteria.append(criterion)

    def input_priority(self):
        names = [c.name for c in self.criteria]
        row, column = len(self.criteria), len(self.criteria)
        m = input_matrix("Pairwise Comparisons: Enter relative importance of {} to {}:",
                         row=row, column=column, names=names)
        self.update_pairwise_matrix(m)
        for sc in self.criteria:
            # calc and update local priority of sub criteria
            m_normed = m / m.sum(axis=0)
            weights = m_normed.sum(axis=1)
            weights = weights / weights.sum()
            for i, w in enumerate(weights):
                self.criteria[i].priority = w
                self.criteria[i].global_priority = w
            sc.input_priority()  # recursive call

    def calc_priority_vector(self):
        for c in self.criteria:
            if c.is_leaf():
                self.priority_list.append(c.global_priority)
                self.priority_names.append(c.name)
            else:
                c.calc_priority_vector()
                self.priority_list.extend(c.priority_list)
                self.priority_names.extend(c.priority_names)

    def input_alternatives_matrix(self):
        num_alt = len(self.alternatives)
        num_pri = len(self.priority_list)
        self.alternatives_matrix = np.zeros(shape=(num_alt, num_pri))

        for c, p in enumerate(self.priority_names):
            print(self.alternatives)
            alternative_matrix = input_matrix("Alternatives Comparisons: "
                                              "Enter relative weight of {} to {} with respect to " + p + ":",
                                              row=num_alt, column=num_alt, names=self.alternatives)
            m = alternative_matrix
            m_normed = m / m.sum(axis=0)
            weights = m_normed.sum(axis=1)
            self.alternatives_matrix[:, c] = weights

    def input_values(self):
        self.input_criteria()
        self.input_priority()
        self.calc_priority_vector()
        self.input_alternatives_matrix()

    def decide(self):
        priority_array = np.array(self.priority_list).transpose()
        result_vector = self.alternatives_matrix @ priority_array
        self.result_vector = result_vector / result_vector.sum()
        self.result = list(zip(self.alternatives, list(self.result_vector.ravel())))
        self.result.sort(key=lambda x: x[1], reverse=True)
        return self.result

    def draw(self):
        self.G.node(name="goal", label=self.goal)
        for alternative in self.alternatives:
            self.G.node(alternative)
        for criterion in self.criteria:
            self.G.node(name=criterion.name,
                        label=C_NODE_LABEL.format(criterion.name, criterion.global_priority))
            self.G.edge(tail_name="goal", head_name=criterion.name)
            criterion.draw(self.G, self.alternatives)

    def draw_result(self):
        for n, p in self.result:
            self.G.node(n, label="{}\n Priority = {:.2f}".format(n, p))

    def view(self, *args, **kwargs):
        self.draw()
        self.G.view(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.draw()
        self.G.save(*args, **kwargs)
