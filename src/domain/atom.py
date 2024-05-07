from typing import Self


class Location:
    all_locations: list[Self] = []

    def __init__(self, row: int, col: int):
        self.row: int = row
        self.col: int = col
        self.neighbours: list[Location] = None
        if self not in self.all_locations:
            self.all_locations += [self]

    def __repr__(self):
        return f"Loc({self.row} , {self.col})"

    def __eq__(self, other: Self):
        return self.row == other.row and self.col == other.col

    def __hash__(self):
        return hash(str(self))

    def is_neighbour(self, loc: Self):
        return loc in self.neighbours

    def calculate_neighbours(self, walls: list[list[bool]]):
        possibilities = [(self.row, self.col - 1), (self.row, self.col + 1), (self.row - 1, self.col),
                         (self.row + 1, self.col)]
        self.neighbours = []
        for (r, c) in possibilities:
            if 0 <= r < len(walls):
                if 0 <= c < len(walls[r]):
                    i = self.all_locations.index(Location(r, c))
                    self.neighbours += [self.all_locations[i]]

    @staticmethod
    def calculate_all_neighbours(walls: list[list[bool]]):
        for loc in Location.all_locations:
            loc.calculate_neighbours(walls)


class Atom:
    def __init__(self, predicate, *args):
        self.predicate = predicate
        self.args = args

    def __repr__(self):
        return f"{self.predicate}({', '.join([str(el) for el in self.args])})"

    def __eq__(self, other):
        return self.predicate == other.predicate and self.args == other.args

    def __hash__(self):
        return hash((self.predicate,) + self.args)

    def eval(self):
        pass

    def effect(self):
        pass


class AgentAt(Atom):
    def __init__(self, agt: int, loc: Location):
        super().__init__("AgentAt", (agt, loc))
        self.agt = agt
        self.loc = loc


class Neighbour(Atom):
    def __init__(self, loc1: Location, loc2: Location):
        super().__init__("Neighbour", (loc1, loc2))
        self.loc1 = loc1
        self.loc2 = loc2

    def eval(self):
        return self.loc1.is_neighbour(self.loc2)

class Box:
    def __init__(self, name:str, id:int) -> None:
        self.name = name
        self.id = id
    def __str__(self) -> str:
        return f"{self.name}{self.id}"
    def __repr__(self) -> str:
        return str(self)
    def __hash__(self) -> int:
        return hash(str(self))
    def __eq__(self, other: Self):
        return other is None or (self.name == other.name and self.id == other.id)
    
class BoxGoal(Box):
    pass

class BoxAt(Atom):
    def __init__(self, box: Box, loc: Location):
        super().__init__("BoxAt", (box, loc))
        self.box = box
        self.loc = loc


class Free(Atom):
    walls = None

    def __init__(self, loc: Location):
        super().__init__("Free", (loc))
        self.loc = loc

    def eval(self, literals: set[Atom]):
        agent_at_literals = [lit for lit in literals if isinstance(lit, AgentAt)]
        box_at_literals = [lit for lit in literals if isinstance(lit, BoxAt)]
        return (not self.walls[self.loc.row][self.loc.col]
                and not any([lit.loc == self.loc for lit in agent_at_literals])
                and not any([lit.loc == self.loc for lit in box_at_literals]))
