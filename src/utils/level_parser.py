from typing import Tuple
from src.domain.atom import Box, encode_agent, Location, Atom, encode_box
from src.utils.color import Color

class Parser:
    @staticmethod
    def read_colors(server_messages):
        server_messages.readline()  # colors
        agent_colors = [None] * 10
        box_colors = [None] * 26
        boxes = {}
        line = server_messages.readline()
        while not line.startswith("#"):
            split = line.split(":")
            color = Color.from_string(split[0].strip())
            entities = [e.strip() for e in split[1].split(",")]
            for e in entities:
                if "0" <= e <= "9":
                    agent_colors[ord(e) - ord("0")] = color
                elif "A" <= e <= "Z":
                    if e not in boxes:
                        boxes[e] = []
                    boxes[e].append((e, len(boxes[e])))
                    box_colors[ord(e) - ord("A")] = color
            line = server_messages.readline()
        return agent_colors, box_colors, boxes

    @staticmethod
    def populate_literals(literals: list[Atom], line, row: int, walls: list[list[bool]] = None, agent_box_dict: dict[int, list[int]] = None, boxes_dict: dict[int, list[Tuple[int,int]]] = None):
        for col, c in enumerate(line):
            if "0" <= c <= "9":
                agent = ord(c) - ord("0")
                literals += [encode_agent((row, col), agent)]
            elif "A" <= c <= "Z":
                box = ord(c) - ord("A")
                if walls != None:
                    box_is_movable = any(box in boxes for boxes in agent_box_dict.values())
                    if not box_is_movable:
                        walls[row][col] = True  # Treat as a wall if no agent can move this box
                        continue # Don't include the box
                if box not in boxes_dict:
                    boxes_dict[box] = []
                new_boxgoal = (box, len(boxes_dict[box]))
                boxes_dict[box].append(new_boxgoal)
                literals += [encode_box((row, col), new_boxgoal)]  # Treat as a movable box
            elif walls != None and (c == "+" or c == "\n"):
                walls[row][col] = True

    @staticmethod
    def read_level(server_messages, agent_box_dict: dict[int, list[int]]):
        literals: list[Atom] = []
        num_rows = 0
        num_cols = 0
        level_lines = []
        line = server_messages.readline()
        while not line.startswith("#"):
            #extra trimming
            last_plus_index = line.rfind('+') # Finding the last index of '+'
            line = line[:last_plus_index + 1] # Slicing the string to keep everything up to the last '+'
            level_lines.append(line)
            num_cols = max(num_cols, len(line))
            num_rows += 1
            line = server_messages.readline()

        walls = [[False] * num_cols for _ in range(num_rows)]
        boxes: dict[int, list[Box]] = {}
        row = 0
        for line in level_lines:
            Parser.populate_literals(literals, line, row, walls, agent_box_dict, boxes)
            row += 1
        Location.calculate_all_neighbours(walls)
        return literals, num_rows, num_cols, walls, boxes

    @staticmethod
    def read_goal_state(server_messages):
        goal_literals: list[Atom] = []
        goal_boxes: dict[int, list[Box]] = {}
        line = server_messages.readline()
        row = 0
        while not line.startswith("#"):
            Parser.populate_literals(goal_literals, line, row, boxes_dict=goal_boxes)
            row += 1
            line = server_messages.readline()
        return goal_literals, goal_boxes

    @staticmethod
    def create_agent_box_dict(agent_colors, box_colors):
        return {
            i: [
                j
                for j, b in enumerate(box_colors)
                if b is not None and b == a
            ]
            for i, a in enumerate(agent_colors)
            if a is not None
        }
