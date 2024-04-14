import random
import string
import sys

sys.setrecursionlimit(1_000_000)


class CellularAutomata:
    @staticmethod
    def random_fill(map_, width, height, percent_are_walls=40):
        random_column = random.randint(4, width - 5)

        for y in range(height):
            for x in range(width):
                if x != random_column and random.randint(0, 99) < percent_are_walls:
                    map_[x + y * width] = True

    @staticmethod
    def place_wall_logic(map_, width, height, x, y):
        return (
            CellularAutomata.count_adjacent_walls(map_, width, height, x, y) >= 6
            or CellularAutomata.count_nearby_walls(map_, width, height, x, y) <= 3
        )

    # region Algo
    @staticmethod
    def generate(width, height, iterations=4, percent_are_walls=40):
        map_ = [False] * (width * height)
        CellularAutomata.random_fill(map_, width, height, percent_are_walls)

        for _ in range(iterations):
            map_ = CellularAutomata.step(map_, width, height)

        return map_

    @staticmethod
    def step(map_, width, height):
        new_map = [False] * (width * height)

        for y in range(height):
            for x in range(width):
                if x == 0 or y == 0 or x == width - 1 or y == height - 1:
                    new_map[x + y * width] = True
                else:
                    new_map[x + y * width] = CellularAutomata.place_wall_logic(
                        map_, width, height, x, y
                    )

        return new_map

    @staticmethod
    def count_adjacent_walls(map_, width, height, x, y):
        walls = 0
        for mapX in range(x - 1, x + 2):
            for mapY in range(y - 1, y + 2):
                if map_[mapX + mapY * width]:
                    walls += 1
        return walls

    @staticmethod
    def count_nearby_walls(map_, width, height, x, y):
        walls = 0
        for mapX in range(x - 2, x + 3):
            for mapY in range(y - 2, y + 3):
                if abs(mapX - x) == 2 and abs(mapY - y) == 2:
                    continue
                if mapX < 0 or mapY < 0 or mapX >= width or mapY >= height:
                    continue
                if map_[mapX + mapY * width]:
                    walls += 1
        return walls

    @staticmethod
    def distance(pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    # @staticmethod
    # def place_agents_and_goals(map_, wall_logic, agent_logic):
    #     width, height = wall_logic['width'], wall_logic['height']
    #     n_agents, goal_threshold = agent_logic['n_agents'], agent_logic['goal_threshold']
    #     min_distance, max_distance = agent_logic['min_distance'], agent_logic['max_distance']

    #     open_tiles = [(x, y) for x in range(width) for y in range(height) if not map_[x + y * width]]
    #     random.shuffle(open_tiles)  # Shuffle open tiles to randomize agent placement

    #     agent_map = [' '] * (width * height)
    #     goal_map = [' '] * (width * height)
    #     agents_with_goals = random.sample(range(n_agents), k=int(n_agents * (goal_threshold / 100)))

    #     for agent_id in range(n_agents):
    #         if not open_tiles:
    #             break

    #         agent_pos = open_tiles.pop(0)
    #         agent_map[agent_pos[0] + agent_pos[1] * width] = str(agent_id + 1)

    #         if agent_id in agents_with_goals:
    #             valid_goal_tiles = [pos for pos in open_tiles if min_distance <= CellularAutomata.distance(agent_pos, pos) <= max_distance]
    #             if valid_goal_tiles:
    #                 goal_pos = random.choice(valid_goal_tiles)
    #                 open_tiles.remove(goal_pos)
    #                 goal_map[goal_pos[0] + goal_pos[1] * width] = str(agent_id + 1)
    #             else:
    #                 print(f"No valid goal found for agent {agent_id + 1} within the distance range.")

    #     return agent_map, goal_map

    @staticmethod
    def place_entities(
        map_, wall_logic, entity_logic, entity_map, goal_map, entity_type="agent"
    ):
        width, height = wall_logic["width"], wall_logic["height"]
        n_entities, goal_threshold = (
            entity_logic["n_entities"],
            entity_logic["goal_threshold"],
        )
        min_distance, max_distance = (
            entity_logic["min_distance"],
            entity_logic["max_distance"],
        )

        # Get tiles that are open and not already occupied by other entities
        open_tiles = [
            (x, y)
            for y in range(height)
            for x in range(width)
            if not map_[x + y * width] and entity_map[x + y * width] == " "
        ]
        random.shuffle(open_tiles)  # Shuffle open tiles to randomize agent placement
        entities_with_goals = random.sample(
            range(n_entities), k=int(n_entities * (goal_threshold / 100))
        )

        # Determine entity representation (letters for boxes, numbers for agents)
        if entity_type == "agent":
            entity_ids = map(str, range(n_entities))
        elif entity_type == "box":
            entity_ids = string.ascii_uppercase[:n_entities]

        entity_assigned = 0
        for entity_id in entity_ids:
            if not open_tiles:
                break
            x, y = open_tiles.pop(0)
            entity_map[x + y * width] = entity_id

            if entity_assigned in entities_with_goals:
                valid_goal_tiles = [
                    pos
                    for pos in open_tiles
                    if min_distance
                    <= CellularAutomata.distance((x, y), pos)
                    <= max_distance
                ]
                if valid_goal_tiles:
                    gx, gy = random.choice(valid_goal_tiles)
                    goal_map[gx + gy * width] = entity_id
                    open_tiles.remove((gx, gy))
                else:
                    print(
                        f"No valid goal found for {entity_id} within the distance range."
                    )
            entity_assigned += 1

        return entity_map, goal_map

    @staticmethod
    def print_combined_map(walls, agent_map, width, height):
        symbols = {" ": ".", "wall": "#"}

        for y in range(height):
            row = ""
            for x in range(width):
                idx = x + y * width
                if agent_map[idx] != " ":
                    row += agent_map[idx]
                else:
                    row += symbols["wall"] if walls[idx] else symbols[" "]
            print(row)

    # endregion


class Analysis:
    @staticmethod
    def summary(map, width, height):
        map_summary = {
            "loa": Analysis.largest_open_area(map, width, height),
            "caa": Analysis.count_accessible_areas(map, width, height),
            "cde": Analysis.count_dead_ends(map, width, height),
            "wtosr": Analysis.wall_to_open_space_ratio(map, width, height),
            "cn": Analysis.count_neighbors(map, width, height),
            "cuc": Analysis.count_uninterrupted_chains(map, width, height),
        }

        print("largest_open_area:", map_summary["loa"])
        print("count_accessible_areas:", map_summary["caa"])
        print("count_dead_ends:", map_summary["cde"])
        print(f"wall_to_open_space_ratio: {map_summary['wtosr']:.2f}")
        print("count_neighbors:", map_summary["cn"])
        print("count_uninterrupted_chains:", map_summary["cuc"][0])
        return map_summary

    @staticmethod
    def is_wall(map_, x, y, width, height):
        return x < 0 or x >= width or y < 0 or y >= height or map_[x + y * width]

    @staticmethod
    def is_open(map_, x, y, width, height):
        return not Analysis.is_wall(map_, x, y, width, height)

    @staticmethod
    def get_neighbors(map_, x, y, width, height, checkOpen=True):
        neighbors = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
        if checkOpen:
            return [
                (nx, ny)
                for nx, ny in neighbors
                if Analysis.is_open(map_, nx, ny, width, height)
            ]
        else:
            return [
                (nx, ny)
                for nx, ny in neighbors
                if Analysis.is_wall(map_, nx, ny, width, height)
            ]

    @staticmethod
    def flood_fill(map_, x, y, width, height, visited):
        if Analysis.is_wall(map_, x, y, width, height) or visited[y][x]:
            return 0
        visited[y][x] = True
        return 1 + sum(
            Analysis.flood_fill(map_, x + dx, y + dy, width, height, visited)
            for dx, dy in [(0, 1), (1, 0), (-1, 0), (0, -1)]
        )

    @staticmethod
    def largest_open_area(map_, width, height):
        visited = [[False for _ in range(width)] for _ in range(height)]
        largest_area = 0
        for y in range(height):
            for x in range(width):
                if not visited[y][x] and Analysis.is_open(map_, x, y, width, height):
                    area = Analysis.flood_fill(map_, x, y, width, height, visited)
                    largest_area = max(largest_area, area)
        return largest_area

    @staticmethod
    def count_accessible_areas(map_, width, height):
        visited = [[False for _ in range(width)] for _ in range(height)]
        areas = 0
        for y in range(height):
            for x in range(width):
                if not visited[y][x] and Analysis.is_open(map_, x, y, width, height):
                    Analysis.flood_fill(map_, x, y, width, height, visited)
                    areas += 1
        return areas

    @staticmethod
    def count_dead_ends(map_, width, height):
        dead_ends = 0
        for y in range(height):
            for x in range(width):
                if Analysis.is_open(map_, x, y, width, height):
                    walls = Analysis.get_neighbors(map_, x, y, width, height, False)
                    if len(walls) == 3:
                        dead_ends += 1
        return dead_ends

    @staticmethod
    def wall_to_open_space_ratio(map_, width, height):
        walls = sum(1 for cell in map_ if cell)
        open_spaces = width * height - walls
        return walls / open_spaces if open_spaces else float("inf")

    @staticmethod
    def count_neighbors(map_, width, height):
        counts = {
            1: 0,
            2: 0,
            3: 0,
            4: 0,
        }  # Initialize counts for each number of open neighbors
        for y in range(height):
            for x in range(width):
                if Analysis.is_open(map_, x, y, width, height):
                    open_neighbors = len(
                        Analysis.get_neighbors(map_, x, y, width, height)
                    )
                    if open_neighbors in counts:
                        counts[open_neighbors] += 1
        return counts

    @staticmethod
    def count_uninterrupted_chains(map_, width, height):
        visited = set()
        chains = 0
        modified_map = [" " for i in map_]

        for y in reversed(range(height)):
            for x in reversed(range(width)):
                if (x, y) not in visited and Analysis.is_open(
                    map_, x, y, width, height
                ):
                    open_neighbors = Analysis.get_neighbors(map_, x, y, width, height)

                    if len(open_neighbors) == 2 and (
                        open_neighbors[0][0] == open_neighbors[1][0]
                        or open_neighbors[0][1] == open_neighbors[1][1]
                    ):
                        nx, ny = x, y
                        chain_detected = False

                        while Analysis.is_open(map_, nx, ny, width, height):
                            current_neighbors = Analysis.get_neighbors(
                                map_, nx, ny, width, height
                            )
                            if len(current_neighbors) != 2:
                                break

                            # Mark the current cell as part of a chain
                            if not chain_detected:
                                chains += 1
                                chain_detected = True
                            modified_map[nx + ny * width] = str(chains)
                            visited.add((nx, ny))

                            # Determine the next cell in the chain
                            next_steps = [
                                n for n in current_neighbors if n not in visited
                            ]
                            if not next_steps:
                                break
                            nx, ny = next_steps[0]

        return chains, modified_map


class testGen:
    @staticmethod
    def write_map_section(file, section_name, map_, display_map, width, height):
        file.write(f"#{section_name}\n")
        for y in range(height):
            row = ""
            for x in range(width):
                idx = x + y * width
                if display_map[idx] != " ":
                    row += display_map[idx]
                elif map_[idx]:
                    row += "+"
                else:
                    row += " "
            file.write(row + "\n")

    @staticmethod
    def assign_colors(entities, colors, weights):
        color_assignments = {}
        for entity in entities:
            chosen_color = random.choices(colors, weights=weights, k=1)[0]
            if chosen_color in color_assignments:
                color_assignments[chosen_color].append(entity)
            else:
                color_assignments[chosen_color] = [entity]
        return color_assignments

    @staticmethod
    def write_map_to_file(
        map_, entity_map, goal_map, width, height, level_name, filename, color_logic
    ):
        colors = color_logic["colors"]
        agent_weights = color_logic["agent_weights"]
        box_weights = color_logic["box_weights"]

        agent_entities = [e for e in set(entity_map) - {" "} if e.isdigit()]
        box_entities = [e for e in set(entity_map) - {" "} if e.isalpha()]

        # Assign colors to agents and boxes based on weights
        agent_color_assignments = testGen.assign_colors(
            agent_entities, colors, agent_weights
        )
        # Try to only have boxes in a color of an existing agent
        valid_colors_and_weights = [
            (color, weight)
            for color, weight in zip(colors, box_weights)
            if color in agent_color_assignments and agent_color_assignments[color]
        ]
        filtered_colors, filtered_weights = (
            zip(*valid_colors_and_weights) if valid_colors_and_weights else ([], [])
        )
        box_color_assignments = testGen.assign_colors(
            box_entities, filtered_colors, filtered_weights
        )

        with open(f"./levels/generated/{filename}", "w") as file:
            file.write("#domain\n")
            file.write("hospital\n")
            file.write("#levelname\n")
            file.write(f"{level_name}\n")
            file.write("#colors\n")

            # Try and write agents before boxes
            combined_assignments = {
                color: agent_color_assignments.get(color, [])
                + box_color_assignments.get(color, [])
                for color in colors
            }
            for color, entities in combined_assignments.items():
                if entities:  # Only list colors with assigned entities
                    file.write(f"{color}: " + ", ".join(entities) + "\n")

            testGen.write_map_section(file, "initial", map_, entity_map, width, height)
            testGen.write_map_section(file, "goal", map_, goal_map, width, height)
            file.write("#end\n")

    @staticmethod
    def create_levels(
        num_levels, wall_logic, agent_logic, box_logic, color_logic, print_stats=True
    ):
        width, height = wall_logic["width"], wall_logic["height"]

        for i in range(num_levels):
            level_name = f"test-level-{i}"
            filename = f"level_{i}.lvl"

            # Generate maps
            walls = CellularAutomata.generate(**wall_logic)
            entity_map, goal_map = [" "] * (width * height), [" "] * (width * height)
            entity_map, goal_map = CellularAutomata.place_entities(
                walls, wall_logic, agent_logic, entity_map, goal_map
            )
            entity_map, goal_map = CellularAutomata.place_entities(
                walls, wall_logic, box_logic, entity_map, goal_map, entity_type="box"
            )

            if print_stats:
                print("---Summary---")
                sum = Analysis.summary(walls, width, height)
                # CellularAutomata.print_combined_map(walls, sum['cuc'][1], width, height)
                print("---End---")
                print()

            testGen.write_map_to_file(
                walls,
                entity_map,
                goal_map,
                width,
                height,
                level_name,
                filename,
                color_logic,
            )
            print(f"{level_name} written to {filename}")


if __name__ == "__main__":
    wall_logic_params = {
        "width": 15,
        "height": 10,
        "iterations": 2,
        "percent_are_walls": 50,
    }

    agent_logic_params = {
        "n_entities": 3,
        "goal_threshold": 100,  # 0-100
        "min_distance": 0,
        "max_distance": 200,
    }

    box_logic_params = {
        "n_entities": 1,
        "goal_threshold": 100,  # 0-100
        "min_distance": 0,
        "max_distance": 200,
    }
    color_logic_param = {
        "colors": [
            "blue",
            "red",
            "cyan",
            "purple",
            "green",
            "orange",
            "pink",
            "grey",
            "lightblue",
            "brown",
        ],
        "agent_weights": [1, 2, 3, 2, 1, 0, 0, 0, 0, 0],
        "box_weights": [0, 1, 2, 1, 1, 3, 2, 1, 0, 0],
    }

    testGen.create_levels(
        3, wall_logic_params, agent_logic_params, box_logic_params, color_logic_param
    )

    # walls = CellularAutomata.generate(**wall_logic_params)
    # agent_map, goal_map = CellularAutomata.place_agents_and_goals(walls, wall_logic_params, agent_logic_params)

    # width, height = wall_logic_params['width'], wall_logic_params['height']
    # print("Agent Map:")
    # CellularAutomata.print_combined_map(walls, agent_map, width, height)
    # print("\nGoal Map:")
    # CellularAutomata.print_combined_map(walls, goal_map, width, height)
    # print("\nWalls only:")
    # CellularAutomata.print_combined_map(walls, [" " for i in range(width*height)], width, height)

    # sum = Analysis.summary(walls, width, height);
    # CellularAutomata.print_combined_map(walls, sum['cuc'][1], width, height)

    # testGen.write_map_to_file(walls, agent_map, goal_map, width, height)
