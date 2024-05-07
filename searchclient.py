import argparse
import sys

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
from src.utils.info import handle_debug

class SearchClient:
    @staticmethod
    def parse_level(server_messages) -> State:
        # We can assume that the level file is conforming to specification, since the server verifies this.
        # Read domain.
        server_messages.readline()  # domain
        server_messages.readline()  # hospital

        # Read Level name.
        server_messages.readline()  # level name
        Info.level_name = server_messages.readline().strip()  # <name>

        # Read initial state.
        # line is currently "#initial".
        return State.make_initial_state(server_messages)

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
    def set_frontier_strategy(args, initial_state, heuristic):
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
            return FrontierIW(heuristic, 2)
        else:
            print(
                "Defaulting to BFS search. "
                "Use arguments -bfs, -dfs, -astar, -wastar, or -greedy to set the search strategy.",
                file=sys.stderr,
                flush=True,
            )
            return FrontierBFS()

    @staticmethod
    def initialize_and_configure(args):
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
        initial_state = SearchClient.parse_level(server_messages)

        Info.test_name = args.test_name
        Info.test_folder = args.test_folder

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
            for ip, joint_action in enumerate(plan):
                states[ip + 1] = states[ip].result(joint_action)
                if isinstance(heuristic, HeuristicComplexDijkstra):
                    my_message = str(heuristic.f(states[ip + 1]))
                else:
                    my_message = None
                print("|".join(a.get_name() + '@' + (my_message if my_message is not None else a.get_name()) for a in
                               joint_action), flush=True)
                server_messages.readline()

    @staticmethod
    def main(args) -> None:
        initial_state, heuristic, frontier = SearchClient.initialize_and_configure(args)
        SearchClient.execute_and_print_plan(initial_state, frontier, heuristic, sys.stdin)


debug = False
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