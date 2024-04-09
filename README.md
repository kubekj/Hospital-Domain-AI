# Hospital-Domain-AI
## Project Overview
The goal of the Hospital-Domain-AI project is to create an efficient client for the MAvis server that specifically complies with the hospital domain presented during classes. This project utilizes various search strategies to efficiently navigate through complex hospital layouts, allowing for the resolution of multi-agent pathfinding (MAPF) issues. Additionally, we offer the option to use more basic algorithms for search problems, which enables the comparison of different approaches.

### Prerequisites
- Java Runtime Environment (JRE) version 11 or above
- Python 3.6 or above

### Usage
The project supports various search strategies to tackle the MAPF/APF problems. Below are the commands to execute each strategy:

#### Breadth-First Search (BFS)

```bash
java -jar ./server.jar -l ./levels/MAPF01.lvl -c "python searchclient.py -bfs --test-name bfs --test-folder ../benchmarks" -g
```

#### Depth-First Search (DFS)
```bash
java -jar ./server.jar -l ./levels/MAPF01.lvl -c "python searchclient.py -dfs --test-name dfs --test-folder ../benchmarks" -g

```

#### Uniform-cost search (also known as Dijkstra)
```bash
java -jar ./server.jar -l ./levels/MAPF01.lvl -c "python searchclient.py -greedy -s_dij --test-name greedy --test-folder ../benchmarks" -g
```

#### Greedy Best-First Search with Customized UCF (Currently Not Working)
```bash
java -jar ./server.jar -l ./levels/MAPF01.lvl -c "python searchclient.py -greedy -c_dij --test-name greedy --test-folder ../benchmarks" -g
```

#### Iterated Width Search
```bash
java -jar ./server.jar -l ./levels/MAPF02C.lvl -c "python searchclient.py -iw -s_dij --test-name iw --test-folder ../benchmarks" -g      
java -jar ./server.jar -l ./levels/MAPF03.lvl -c "python searchclient.py -iw -s_dij --test-name iw --test-folder ../benchmarks" -g
java -jar ./server.jar -l ./levels/MAPF03C.lvl -c "python searchclient.py -iw -s_dij --test-name iw --test-folder ../benchmarks" -g

java -jar ./server.jar -l ./levels/test_push.lvl -c "python searchclient.py -iw -c_dij --test-name iw --test-folder ../benchmarks" -g
java -jar ./server.jar -l ./levels/test.lvl -c "python searchclient.py -iw -c_dij --test-name iw --test-folder ../benchmarks" -g

java -jar ./server.jar -l ./levels/SAFirefly.lvl -c "python searchclient.py -iw -s_dij --test-name iw --test-folder ../benchmarks" -g
```

