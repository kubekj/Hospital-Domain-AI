# Hospital-Domain-AI
The goal of the project is to construct an advanced client for the MAvis server using the hospital domain.


java -jar ./server.jar -l ./levels/BFSfriendly-1.lvl -c "python src/searchclient.py -bfs --test-name bfs --test-folder ../benchmarks" -g -t 300
java -jar ./server.jar -l ./levels/MAPF00.lvl -c "python src/searchclient.py -bfs --test-name bfs --test-folder ../benchmarks" -g
java -jar ./server.jar -l ./levels/MAPF01.lvl -c "python src/searchclient.py -bfs --test-name bfs --test-folder ../benchmarks" -g
java -jar ./server.jar -l ./levels/MAPF02.lvl -c "python src/searchclient.py -iw --test-name iw --test-folder ../benchmarks" -g
java -jar ./server.jar -l ./levels/MAPF02C.lvl -c "python src/searchclient.py -iw -s_dij --test-name iw --test-folder ../benchmarks" -g
java -jar ./server.jar -l ./levels/MAPF03.lvl -c "python src/searchclient.py -iw -s_dij --test-name iw --test-folder ../benchmarks" -g
java -jar ./server.jar -l ./levels/MAPF03C.lvl -c "python src/searchclient.py -iw -s_dij --test-name iw --test-folder ../benchmarks" -g