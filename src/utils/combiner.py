
from typing import Dict, List
from src.domain.action import Action
from src.domain.leveldata import LevelData


from src.domain.action import Action
from src.domain.leveldata import LevelData

class Combiner:
    @staticmethod
    def combine_plans(plans: List[List[List[Action]]], leveldata: LevelData) -> List[List[Action]]:
        # Extract agent numbers from leveldata.colors
        agents = {agent for colors in leveldata.colors.values() for agent in colors if agent.isdigit()}

        # Determine the maximum number of timesteps in any plan
        max_length = max(len(plan) for plan in plans)

        # Initialize a list to store the combined actions for each timestep
        combined_plans = [[] for _ in range(max_length)]

        # Iterate through each timestep
        for timestep in range(max_length):
            # Initialize a dictionary to store the latest action for each agent at this timestep
            actions_this_step: Dict[str, Action] = {agent: Action(int(agent)) for agent in agents}

            # Gather actions for this timestep from each plan
            for plan in plans:
                if timestep < len(plan):
                    # Extract actions from the nested lists if necessary
                    actions_at_timestep = plan[timestep]
                    for action in actions_at_timestep:
                        # Check to ensure that action is indeed an Action object and not a sub-list or another type
                        if isinstance(action, Action):
                            actions_this_step[str(action.agt)] = action

            # Ensure every agent has an action at this timestep
            combined_timestep = [actions_this_step[agent] for agent in sorted(agents)]
            combined_plans[timestep] = combined_timestep

        return combined_plans

