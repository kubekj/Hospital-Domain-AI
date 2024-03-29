import json
import os
import os.path
import sys
import time

import memory
from action import Action
from frontier import Frontier, FrontierIW
from state import State
from info import Info

start_time = time.perf_counter()
saved_once = False


def search(initial_state: State, frontier: Frontier):
    if not saved_once:
        save_run_information(None, None, None, {'Passed': False})
    frontier.add(initial_state)
    explored = set()

    while True:

        # iterations += 1
        # if iterations % 1000 == 0:
        #     print_search_status(explored, frontier)

        # if memory.get_usage() > memory.max_usage:
        #     print_search_status(explored, frontier)
        #     print('Maximum memory usage exceeded.', file=sys.stderr, flush=True)
        #     return None

        if frontier.is_empty():
            if isinstance(frontier, FrontierIW):
                frontier = FrontierIW(frontier.heuristic,frontier.width+1)
                frontier.add(initial_state)
                explored = set()
                if frontier.is_empty():
                    return None
            else:
                return None

        state: State = frontier.pop()
        explored.add(state)
        

        if state.is_goal_state():
            plan = state.extract_plan()
            save_run_information(explored, frontier, plan)
            return plan

        # Assuming expanded_states is obtained from some state.get_expanded_states() method
        expanded_states = state.get_expanded_states()

        # Assuming heuristics is a list of heuristic values for each state in expanded_states
        heuristics = [frontier.heuristic.h(s) for s in expanded_states]

        # Combine expanded_states with their corresponding heuristics, sort by heuristic, and extract states
        sorted_states = [(h, state) for h, state in sorted(zip(heuristics, expanded_states), key=lambda x: x[0])]

        # Now sorted_states contains the states ordered by their heuristic values
        for expanded_state in [s for (_,s) in sorted_states]:
            if not frontier.contains(expanded_state) and expanded_state not in explored:
                frontier.add(expanded_state)


def print_search_status(explored:set[State], frontier):
    status_template = ('#Expanded: {:8,}, '
                       '#Frontier: {:8,}, '
                       '#Generated: {:8,}, '
                       'Time: {:3.3f} s'
                       '\n[Alloc: {:4.2f} MB, MaxAlloc: {:4.2f} MB]')
    elapsed_time = time.perf_counter() - start_time
    print(status_template.format(len(explored), frontier.size(), len(explored) + frontier.size(), elapsed_time,
                                 memory.get_usage(), memory.max_usage), file=sys.stderr, flush=True)


def save_run_information(explored:set[State], frontier, plan: list[list[Action]], information=None):
    elapsed_time = time.perf_counter() - start_time
    folder_path = Info.test_folder
    # Check if the folder exists, create it if it doesn't
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Folder '{folder_path}' created.")

    # Define the full path for the file
    file_path = os.path.join(folder_path, Info.test_name + '.json')
    all_data = deserialize_from_json_file(file_path)
    if information is None:
        information = {
            'Passed': True,
            'Expanded': len(explored),
            'Frontier': frontier.size(),
            'Generated': len(explored) + frontier.size(),
            'Solution length': len(plan),
            'Time': elapsed_time
        }
    all_data[Info.level_name] = information

    serialize_to_json_file(all_data, file_path)


def serialize_to_json_file(data, file_path: str):
    """
    Serializes the given data to a JSON file.

    :param data: The Python data structure to serialize.
    :param file_path: The path of the file where to save the JSON data.
    """
    try:
        with open(file_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)  # Pretty printing with 4 spaces indentation
        # print(f"Data successfully serialized to {file_path}")
    except Exception as e:
        # print(f"An error occurred during serialization: {e}")
        pass


def deserialize_from_json_file(file_path:str):
    """
    Deserializes JSON data from a file into a Python object.

    :param file_path: The path of the JSON file to read.
    :return: The deserialized Python object.
    """
    try:
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
        # print(f"Data successfully deserialized from {file_path}")
        return dict(data)
    except FileNotFoundError:
        # print(f"File not found: {file_path}")
        return {}
    except Exception as e:
        # print(f"An error occurred during deserialization: {e}")
        return {}
