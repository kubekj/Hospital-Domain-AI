import argparse
from dataclasses import dataclass
import itertools
import os
import sys
from typing import Any, List

from src.domain.atom import Location
from src.domain.leveldata import LevelData
from src.domain.action import Action
from src.domain.leveldata import LevelData
from src.domain.state import State
from src.frontiers.best_first import FrontierBestFirst
from src.frontiers.bfs import FrontierBFS
from src.frontiers.dfs import FrontierDFS
from src.frontiers.iw import FrontierIW
from src.heuristics.astar import HeuristicAStar
from src.heuristics.complex_dijkstra import HeuristicComplexDijkstra
from src.heuristics.manhattan import HeuristicManhattan
from src.heuristics.simple import HeuristicSimple
from src.heuristics.simple_dijkstra import HeuristicSimpleDijkstra
from src.heuristics.wastar import HeuristicWeightedAStar
from src.searches.graphsearch import Info, graph_search
from src.utils import memory
from src.utils.combiner import Combiner
from src.utils.info import handle_debug

import pickle

@dataclass
class StateInfo:
    initial: State
    heuristic: Any
    frontier: Any
    location: Any

class SearchClient:
    @staticmethod
    def parse_level(server_messages) -> LevelData:
        # We can assume that the level file is conforming to specification, since the server verifies this.
        # Read domain.
        leveldata: LevelData = LevelData()
        leveldata.parse_level(server_messages)
        leveldata.convert_dead_boxes_to_walls()
        leveldata.to_string_representation() #important don't remove
        Info.level_name = leveldata.levelname
        return leveldata
        # return State.make_initial_state(server_messages)

    @staticmethod
    def generate_state(leveldata: LevelData) -> State:
        #state generation
        return State.make_initial_state(leveldata)

    @staticmethod
    def set_heuristic_strategy(args, initial_state):
        if args.simple:
            return HeuristicSimple(initial_state)
        elif args.s_dij:
            return HeuristicSimpleDijkstra(initial_state)
        elif args.c_dij:
            return HeuristicComplexDijkstra(initial_state)
        elif args.manhattan:
            return HeuristicManhattan(initial_state)
        else:
            return HeuristicSimple(initial_state)

    @staticmethod
    def set_frontier_strategy(args, initial_state: State, heuristic, initialWidth=1):
        if args.bfs:
            return FrontierBFS()
        elif args.dfs:
            return FrontierDFS()
        elif args.astar:
            return FrontierBestFirst(HeuristicAStar(initial_state))
        elif args.wastar is not False:
            return FrontierBestFirst(HeuristicWeightedAStar(initial_state, args.wastar))
        elif args.greedy:
            return FrontierBestFirst(heuristic)
        elif args.iw:
            # Set initial width to the minimum of the number of agents or the initial width.
            width = min(len(initial_state.agent_locations), initialWidth)
            return FrontierIW(heuristic, width)
        else:
            print(
                "Defaulting to BFS search. "
                "Use arguments -bfs, -dfs, -astar, -wastar, or -greedy to set the search strategy.",
                file=sys.stderr,
                flush=True,
            )
            return FrontierBFS()

    @staticmethod
    def initClient():
        print(
            "SearchClient initializing. I am sending this using the error output stream.",
            file=sys.stderr,
            flush=True,
        )

        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="ASCII")

        print("SearchClient", flush=True)
        print("#This is a comment.", flush=True)

        server_messages = sys.stdin
        if hasattr(server_messages, "reconfigure"):
            server_messages.reconfigure(encoding="ASCII")
        
        return server_messages 

    @staticmethod
    def initialize_and_configure(args, leveldata):
        initial_state = SearchClient.generate_state(leveldata)

        heuristic = SearchClient.set_heuristic_strategy(args, initial_state)
        frontier = SearchClient.set_frontier_strategy(args, initial_state, heuristic)

        return initial_state, heuristic, frontier

    @staticmethod
    def execute_and_print_plan(initial_state, frontier, heuristic, server_messages):
        print("Starting {}.".format(frontier.get_name()), file=sys.stderr, flush=True)
        plan = graph_search(initial_state, frontier)

        if plan is None:
            print("Unable to solve level.", file=sys.stderr, flush=True)
            sys.exit(0)
        else:
            print(
                "Found solution of length {}.".format(len(plan)),
                file=sys.stderr,
                flush=True,
            )
            states: list[State] = [None] * (len(plan) + 1)
            states[0] = initial_state
            heuristic = SearchClient.set_heuristic_strategy(args, initial_state)
            frontier = SearchClient.set_frontier_strategy(args, initial_state, heuristic)
            with open("plans/plan.pkl", "wb") as f:
                pickle.dump(plan, file=f)
            for ip, joint_action in enumerate(plan):
                states[ip + 1] = states[ip].result(joint_action)
                my_message = None
                
                my_message = (
                    str(heuristic.f(states[ip + 1]))
                    if isinstance(heuristic, HeuristicComplexDijkstra)
                    else None
                )
                print(
                    "|".join(
                        a.get_name()
                        + "@"
                        + (my_message if my_message is not None else a.get_name())
                        for a in joint_action
                    ),
                    flush=True,
                )
                server_messages.readline()


    def SplitSearch(args, server_messages):
        #create all leveldatas
        leveldata:LevelData = SearchClient.parse_level(server_messages)

        sub_levels: List[LevelData] = leveldata.segment_regions()

        #do everything and create all plans from a-z, loop for all leveldatas
        #planCreationLoop
        plans = []
        for level in sub_levels:
            #setup
            level.to_string_representation() #important don't remove
            initial_state = SearchClient.generate_state(level)

            initial_state, heuristic, frontier = SearchClient.initialize_and_configure(args, level)
            heuristic = SearchClient.set_heuristic_strategy(args, initial_state)
            frontier = SearchClient.set_frontier_strategy(args, initial_state, heuristic)

            #create plan
            print("Starting {}.".format(frontier.get_name()), file=sys.stderr, flush=True)
            plan = graph_search(initial_state, frontier)

            if plan is None:
                print("Unable to solve level.", file=sys.stderr, flush=True)
                sys.exit(0)
            else:
                plans.append(plan)

        #combine plans
        final_plan = Combiner.combine_plans(plans, leveldata)

        #global object reset, necessary
        initial_state = SearchClient.generate_state(leveldata)
        initial_state, heuristic, frontier = SearchClient.initialize_and_configure(args, level)
        heuristic = SearchClient.set_heuristic_strategy(args, initial_state)
        frontier = SearchClient.set_frontier_strategy(args, initial_state, heuristic)

        SearchClient.print_found_plan_stuff(final_plan, initial_state, heuristic, args, server_messages)

    @staticmethod
    def print_found_plan_stuff(plan, initial_state, heuristic, args, server_messages):
        print(
            "Found solution of length {}.".format(len(plan)),
            file=sys.stderr,
            flush=True,
        )
        states: list[State] = [None] * (len(plan) + 1)
        states[0] = initial_state
        heuristic = SearchClient.set_heuristic_strategy(args, initial_state)
        frontier = SearchClient.set_frontier_strategy(args, initial_state, heuristic)
        with open("plans/plan.pkl", "wb") as f:
            pickle.dump(plan, file=f)
        for ip, joint_action in enumerate(plan):
            states[ip + 1] = states[ip].result(joint_action)
            my_message = None
            
            my_message = (
                str(heuristic.f(states[ip + 1]))
                if isinstance(heuristic, HeuristicComplexDijkstra)
                else None
            )
            print(
                "|".join(
                    a.get_name()
                    + "@"
                    + (my_message if my_message is not None else a.get_name())
                    for a in joint_action
                ),
                flush=True,
            )
            server_messages.readline()

    def execute_and_print_hardcoded_plan(initial_state, frontier, heuristic, server_messages):
        
        def load_pickle_files(directory):
            data_dict = {}
            # List all files in the directory
            for filename in os.listdir(directory):
                if filename.startswith("plan_") and filename.endswith(".pkl"):
                    # Extract the number X from the filename "plan_X.pkl"
                    number = int(filename.split('_')[1].split('.')[0])
                    # Construct the full path to the file
                    file_path = os.path.join(directory, filename)
                    # Load the pickle file
                    with open(file_path, 'rb') as file:
                        data_dict[number] = pickle.load(file)
                        if isinstance(data_dict[number] , list):
                            data_dict[number]:list[Action] = [el[0] for el in data_dict[number]]
                            for el in data_dict[number]:
                                el.agt = number

            return data_dict
        def merge_dict_arrays(data_dict):
            # Find the maximum length of any array in the dictionary
            max_length = max(len(lst) for lst in data_dict.values())

            # Extend each array to the maximum length using its key for the fill value
            extended_arrays = []
            for key, lst in data_dict.items():
                # Create new list with extended part filled with Action(key)
                extended_list = lst + [Action(key)] * (max_length - len(lst))
                extended_arrays.append(extended_list)
            
            # Now use zip (not zip_longest since all arrays are of equal length)
            return list(zip(*extended_arrays))
        print("Starting {}.".format(frontier.get_name()), file=sys.stderr, flush=True)
        sub_plans = load_pickle_files("./plans")
        plan = merge_dict_arrays(sub_plans)
        print(
            "Found solution of length {}.".format(len(plan)),
            file=sys.stderr,
            flush=True,
        )
        states: list[State] = [None] * (len(plan) + 1)
        states[0] = initial_state
        heuristic = SearchClient.set_heuristic_strategy(args, initial_state)
        frontier = SearchClient.set_frontier_strategy(args, initial_state, heuristic)
        for ip, joint_action in enumerate(plan):
            states[ip + 1] = states[ip].result(joint_action)
            my_message = None
            my_message = (
                str(heuristic.f(states[ip + 1]))
                if isinstance(heuristic, HeuristicComplexDijkstra)
                else None
            )
            print(
                "|".join(
                    a.get_name()
                    + "@"
                    + (my_message if my_message is not None else a.get_name())
                    for a in joint_action
                ),
                flush=True,
            )
            server_messages.readline()

    @staticmethod
    def main(args) -> None:
        server_messages = SearchClient.initClient()
        Info.test_name = args.test_name
        Info.test_folder = args.test_folder

        if not args:
            SearchClient.SplitSearch(args, server_messages)
        else: 
            leveldata:LevelData = SearchClient.parse_level(server_messages)
            initial_state, heuristic, frontier = SearchClient.initialize_and_configure(args, leveldata)
            SearchClient.execute_and_print_plan(initial_state, frontier, heuristic, sys.stdin)
            # SearchClient.execute_and_print_hardcoded_plan(initial_state, frontier, heuristic, sys.stdin)


