# Hospital-Domain-AI
The goal of the project is to construct an advanced client for the MAvis server using the hospital domain.

```bash
BFS
java -jar ./server.jar -l ./levels/MAPF01.lvl -c "python searchclient.py -bfs --test-name bfs --test-folder ../benchmarks" -g

DFS
java -jar ./server.jar -l ./levels/MAPF01.lvl -c "python searchclient.py -dfs --test-name dfs --test-folder ../benchmarks" -g

Greedy Simple Dijkstra
java -jar ./server.jar -l ./levels/MAPF01.lvl -c "python searchclient.py -greedy -s_dij --test-name greedy --test-folder ../benchmarks" -g

Greedy Complex Dijkstra (CURRENTLY NOT WORKING)
java -jar ./server.jar -l ./levels/MAPF01.lvl -c "python searchclient.py -greedy -c_dij --test-name greedy --test-folder ../benchmarks" -g

Iterated Width
java -jar ./server.jar -l ./levels/MAPF02C.lvl -c "python searchclient.py -iw -s_dij --test-name iw --test-folder ../benchmarks" -g      
java -jar ./server.jar -l ./levels/MAPF03.lvl -c "python searchclient.py -iw -s_dij --test-name iw --test-folder ../benchmarks" -g
java -jar ./server.jar -l ./levels/MAPF03C.lvl -c "python searchclient.py -iw -s_dij --test-name iw --test-folder ../benchmarks" -g
```
