# Hospital-Domain-AI
## Project Overview
The goal of the Hospital-Domain-AI project is to create an efficient client for the MAvis server that specifically complies with the hospital domain presented during the course. This project utilizes various search strategies to efficiently navigate through complex hospital layouts, allowing for the resolution of multi-agent pathfinding (MAPF) issues. Additionally, we offer the option to use basic as well as advanced algorithms for search problems, which enables the comparison of different approaches.

### Prerequisites
- Java Runtime Environment (JRE) version 11 or above
- Python 3.6 or above

## Usage
The project supports various search strategies to tackle the MAPF/APF problems. Below are the commands to execute each strategy:

### Basic Search Strategies

#### Breadth-First Search (BFS)

```bash
java -jar ./server.jar -l ./levels/MAPF01.lvl -c "python searchclient.py -bfs" -g
```

#### Depth-First Search (DFS)
```bash
java -jar ./server.jar -l ./levels/MAPF01.lvl -c "python searchclient.py -dfs" -g
```

#### Uniform-cost search (also known as Dijkstra)
```bash
java -jar ./server.jar -l ./levels/MAPF01.lvl -c "python searchclient.py -greedy -s_dij" -g
```

### Advanced Search Strategies

#### Greedy Best-First Search with Customized UCF
```bash
java -jar ./server.jar -l ./levels/MAPF01.lvl -c "python searchclient.py -greedy -c_dij" -g
```

#### Iterated Width Search with Customized UCF
```bash
java -jar ./server.jar -l ./complevels/mishmash.lvl -c "python searchclient.py -iw -c_dij" -g
```

