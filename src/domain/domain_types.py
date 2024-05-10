from typing import NamedTuple, Tuple


Atom = int #Making it easiet to spot the encoded literal
Box = Tuple[int, int]
Pos = NamedTuple("Pos", [("row", int), ("col", int)])
PosIn = Pos | Tuple[int, int]
LiteralList = list[set[Atom]]

def LiteralList_new(): return [set(), set()]