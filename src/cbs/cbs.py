from queue import PriorityQueue


class CBSNode:
    def __init__(self, constraints, solutions, cost, merged_agents=None):
        self.constraints = constraints
        self.solutions = solutions
        self.cost = cost
        self.merged_agents = merged_agents if merged_agents is not None else {}

    def add_meta_agent(self, agents, merged_solution):
        meta_agent = tuple(sorted(agents))
        self.merged_agents[meta_agent] = agents
        self.solutions[meta_agent] = merged_solution
        for agent in agents:
            if agent in self.solutions:
                del self.solutions[agent]


def conflict_based_search(problem, agents, compute_cost):
    open_list = PriorityQueue()
    root = CBSNode(constraints=[], solutions={}, cost=0)
    root.solutions = {agent: a_star_search(problem, agent) for agent in agents}
    root.cost = compute_cost(root.solutions)
    open_list.put((root.cost, root))

    while not open_list.empty():
        current_cost, current_node = open_list.get()
        conflict = detect_conflicts(current_node.solutions)
        if conflict is None:
            return current_node.solutions
        new_nodes = resolve_conflicts(current_node, conflict)
        for node in new_nodes:
            node.cost = compute_cost(node.solutions)
            open_list.put((node.cost, node))

def detect_conflicts(solutions):
    locations = {}
    for agent, path in solutions.items():
        for time, position in enumerate(path):
            if (position, time) in locations:
                other_agent = locations[(position, time)]
                return agent, other_agent, position, time
            locations[(position, time)] = agent
    return None

def resolve_conflicts(node, conflict):
    agent1, agent2, position, time = conflict

