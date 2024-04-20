import sys
import debugpy
import argparse

from src.cbs.cbssearch import conflict_based_search
from src.cbs.cbsstate import CBSState
from src.utils import memory
from src.utils.info import handle_debug


class CBSSearchClient:
    @staticmethod
    def parse_level(server_messages) -> CBSState:
        # We can assume that the level file is conforming to specification, since the server verifies this.
        # Read domain.
        server_messages.readline()  # domain
        server_messages.readline()  # hospital

        # Read Level name.
        server_messages.readline()  # level name
        server_messages.readline().strip()  # <name>
        # Info.level_name = server_messages.readline().strip()  # <name>

        # Read initial state.
        # line is currently "#initial".
        return CBSState.make_initial_state(server_messages)

    @staticmethod
    def initialize_and_configure(args):
        """
        Initializes and configures the search client.

        :param args: The command line arguments.
        :return: The initial state and the frontier.
        """
        print(
            "SearchClient initializing.",
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
        initial_state = CBSSearchClient.parse_level(server_messages)

        # Info.test_name = args.test_name
        # Info.test_folder = args.test_folder

        return initial_state

    @staticmethod
    def execute_and_print_plan(initial_state, server_messages):
        """
        Executes the search plan and prints the results.

        :param initial_state: The initial state of the search.
        :param server_messages: The server messages.
        """
        print("Starting {}.".format("CBS with Meta Agent approach"), file=sys.stderr, flush=True)
        plan = conflict_based_search(initial_state)

        if plan is None:
            print("Unable to solve level.", file=sys.stderr, flush=True)
            sys.exit(0)
        else:
            print(
                "Found solution of length {}.".format(len(plan)),
                file=sys.stderr,
                flush=True,
            )
            states = [State(None) for _ in range(len(plan) + 1)]
            states[0] = initial_state
            for ip, joint_action in enumerate(plan):
                states[ip + 1] = states[ip].result(joint_action)
                print("|".join(a.get_name() + '@' for a in joint_action), flush=True)
                server_messages.readline()

    @staticmethod
    def main(args) -> None:
        initial_state = CBSSearchClient.initialize_and_configure(args)
        CBSSearchClient.execute_and_print_plan(initial_state, sys.stdin)

debug = False
fail_info = True
if __name__ == "__main__":
    handle_debug(debug)

    parser = argparse.ArgumentParser(description="Search client based on state-space conflict based graph search.")

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

    args = parser.parse_args()

    memory.max_usage = args.max_memory

    CBSSearchClient.main(args)
