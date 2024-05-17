from itertools import chain
import json
import os
import os.path
import sys
import time

from src.domain.atom import atom_repr, get_atom_location, encode_agent
from src.domain.domain_types import Atom
from src.frontiers.baseline.best_first import FrontierBestFirst
from src.frontiers.frontier import Frontier
from src.frontiers.iw import FrontierIW

from src.domain.state import State
from src.domain.action import Action

from src.utils import memory
from src.utils.info import Info

start_time = time.perf_counter()
SAVED_ONCE = True

def sort_by_y(x: Atom):
    return get_atom_location(x)[0]

def SIW(initial_state: State, frontier: FrontierIW):
    current_state = initial_state
    n_expl, n_front = 0, 0
    
    # goals = [sorted(a, key=sort_by_y) for a in initial_state.goal_literals_to_check]

    size = len(initial_state.goal_literals_to_check[0]) + len(initial_state.goal_literals_to_check[1])
    for i in range(1, size +1):
        # State.goal_literals_to_check = (goals[0][:i], goals[1][:i])
        print("#", frontier.size(), [atom_repr(a) for a in list(initial_state.goal_literals_to_check[0])[:i]])
        print("#", frontier.size(), [atom_repr(a) for a in list(initial_state.goal_literals_to_check[1])[:i]])
        state, explored, new_frontier = graph_search(current_state, frontier, i)
        if not state: return None
        current_state = state
        n_expl += len(explored)
        n_front += new_frontier.size()

    print("#", n_expl, n_front, n_expl + n_front)

    plan = current_state.extract_plan()
    save_run_information(n_expl, n_front, plan)
    return plan


def graph_search(initial_state: State, frontier: FrontierIW, g: int | None = None):
    if not SAVED_ONCE:
        save_run_information(None, None, None, {"Passed": False})

    iterations = 0
    frontier.add(initial_state)
    explored = set()

    while True:
        iterations += 1
        # log_search_status(iterations, explored, frontier)
        # print("#"+str(iterations),file=sys.stderr,flush=True,)

        if frontier.is_empty():
            if isinstance(frontier, FrontierIW):
                frontier = FrontierIW(frontier.heuristic, frontier.width + 1)
                frontier.add(initial_state)
                explored = set()
                if frontier.is_empty():
                    return None
            else:
                return None

        state = frontier.pop()
        explored.add(state)

        if state.is_goal_state(g):
            if g is not None: 
                return state, explored, frontier
            plan = state.extract_plan()
            save_run_information(explored, frontier, plan)
            return plan

        expanded_states = state.get_expanded_states()

        if isinstance(frontier, (FrontierIW, FrontierBestFirst)):
            heuristics = [frontier.heuristic.h(s) for s in expanded_states]
            sorted_states = sorted(zip(heuristics, expanded_states), key=lambda x: x[0])
            
            #WARNING: By discarding unlikely states, we can achieve a massive speedup in some levels, but it might be problamatic in cases where our heuristic performs badly.
            cutoff_index = max(int(len(sorted_states) * 0.2), 10) 
            expanded_states = [s for _, s in sorted_states[:cutoff_index]]

        for expanded_state in expanded_states:
            if not frontier.contains(expanded_state) and expanded_state not in explored:
                frontier.add(expanded_state)


def log_search_status(iterations, explored: set[State], frontier):
    iterations += 1
    if iterations % 1000 == 0:
        print_search_status(explored, frontier)

    if memory.get_usage() > memory.max_usage:
        print_search_status(explored, frontier)
        # TODO: Reset frontier after memory limit is reached, go to next width for IW
        print("Maximum memory usage exceeded.", file=sys.stderr, flush=True)
        return None


def print_search_status(explored: set[State], frontier):
    status_template = (
        "#Expanded: {:8,}, "
        "#Frontier: {:8,}, "
        "#Generated: {:8,}, "
        "Time: {:3.3f} s"
        "\n[Alloc: {:4.2f} MB, MaxAlloc: {:4.2f} MB]"
    )
    elapsed_time = time.perf_counter() - start_time
    print(
        status_template.format(
            len(explored),
            frontier.size(),
            len(explored) + frontier.size(),
            elapsed_time,
            memory.get_usage(),
            memory.max_usage,
        ),
        file=sys.stderr,
        flush=True,
    )


def save_run_information(explored: set[State] | int, frontier: Frontier | int, plan: list[list[Action]], information=None):
    """
    This function saves the information about the current run of the search algorithm.

    :param explored: A set of states that have been explored by the search algorithm.
    :param frontier: The frontier used by the search algorithm. It should have a size() method.
    :param plan: A list of lists of actions representing the plan found by the search algorithm.
    :param information: An optional dictionary containing additional information to be saved. If not provided, a default dictionary is created with the following keys:
        - 'Passed': Always set to True.
        - 'Expanded': The number of states expanded by the search algorithm.
        - 'Frontier': The size of the frontier at the end of the search.
        - 'Generated': The total number of states generated by the search algorithm.
        - 'Solution length': The length of the plan found by the search algorithm.
        - 'Time': The time taken by the search algorithm.
    """
    elapsed_time = time.perf_counter() - start_time
    folder_path = Info.test_folder

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Folder '{folder_path}' created.")

    file_path = os.path.join(folder_path, Info.test_name + ".json")

    all_data = deserialize_from_json_file(file_path)

    n_expl = explored if isinstance(explored, int) else len(explored)
    n_front = frontier if isinstance(frontier, int) else frontier.size()
    if information is None:
        information = {
            "Passed": True,
            "Expanded": n_expl,
            "Frontier": n_front,
            "Generated": n_expl + n_front,
            "Solution length": len(plan),
            "Time": elapsed_time,
        }

    all_data[Info.level_name] = information
    serialize_to_json_file(all_data, file_path)


def serialize_to_json_file(data, file_path: str):
    try:
        with open(file_path, "w") as json_file:
            json.dump(data, json_file, indent=4)  # Pretty printing with 4 spaces indentation
    except Exception as e:
        print(f"An error occurred during serialization: {e}")
        pass


def deserialize_from_json_file(file_path: str):
    try:
        with open(file_path, "r") as json_file:
            data = json.load(json_file)
        return dict(data)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return {}
    except Exception as e:
        print(f"An error occurred during deserialization: {e}")
        return {}
