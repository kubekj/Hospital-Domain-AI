import json
import os
import os.path
import sys
import time

from src.frontiers.best_first import FrontierBestFirst
from src.frontiers.frontier import Frontier
from src.frontiers.iw import FrontierIW

from src.domain.state import State
from src.domain.action import Action

from src.utils import memory
from src.utils.info import Info

start_time = time.perf_counter()
saved_once = True


def graph_search(initial_state, frontier: Frontier):
    if not saved_once:
        save_run_information(None, None, None, {"Passed": False})

    # iterations = 0
    frontier.add(initial_state)
    explored = set()

    while True:
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

        if state.is_goal_state():
            plan = state.extract_plan()
            save_run_information(explored, frontier, plan)
            return plan

        # Assuming expanded_states is obtained from some state.get_expanded_states() method
        expanded_states = state.get_expanded_states()
        # print("#Expanded states:", expanded_states)

        if isinstance(frontier, (FrontierIW, FrontierBestFirst)):
            heuristics = [frontier.heuristic.h(s) for s in expanded_states]
            sorted_states = sorted(zip(heuristics, expanded_states), key=lambda x: x[0])
            expanded_states = [s for _, s in sorted_states]

        for expanded_state in expanded_states:
            if not frontier.contains(expanded_state) and expanded_state not in explored:
                frontier.add(expanded_state)


def log_search_status(iterations, explored: set[State], frontier):
    iterations += 1
    if iterations % 1000 == 0:
        print_search_status(explored, frontier)

    if memory.get_usage() > memory.max_usage:
        print_search_status(explored, frontier)
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


def save_run_information(
    explored: set[State], frontier, plan: list[list[Action]], information=None
):
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

    # Check if the folder for saving the run information exists. If not, create it.
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Folder '{folder_path}' created.")

    # The file path for saving the run information.
    file_path = os.path.join(folder_path, Info.test_name + ".json")

    # Deserialize the existing data from the file.
    all_data = deserialize_from_json_file(file_path)

    # If no additional information is provided, create a default dictionary.
    if information is None:
        information = {
            "Passed": True,
            "Expanded": len(explored),
            "Frontier": frontier.size(),
            "Generated": len(explored) + frontier.size(),
            "Solution length": len(plan),
            "Time": elapsed_time,
        }

    # Add the information about the current run to the existing data.
    all_data[Info.level_name] = information

    # Serialize the updated data back to the file.
    serialize_to_json_file(all_data, file_path)


def serialize_to_json_file(data, file_path: str):
    """
    Serializes the given data to a JSON file.

    :param data: The Python data structure to serialize.
    :param file_path: The path of the file where to save the JSON data.
    """
    try:
        with open(file_path, "w") as json_file:
            json.dump(
                data, json_file, indent=4
            )  # Pretty printing with 4 spaces indentation
        # print(f"Data successfully serialized to {file_path}")
    except Exception as e:
        print(f"An error occurred during serialization: {e}")
        pass


def deserialize_from_json_file(file_path: str):
    """
    Deserializes JSON data from a file into a Python object.

    :param file_path: The path of the JSON file to read.
    :return: The deserialized Python object.
    """
    try:
        with open(file_path, "r") as json_file:
            data = json.load(json_file)
        # print(f"Data successfully deserialized from {file_path}")
        return dict(data)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return {}
    except Exception as e:
        print(f"An error occurred during deserialization: {e}")
        return {}
