import argparse
import sys
import time

import debugpy

import memory
from color import Color
from info import Info
from frontier import Frontier, FrontierBFS, FrontierDFS, FrontierBestFirst
from graphsearch import Info, search
from heuristic import Heuristic, HeuristicAStar, HeuristicWeightedAStar, HeuristicGreedy, HeuristicType
from state import State
from action import Action

class SearchClient:
    @staticmethod
    def parse_level(server_messages) -> State:
        # We can assume that the level file is conforming to specification, since the server verifies this.
        # Read domain.
        server_messages.readline()  # #domain
        server_messages.readline()  # hospital

        # Read Level name.
        server_messages.readline()  # #levelname
        Info.level_name = server_messages.readline().strip()  # <name>

        # Read initial state.
        # line is currently "#initial".
        
        return State.make_initial_state(server_messages)

    @staticmethod
    def print_search_status(start_time: int, explored: list[State], frontier: Frontier) -> None:
        status_template = ('#Expanded: {:8,}, '
                           '#Frontier: {:8,}, '
                           '#Generated: {:8,}, '
                           'Time: {:3.3f} s'
                           '\n[Alloc: {:4.2f} MB, MaxAlloc: {:4.2f} MB]')
        elapsed_time = time.perf_counter() - start_time
        print(status_template.format(len(explored), frontier.size(), len(explored) + frontier.size(), elapsed_time,
                                     memory.get_usage(), memory.max_usage), file=sys.stderr, flush=True)

    @staticmethod
    def main(args) -> None:
        # Use stderr to print to the console.
        print('SearchClient initializing. I am sending this using the error output stream.', file=sys.stderr,
              flush=True)

        # Send client name to server.
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding='ASCII')
        print('SearchClient', flush=True)

        # We can also print comments to stdout by prefixing with a #.
        print('#This is a comment.', flush=True)

        # Parse the level.
        server_messages = sys.stdin
        if hasattr(server_messages, "reconfigure"):
            server_messages.reconfigure(encoding='ASCII')
        initial_state = SearchClient.parse_level(server_messages)

        Info.test_name = args.test_name
        Info.test_folder = args.test_folder

        ############ START: TO EDIT

        if args.simple:
            Heuristic.strategy = HeuristicType.Simple
        elif args.s_dij:
            Heuristic.strategy = HeuristicType.SimpleDijkstra
        elif args.c_dij:
            Heuristic.strategy = HeuristicType.ComplexDijkstra
        elif args.manhattan:
            Heuristic.strategy = HeuristicType.Manhattan
        else:
            Heuristic.strategy = HeuristicType.Simple

        # Select search strategy.
        if args.bfs:
            frontier = FrontierBFS()
        elif args.dfs:
            frontier = FrontierDFS()
        elif args.astar:
            frontier = FrontierBestFirst(HeuristicAStar(initial_state))
        elif args.wastar is not False:
            frontier = FrontierBestFirst(HeuristicWeightedAStar(initial_state, args.wastar))
        elif args.greedy:
            frontier = FrontierBestFirst(HeuristicGreedy(initial_state))
        else:
            # Default to BFS search.
            frontier = FrontierBFS()
            print('Defaulting to BFS search. '
                  'Use arguments -bfs, -dfs, -astar, -wastar, or -greedy to set the search strategy.',
                  file=sys.stderr,
                  flush=True)
        ############ END: TO EDIT


        # Search for a plan.
        print('Starting {}.'.format(frontier.get_name()), file=sys.stderr, flush=True)
        plan = search(initial_state, frontier)
        # Print plan to server.
        if plan is None:
            print('Unable to solve level.', file=sys.stderr, flush=True)
            sys.exit(0)
        else:
            print('Found solution of length {}.'.format(len(plan)), file=sys.stderr, flush=True)
            if True:
                states = [None for _ in range(len(plan) + 1)]
                states[0] = initial_state
            for ip, joint_action in enumerate(plan):
                states[ip + 1] = states[ip].result(joint_action)
                if Heuristic.strategy == HeuristicType.ComplexDijkstra:
                    my_message = str(frontier.heuristic.f(states[ip + 1])) 
                    action = Action.PullNE
                    if states[ip].is_applicable(0, action):
                        my_message  += "-" + str(frontier.heuristic.f(states[ip].result([action])))
                else:
                    my_message = None
                print("|".join(a.get_name() + '@' + (my_message if my_message is not None else a.get_name()) for a in joint_action), flush=True)
                # We must read the server's response to not fill up the stdin buffer and block the server.
                response = server_messages.readline()
                if fail_info:
                    answers = response.split('|')
                    failed = [a.strip() != 'true' for a in answers]
                    if any(failed):
                        print(f'''Failed move in s
                              tep: {ip}. @@ {"|".join(f"#{a.name_}#" for a in joint_action)} @@ {response}''',
                              flush=True)

                if True:
                    # states[ip + 1] = states[ip].result(joint_action)
                    # states[ip].is_conflicting(joint_action)
                    # states[ip].is_applicable(0, joint_action[0])
                    pass


debug = False
fail_info = False
if __name__ == '__main__':
    if debug:
        debugpy.listen(("localhost", 1234))  # Open a debugging server at localhost:1234
        debugpy.wait_for_client()  # Wait for the debugger to connect
        debugpy.breakpoint()  # Ensure the program starts paused

    # Program arguments.
    parser = argparse.ArgumentParser(description='Simple client based on state-space graph search.')
    parser.add_argument('--max-memory', metavar='<MB>', type=float, default=2048.0,
                        help='The maximum memory usage allowed in MB (soft limit, default 2048).')
    parser.add_argument('--test-name', metavar='<test_name>', type=str, default='default',
                        help='Name the file where the information will be stored.')
    parser.add_argument('--test-folder', metavar='<test_folder_path>', type=str, default='./tests',
                        help='Name the folder the files with the information will be stored.')
    strategy_group = parser.add_mutually_exclusive_group()
    strategy_group.add_argument('-bfs', action='store_true', dest='bfs', help='Use the BFS strategy.')
    strategy_group.add_argument('-dfs', action='store_true', dest='dfs', help='Use the DFS strategy.')
    strategy_group.add_argument('-astar', action='store_true', dest='astar', help='Use the A* strategy.')
    strategy_group.add_argument('-wastar', action='store', dest='wastar', nargs='?', type=int, default=False, const=5,
                                help='Use the WA* strategy.')
    strategy_group.add_argument('-greedy', action='store_true', dest='greedy', help='Use the Greedy strategy.')

    strategy_group2 = parser.add_mutually_exclusive_group()
    strategy_group2.add_argument('-simple', action='store_true', dest='simple', help='Use the Simple Heuristic.')
    strategy_group2.add_argument('-s_dij', action='store_true', dest='s_dij', help='Use the Simple Dijkstra Heuristic.')
    strategy_group2.add_argument('-c_dij', action='store_true', dest='c_dij',
                                 help='Use the Complex Dijkstra Heuristic.')
    strategy_group2.add_argument('-manhattan', action='store_true', dest='manhattan', help='Use the Manhattan Heuristic.')

    args = parser.parse_args()

    # Set max memory usage allowed (soft limit).
    memory.max_usage = args.max_memory

    # Run client.
    SearchClient.main(args)
