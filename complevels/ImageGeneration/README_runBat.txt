Setup:
First modify perhaps the graphsearch.py file so it just outputs this

    MAPF00_sol = [[Action.MoveS]] * 2 + [[Action.MoveE]] * 10 + [[Action.MoveS]] * 2
        
    return MAPF00_sol

How to run:
.\create_images_of_levels.bat