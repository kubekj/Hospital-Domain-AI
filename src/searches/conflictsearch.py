from src.domain.state import State


class ConflictBasedSearch:
    def __init__(self):
        self.constraints = None

    def conflict_based_search(self, initial_state: State, agents: list, cost: int):
        return None


'''
def ConflictBasedSearch (problem, agents, cost):
    root.constraints = []
    for a in agents:
        root.solution[a] = AStar(problem[a])
    root.cost = cost(root. solution)
    frontier = PriorityQueue (root, lambda n: n.cost)
    while not frontier.empty():
        node = frontier.get() # get lowest cost
        if IsValid (node.solution):
            return node.solution
        (a1, a2, v, t) = FindFirstConflict(node.solution)
        for a in [a1 , a2]:
            m = n.copy()
            m.constraints.append((a, v, t))
            m.solution[a] = SpaceTimeAStar(problem[a], m.constraints)
            m.cost = cost(m.solution)
            if m.cost < infinity: # solution is found
                frontier.put(m)
'''
