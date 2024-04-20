from src.cbs.cbsconstraints import CBSConstraints


class CTNode:
    def __init__(self, constraints: CBSConstraints, solution, total_cost: int):
        self.constraints = constraints
        self.solution = solution
        self.total_cost = total_cost

    @staticmethod
    def sic(solution):
        """
        calculate Sum-of-Individual-Costs heuristics
        """
        return sum(len(sol) for sol in solution.items())

    def __lt__(self, other):
        return self.total_cost < other.total_cost

    def __str__(self):
        return str(self.constraints)

    def is_goal_node(self):
        pass
