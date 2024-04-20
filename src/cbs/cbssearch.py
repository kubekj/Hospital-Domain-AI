from queue import PriorityQueue

from src.cbs.cbsconstraints import CBSConstraints
from src.cbs.ctnode import CTNode


def conflict_based_search(problem, agents):
    root = CTNode(CBSConstraints(), {}, 0)
    root.solution = {
        agent: a_star_search(problem, agent) for agent in agents
    }
    root.total_cost = CTNode.sic(root.solution)
    frontier = PriorityQueue()
    frontier.put((root.total_cost, root))

    while not frontier.empty():
        ctnode = frontier.get()[1]
        if ctnode.is_goal_node():
            return ctnode.solution

        for child in ctnode.generate_children():
            frontier.put((child.total_cost, child))

def detect_conflicts(solutions):
    pass

def resolve_conflicts(node, conflict):
    pass

