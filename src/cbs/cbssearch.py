import math
from queue import PriorityQueue

from src.cbs.cbsconstraints import CBSConstraints
from src.cbs.ctnode import CTNode
from src.frontiers.best_first import FrontierBestFirst
from src.heuristics.astar import HeuristicAStar
from src.searches.graphsearch import graph_search


def conflict_based_search(problem):
    agents = problem.agents
    root = CTNode(CBSConstraints(), {}, 0)
    root.solution = {
        agent: graph_search(problem, FrontierBestFirst(HeuristicAStar(problem))) for agent in agents
    }
    root.total_cost = CTNode.sic(root.solution)
    frontier = PriorityQueue()
    frontier.put((root.total_cost, root))

    while not frontier.empty():
        node = frontier.get()[1]
        if node.is_valid():
            return node.solution

        agent1, agent2, v, t = node.find_first_conflict()
        for a in [agent1, agent2]:
            copied_node = node.copy()
            copied_node.add_constraint(a, v, t)
            copied_node.solution[a] = spacetime_a_star_search(problem[a], copied_node.constraints)
            copied_node.total_cost = CTNode.sic(copied_node.solution)
            if copied_node.total_cost < math.inf:
                frontier.put((copied_node.total_cost, copied_node))

def detect_conflicts(solutions):
    pass

def resolve_conflicts(node, conflict):
    pass

