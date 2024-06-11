# Hospital-Domain-AI
## Project Overview
The goal of this project is to create an efficient client for the MAvis server, specifically designed to comply with the hospital domain (described during the course). This project employs various search strategies to effectively navigate complex hospital layouts, addressing multi-agent pathfinding (MAPF) issues. Additionally, it offers the option to use both basic and advanced algorithms for search problems, enabling the comparison of different approaches, including problem planning and maze solving through Iterated Width (IW) search.

### Prerequisites
- Java Runtime Environment (JRE) version 11 or above
- Python 3.12 or above with specified packages:
  - numpy   
  - debugpy   
  - psutil  

## Usage
The project supports various search strategies to tackle the MAPF problems. Below are the commands to execute each strategy with level **MAPF01** as an example with a graphical representation, every bash command is equipped with a 180 seconds timeout indicated by "-t 180":

#### Breadth-First Search (BFS)
```bash
java -jar ./server.jar -l ./all_levels/levels/MAPF01.lvl -c "python searchclient.py -bfs" -g -t 180
```

#### Depth-First Search (DFS)
```bash
java -jar ./server.jar -l ./all_levels/levels/MAPF01.lvl -c "python searchclient.py -dfs" -g -t 180
```

#### Uniform-cost search (also known as Dijkstra)
```bash
java -jar ./server.jar -l ./all_levels/levels/MAPF01.lvl -c "python searchclient.py -greedy -s_dij" -g -t 180
```

#### Greedy Best-First Search with Customized UCF
```bash
java -jar ./server.jar -l ./all_levels/levels/MAPF01.lvl -c "python searchclient.py -greedy -c_dij" -g -t 180
```

#### Iterated Width Search with Customized UCF
```bash
java -jar ./server.jar -l ./all_levels/levels/MAPF01.lvl -c "python searchclient.py -iw -c_dij" -g -t 180
```

### Running all levels at once without visual representation (performance checking)
```bash
java -jar ./server.jar -l ./all_levels/levels -c "python searchclient.py" -t 180
```

#### Project Completed in Course 02285 Artificial Intelligence and Multi-Agent Systems - Technical University of Denmark (DTU)
<img src="https://user-images.githubusercontent.com/65953954/120001846-7f05f180-bfd4-11eb-8c11-2379a547dc9f.jpg" alt="drawing" width="100"/>


