# Hospital-Domain-AI
## Project Overview
The goal of the Hospital-Domain-AI project is to create an efficient client for the MAvis server that specifically complies with the hospital domain presented during the course. This project utilizes various search strategies to efficiently navigate through complex hospital layouts, allowing for the resolution of multi-agent pathfinding (MAPF) issues. Additionally, we offer the option to use basic as well as advanced algorithms for search problems, which enables the comparison of different approaches.

### Prerequisites
- Java Runtime Environment (JRE) version 11 or above
- Python 3.12 or above with specified packages:
  - numpy   
  - debugpy   
  - psutil  

## Usage
The project supports various search strategies to tackle the MAPF/APF problems. Below are the commands to execute each strategy:

#### Iterated Width Search with Customized UCF
```bash
java -jar ./server.jar -l ./complevels2024 -c "python searchclient.py" -t 180
```