debug = True
fail_info = True
if __name__ == "__main__":
    handle_debug(debug)

    # Program arguments.
    parser = argparse.ArgumentParser(
        description="Simple client based on state-space graph search."
    )

    parser.add_argument(
        "--max-memory",
        metavar="<MB>",
        type=float,
        default=2048.0,
        help="The maximum memory usage allowed in MB (soft limit, default 2048).",
    )

    parser.add_argument(
        "--test-name",
        metavar="<test_name>",
        type=str,
        default="default",
        help="Name the file where the information will be stored.",
        required=False
    )

    parser.add_argument(
        "--test-folder",
        metavar="<test_folder_path>",
        type=str,
        default="./tests",
        help="Name the folder the files with the information will be stored.",
        required=False
    )

    parser.add_argument(
        "--profile",
        action="store_true",
        default=False,
        help="Enable profiling with cProfile."
    )

    strategy_group = parser.add_mutually_exclusive_group()
    strategy_group.add_argument(
        "-bfs", action="store_true", dest="bfs", help="Use the BFS strategy."
    )
    strategy_group.add_argument(
        "-dfs", action="store_true", dest="dfs", help="Use the DFS strategy."
    )
    strategy_group.add_argument(
        "-iw", action="store_true", dest="iw", help="Use the IW strategy."
    )
    strategy_group.add_argument(
        "-astar", action="store_true", dest="astar", help="Use the A* strategy."
    )
    strategy_group.add_argument(
        "-wastar",
        action="store",
        dest="wastar",
        nargs="?",
        type=int,
        default=False,
        const=5,
        help="Use the WA* strategy.",
    )
    strategy_group.add_argument(
        "-greedy", action="store_true", dest="greedy", help="Use the Greedy strategy."
    )

    strategy_group2 = parser.add_mutually_exclusive_group()
    strategy_group2.add_argument(
        "-simple", action="store_true", dest="simple", help="Use the Simple Heuristic."
    )
    strategy_group2.add_argument(
        "-s_dij",
        action="store_true",
        dest="s_dij",
        help="Use the Simple Dijkstra Heuristic.",
    )
    strategy_group2.add_argument(
        "-c_dij",
        action="store_true",
        dest="c_dij",
        help="Use the Complex Dijkstra Heuristic.",
    )
    strategy_group2.add_argument(
        "-manhattan",
        action="store_true",
        dest="manhattan",
        help="Use the Manhattan Heuristic.",
    )

    args = parser.parse_args()

    # Set max memory usage allowed (soft limit).
    memory.max_usage = args.max_memory

    if args.profile:
        import cProfile
        import pstats
        profiler = cProfile.Profile()
        profiler.enable()

    # Run client.
    SearchClient.main(args)

    if args.profile:
        profiler.disable()
        stats = pstats.Stats(profiler).sort_stats('cumulative')
        stats.dump_stats('profile.prof')