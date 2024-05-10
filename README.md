# Hospital-Domain-AI
## Project Overview
The goal of the Hospital-Domain-AI project is to create an efficient client for the MAvis server that specifically complies with the hospital domain presented during classes. This project utilizes various search strategies to efficiently navigate through complex hospital layouts, allowing for the resolution of multi-agent pathfinding (MAPF) issues. Additionally, we offer the option to use more basic algorithms for search problems, which enables the comparison of different approaches.

### Prerequisites
- Java Runtime Environment (JRE) version 11 or above
- Python 3.6 or above

### Usage
The project supports various search strategies to tackle the MAPF/APF problems. Below are the commands to execute each strategy:

#### Breadth-First Search (BFS)
With saving the tests in the benchmarks folder:
```bash
java -jar ./server.jar -l ./levels/MAPF01.lvl -c "python searchclient.py -bfs --test-name bfs --test-folder ./benchmarks" -g
```
Without saving the tests:
```bash
java -jar ./server.jar -l ./levels/MAPF01.lvl -c "python searchclient.py -bfs" -g
```

#### Depth-First Search (DFS)
With saving the tests in the benchmarks folder:
```bash
java -jar ./server.jar -l ./levels/MAPF01.lvl -c "python searchclient.py -dfs --test-name dfs --test-folder ./benchmarks" -g
```
Without saving the tests:
```bash
java -jar ./server.jar -l ./levels/MAPF01.lvl -c "python searchclient.py -dfs" -g
```

#### Uniform-cost search (also known as Dijkstra)
With saving the tests in the benchmarks folder:
```bash
java -jar ./server.jar -l ./levels/MAPF01.lvl -c "python searchclient.py -greedy -s_dij --test-name greedy --test-folder ./benchmarks" -g
```
Without saving the tests:
```bash
java -jar ./server.jar -l ./levels/MAPF01.lvl -c "python searchclient.py -greedy -s_dij" -g
```

#### Greedy Best-First Search with Customized UCF (Currently Not Working)
With saving the tests in the benchmarks folder:
```bash
java -jar ./server.jar -l ./levels/MAPF01.lvl -c "python searchclient.py -greedy -c_dij --test-name greedy --test-folder ./benchmarks" -g
```
Without saving the tests:
```bash
java -jar ./server.jar -l ./levels/MAPF01.lvl -c "python searchclient.py -greedy -c_dij" -g
```

#### Iterated Width Search
```bash
java -jar ./server.jar -l ./levels/MAPF02C.lvl -c "python searchclient.py -iw -s_dij --test-name iw --test-folder ./benchmarks" -g      
java -jar ./server.jar -l ./levels/MAPF03.lvl -c "python searchclient.py -iw -s_dij --test-name iw --test-folder ./benchmarks" -g
java -jar ./server.jar -l ./levels/MAPF03C.lvl -c "python searchclient.py -iw -s_dij --test-name iw --test-folder ./benchmarks" -g
java -jar ./server.jar -l ./levels/SACrunch.lvl -c "python searchclient.py -iw -c_dij --test-name iw --test-folder ./benchmarks" -g

java -jar ./server.jar -l ./levels/generated/level_2.lvl -c "python searchclient.py -iw -c_dij --test-name test_level_2_cdij --test-folder ./benchmarks" -g
java -jar ./server.jar -l ./complevels/AgentWayz.lvl -c "python searchclient.py -iw -c_dij --test-name tests_cdij --test-folder ./benchmarks" -g
java -jar ./server.jar -l ./complevels/Tryhard.lvl -c "python searchclient.py -iw -c_dij --test-name tests_cdij --test-folder ./benchmarks" -g
```

Without saving the tests:
```bash
java -jar ./server.jar -l ./levels/MAPFreorder3.lvl -c "python searchclient.py -iw -c_dij" -g
java -jar ./server.jar -l ./complevels/AgentWayz.lvl -c "python searchclient.py -iw -c_dij" -g
java -jar ./server.jar -l ./levels/test3.lvl -c "python searchclient.py -iw -c_dij --profile" -g

java -jar ./server.jar -l ./complevels -c "python searchclient.py -iw -c_dij --test-name tests_cdij_improved --test-folder ./benchmarks" -t 300

java -jar ./server.jar -l ./complevels/Amogus.lvl -c "python searchclient.py -iw -c_dij" -g
```

