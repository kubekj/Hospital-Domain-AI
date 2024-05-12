import sys

class LevelData:
    """
    The object contains string representations of the level and colors.\n
    it also contains lists of lists for the initial and goal states, and a dictionary for colors.
    """
    def __init__(self, initial=None, goal=None, colors=None):
        self.domain = ""
        self.levelname = ""
        self.string_colors = []
        self.string_initial = []
        self.string_goal = []

        # New data structures for use in processing
        self.colors = colors if colors else {}
        self.initial = initial if initial else []
        self.goal = goal if goal else []

        self.goals_list = {}
        self.agent_mapping = {}


    def add_color(self, color, items):
        self.colors[color] = items

    def parse_level(self, input_source):
        """
        Reads all level inputs from the server into the LevelData object.
        """
        mode = None
        for line in input_source:
            line = line.rstrip()  # Remove trailing whitespace and newline characters
            if line.startswith('#'):
                if line == '#domain':
                    mode = 'domain'
                    continue
                elif line == '#levelname':
                    mode = 'levelname'
                    continue
                elif line == '#colors':
                    mode = 'colors'
                    continue
                elif line == '#initial':
                    mode = 'initial'
                    continue
                elif line == '#goal':
                    mode = 'goal'
                    continue
                elif line == '#end':
                    self.normalize_level_lines()  # Normalize line lengths
                    self.remove_unseen_agents()  # Call to cleanup before ending parsing
                    break
                else:
                    mode = None  # Reset mode if it's another section
                    continue  # Skip processing this line further

            if mode == 'domain' and line:
                self.domain = line  # Capture the domain line
                mode = None  # Reset mode after capturing
            elif mode == 'levelname' and line:
                self.levelname = line  # Capture the level name line
                mode = None  # Reset mode after capturing
            elif mode == 'colors' and line:
                self.string_colors.append(line)
                key, value = line.split(':')
                self.colors[key.strip()] = [item.strip() for item in value.split(',')]
            elif mode == 'initial' and line:
                line = LevelData.trim_level_line(line)
                self.string_initial.append(line)
                self.initial.append(list(line))  # Converts string to list of characters
            elif mode == 'goal' and line:
                line = LevelData.trim_level_line(line)
                self.string_goal.append(line)
                self.goal.append(list(line))  # Converts string to list of characters

    def normalize_level_lines(self):
        """
        Ensures all lines in the initial level state are of equal length by padding with '+' symbols.
        """
        if not self.initial:  # If no lines have been parsed, return early
            return

        max_length = max(len(row) for row in self.initial)  # Find the maximum length of the rows

        # Pad each row with '+' until it reaches the maximum length
        for i in range(len(self.initial)):
            extra_length = max_length - len(self.initial[i])
            if extra_length > 0:
                self.initial[i] += ['+'] * extra_length  # Pad with '+'
                self.goal[i] += ['+'] * extra_length  # Pad with '+'

    def remove_unseen_agents(self):
        """
        Removes agents (digits) from the colors dictionary if they are not seen in the initial level layout,
        while retaining the boxes (letters A-Z).
        """
        all_seen_agents = set()
        for row in self.initial:
            for cell in row:
                if cell.isdigit():  # Check if the cell contains a digit which represents an agent
                    all_seen_agents.add(cell)

        # Filter colors to keep only agents that are seen in the initial state, keeping all box identifiers
        for color in list(self.colors.keys()):
            # Filter to keep boxes and only seen agents
            self.colors[color] = [item for item in self.colors[color] if item.isalpha() or item in all_seen_agents]

            # If no items left for the color, remove the color entry
            if not self.colors[color]:
                del self.colors[color]

    def convert_dead_boxes_to_walls(self):
        """
        Analyze for dead boxes and convert them to walls.
        """
        dead_colors = []
        for color, items in self.colors.items():
            has_boxes = any(item.isalpha() for item in items)
            has_agents = any(item.isdigit() for item in items)
            if has_boxes and not has_agents:
                dead_colors.append(color)

        for color in dead_colors:
            box_letters = [item for item in self.colors[color] if item.isalpha()]
            for index in range(len(self.initial)):
                for i in range(len(self.initial[index])):
                    if self.initial[index][i] in box_letters:
                        self.initial[index][i] = '+'
                        self.goal[index][i] = '+'  # Ensure the goal is also updated
            del self.colors[color]  # Remove the dead color

    @staticmethod
    def trim_level_line(line):
        """
        Removes additional spaces or characters on each line of a level.
        """
        last_plus_index = line.rfind('+')
        return line[:last_plus_index + 1]
    
    def to_string_representation(self):
        self.string_colors = [f"{color}: {', '.join(items)}" for color, items in self.colors.items()]
        self.string_initial = [''.join(row) for row in self.initial]
        self.string_goal = [''.join(row) for row in self.goal]

    # region flood fill
    def flood_fill(self, start, grid):
        x_size, y_size = len(grid[0]), len(grid)
        stack = [start]
        filled = set()
        region = []

        while stack:
            x, y = stack.pop()
            if (x, y) in filled or grid[y][x] == '+':
                continue
            filled.add((x, y))
            region.append((x, y))

            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < x_size and 0 <= ny < y_size and grid[ny][nx] != '+':
                    stack.append((nx, ny))

        return region

    def segment_regions(self):
        visited = set()
        regions = []

        for y in range(len(self.initial)):
            for x in range(len(self.initial[0])):
                if self.initial[y][x] != '+' and (x, y) not in visited:
                    region = self.flood_fill((x, y), self.initial)
                    region_goals = {}
                    for rx, ry in region:
                        goal = self.goal[ry][rx]
                        if goal.isdigit() or goal.isalpha():
                            region_goals[goal] = region_goals.get(goal, 0) + 1
                    if region_goals:
                        regions.append((region, region_goals))
                    visited.update(region)

        return self.create_level_data_from_regions(regions)

    def create_level_data_from_regions(self, regions):
        new_levels = []

        for region, region_goals in regions:
            new_initial = [['+' for _ in range(len(self.initial[0]))] for _ in range(len(self.initial))]
            new_goal = [['+' for _ in range(len(self.goal[0]))] for _ in range(len(self.goal))]
            new_colors = {}

            for x, y in region:
                new_initial[y][x] = self.initial[y][x]
                new_goal[y][x] = self.goal[y][x]
                element = self.initial[y][x]
                if element.isdigit() or element.isalpha():
                    for color, items in self.colors.items():
                        if element in items:
                            if color not in new_colors:
                                new_colors[color] = []
                            new_colors[color].append(element)

            if any(cell != '+' for row in new_goal for cell in row):  # Ensure there are goals in the region
                level = LevelData(
                    initial=new_initial,
                    goal=new_goal,
                    colors=new_colors
                )
                level.goals_list = region_goals  # Assign local goals to the specific region level
                new_levels.append(level)

        return new_levels
    # endregion flood fill

    # region agent-normalizing
    def normalize_agent_identifiers(self):
        """
        Renumber agents in self.colors, self.initial, and self.goal from 0 upwards based on their existing order,
        ensuring the agents are in the lowest possible numerical order.
        """
        agent_map = {}
        next_id = 0

        # Extract all digits from self.colors and create a new sorted mapping starting from 0
        for items in self.colors.values():
            for item in items:
                if item.isdigit() and item not in agent_map:
                    agent_map[item] = str(next_id)
                    next_id += 1

        # Update the agents in self.colors with new identifiers
        for color, items in self.colors.items():
            self.colors[color] = [agent_map[item] if item in agent_map else item for item in items]

        # Update agents in self.initial
        for i, row in enumerate(self.initial):
            self.initial[i] = [agent_map[cell] if cell in agent_map else cell for cell in row]

        # Update agents in self.goal
        for i, row in enumerate(self.goal):
            self.goal[i] = [agent_map[cell] if cell in agent_map else cell for cell in row]

        # Save the mapping for potential use by search algorithms to reverse the map if needed
        self.agent_mapping = agent_map
    # endregion agent-normalizing
