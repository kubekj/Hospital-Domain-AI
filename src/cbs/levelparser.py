from src.cbs.cbsagent import CBSAgent
from src.cbs.cbsbox import CBSBox
from src.cbs.cbsstate import CBSState
from src.utils.color import Color


def parse_initial_state(server_messages) -> CBSState:
    parse_domain(server_messages)
    agent_colors, box_colors = parse_colors(server_messages)
    walls, boxes, agent_rows, agent_cols, num_cols, num_rows = parse_level(server_messages)
    goals, goals_coords = parse_goals(server_messages, num_cols, num_rows)

    CBSState.agent_colors = agent_colors
    CBSState.box_colors = box_colors
    CBSState.walls = walls
    CBSState.goals = goals
    CBSState.goals_coords = goals_coords

    boxes = [CBSBox(label=chr(col + ord('A')), position=(row, col), color=box_colors[col])
             for row, cols in enumerate(boxes) for col, label in enumerate(cols) if label]

    agents = []
    for agent_id, (row, col) in enumerate(zip(agent_rows, agent_cols)):
        agent_boxes = {box for box in boxes if box.color == agent_colors[agent_id]}
        agents.append(CBSAgent(agent_id=agent_id,
                               start=(row, col),
                               goal=goals_coords[agent_id],
                               boxes=agent_boxes))

    return CBSState(agents, boxes)


def parse_domain(server_messages) -> None:
    # Read domain.
    server_messages.readline()  # domain
    server_messages.readline()  # hospital

    # Read Level name.
    server_messages.readline()  # level name
    server_messages.readline().strip()  # <name>


def parse_colors(server_messages):
    server_messages.readline()  # colors
    agent_colors = [None for _ in range(10)]
    box_colors = [None for _ in range(26)]
    line = server_messages.readline()
    while not line.startswith("#"):
        split = line.split(":")
        color = Color.from_string(split[0].strip())
        entities = [e.strip() for e in split[1].split(",")]
        for e in entities:
            if "0" <= e <= "9":
                agent_colors[ord(e) - ord("0")] = color
            elif "A" <= e <= "Z":
                box_colors[ord(e) - ord("A")] = color
        line = server_messages.readline()
    return agent_colors, box_colors


def parse_level(server_messages):
    num_rows = 0
    num_cols = 0
    level_lines = []
    line = server_messages.readline()
    while not line.startswith("#"):
        level_lines.append(line)
        num_cols = max(num_cols, len(line))
        num_rows += 1
        line = server_messages.readline()

    num_agents = 0
    agent_rows = [0 for _ in range(10)]
    agent_cols = [0 for _ in range(10)]
    walls = [[False for _ in range(num_cols)] for _ in range(num_rows)]
    boxes = [['' for _ in range(num_cols)] for _ in range(num_rows)]
    row = 0
    for line in level_lines:
        for col, c in enumerate(line):
            if '0' <= c <= '9':
                agent_rows[ord(c) - ord('0')] = row
                agent_cols[ord(c) - ord('0')] = col
                num_agents += 1
            elif 'A' <= c <= 'Z':
                boxes[row][col] = c
            elif c == '+' or c == '\n':
                walls[row][col] = True

        row += 1
    del agent_rows[num_agents:]
    del agent_rows[num_agents:]

    return walls, boxes, agent_rows, agent_cols, num_cols, num_rows


def parse_goals(server_messages, num_cols, num_rows):
    goals = [['' for _ in range(num_cols)] for _ in range(num_rows)]
    goals_coords = []
    line = server_messages.readline()
    row = 0
    while not line.startswith('#'):
        for col, c in enumerate(line):
            if '0' <= c <= '9' or 'A' <= c <= 'Z':
                goals[row][col] = c
                goals_coords.append((row, col))

        row += 1
        line = server_messages.readline()

    return goals, goals_coords
