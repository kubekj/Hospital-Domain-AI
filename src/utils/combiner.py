
from typing import Dict, List

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

    @staticmethod
    def revert_plan_identifiers_listofactions(level_data, plan):
        """
        Reverts agent identifiers in a given plan using the agent_mapping from a LevelData object.

        :param level_data: LevelData object containing agent_mapping for identifier conversion.
        :param plan: List of actions (e.g., [Move(), Push(), Pull()...]) with updated agent identifiers.
        :return: Modified plan with original agent identifiers.
        """
        if not hasattr(level_data, 'agent_mapping'):
            raise AttributeError("LevelData object does not have an agent_mapping attribute")

        # Create a reverse mapping from the new ID to the original ID
        reverse_mapping = {new_id: old_id for old_id, new_id in level_data.agent_mapping.items()}

        # Helper function to revert agent IDs in actions
        def revert_agent_id(action: Action):
            original_id = reverse_mapping.get(str(action.agt), action.agt)
            return action.update_id(int(original_id))

        # Process each action in the plan to revert agent IDs
        reverted_plan = []
        for action_list in plan:
            reverted_actions = []
            for action in action_list:
                reverted_actions.append(revert_agent_id(action))
            reverted_plan.append(reverted_actions)

        return reverted_plan