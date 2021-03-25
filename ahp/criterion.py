from typing import List, Optional

import numpy as np
from graphviz import Digraph

from .utils import input_matrix

SC_NODE_LABEL = "{}\nLocal Priority = {:.2f}\nGlobal Priority = {:.2f}"


class Criterion:
    def __init__(self, name: str):
        self.name = name
        self.sub_criteria: List[Criterion] = []
        self.pairwise_matrix: Optional[np.array] = None
        self.priority: Optional[float] = None
        self.global_priority: Optional[float] = None
        self.priority_list: List[float] = []
        self.priority_names: List[str] = []

    def add_subcriterion(self, criterion: 'Criterion'):
        self.sub_criteria.append(criterion)

    def update_pairwise_matrix(self, array: np.array):
        self.pairwise_matrix = array

    def get_pairwise_matrix(self):
        return self.pairwise_matrix

    def input_subcriteria(self):
        have_subcriteria = input("Does {} have any sub criterion? (y for YES and n for NO)".format(self.name))
        if have_subcriteria.lower() == "y":
            while True:
                criterion_name = input("Enter your sub criterion for {} or 'q' for end:".format(self.name))
                if criterion_name.lower() == "q":
                    break
                criterion = Criterion(name=criterion_name)
                criterion.input_subcriteria()
                self.sub_criteria.append(criterion)

    def get_shape(self):
        if self.is_leaf():
            return len(self), len(self)
        else:
            return None

    def calc_priority_vector(self):
        for c in self.sub_criteria:
            if c.is_leaf():
                self.priority_list.append(c.global_priority)
                self.priority_names.append(c.name)
            else:
                c.calc_priority_vector()
                self.priority_list.extend(c.priority_list)
                self.priority_names.extend(c.priority_names)

    def input_priority(self):
        if not self.is_leaf():
            names = [c.name for c in self.sub_criteria]
            row, column = len(self), len(self)
            m = input_matrix("Pairwise Comparisons: Enter relative importance of {} to {}:",
                             row=row, column=column, names=names)
            self.update_pairwise_matrix(m)
            for sc in self.sub_criteria:
                # calc and update local priority of sub criteria
                m_normed = m / m.sum(axis=0)
                weights = m_normed.sum(axis=1)
                weights = weights / weights.sum()
                for i, w in enumerate(weights):
                    self.sub_criteria[i].priority = w
                    self.sub_criteria[i].global_priority = self.global_priority * w
                    sc.input_priority()  # recursive call

    def is_leaf(self):
        if len(self.sub_criteria) == 0:
            return True
        else:
            return False

    def draw(self, g: Digraph, alternatives):
        if len(self) == 0:
            for alternative in alternatives:
                g.edge(tail_name=self.name, head_name=alternative)
        else:
            for subcriterion in self.sub_criteria:
                g.node(name=subcriterion.name,
                       label=SC_NODE_LABEL.format(subcriterion.name, subcriterion.priority,
                                                  subcriterion.global_priority))
                g.edge(tail_name=self.name, head_name=subcriterion.name)
                subcriterion.draw(g, alternatives)

    def __len__(self):
        return len(self.sub_criteria)

    def __repr__(self):
        return "{}[sc={}, local priority={}]".format(self.name, str(len(self)), self.priority)