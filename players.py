# players.py
import random
from environment import BUILDING_TYPES, BUILDING_COSTS


class BasePlayer:
    def __init__(self, name):
        self.name = name
        self.self_score = 0
        self.final_score = 0

    def select_action(self, observation):
        # To be implemented by subclasses
        pass

    def update_state(self, reward, info):
        # Update scores based on the reward
        self.self_score += reward
        # Potentially update other scores based on info

    def is_cell_empty(self, grid, x, y):
        return grid[x][y][0] == 30 and grid[x][y][1] == 30 and grid[x][y][2] == 30


class EconomicPlayer(BasePlayer):
    def select_action(self, observation):
        # Prioritize building Shops
        grid = observation["grid"]
        resources = observation["resources"]
        available_actions = []
        for action_id in range(len(BUILDING_TYPES) * observation["grid"].shape[0] ** 2):
            building_type_idx = action_id // (observation["grid"].shape[0] ** 2)
            position_idx = action_id % (observation["grid"].shape[0] ** 2)
            building_type = BUILDING_TYPES[building_type_idx]
            x = position_idx // observation["grid"].shape[0]
            y = position_idx % observation["grid"].shape[0]
            if self.is_cell_empty(grid, x, y):
                # Check if player can afford to build Shop
                if building_type == "Shop":
                    if (
                        resources["money"] >= BUILDING_COSTS["Shop"]["money"]
                        and resources["reputation"]
                        >= BUILDING_COSTS["Shop"]["reputation"]
                    ):
                        available_actions.append(action_id)
        if available_actions:
            return random.choice(available_actions)
        else:
            # If no Shop actions available, try to build Park
            for action_id in range(
                len(BUILDING_TYPES) * observation["grid"].shape[0] ** 2
            ):
                building_type_idx = action_id // (observation["grid"].shape[0] ** 2)
                position_idx = action_id % (observation["grid"].shape[0] ** 2)
                building_type = BUILDING_TYPES[building_type_idx]
                x = position_idx // observation["grid"].shape[0]
                y = position_idx % observation["grid"].shape[0]
                if building_type == "Park" and self.is_cell_empty(grid, x, y):
                    if (
                        resources["money"] >= BUILDING_COSTS["Park"]["money"]
                        and resources["reputation"]
                        >= BUILDING_COSTS["Park"]["reputation"]
                    ):
                        available_actions.append(action_id)
            if available_actions:
                return random.choice(available_actions)
        # If no actions available, return a no-op (0)
        return 0


class ReputationPlayer(BasePlayer):
    def select_action(self, observation):
        # Prioritize building Parks and Houses
        grid = observation["grid"]
        resources = observation["resources"]
        available_actions = []
        for action_id in range(len(BUILDING_TYPES) * observation["grid"].shape[0] ** 2):
            building_type_idx = action_id // (observation["grid"].shape[0] ** 2)
            position_idx = action_id % (observation["grid"].shape[0] ** 2)
            building_type = BUILDING_TYPES[building_type_idx]
            x = position_idx // observation["grid"].shape[0]
            y = position_idx % observation["grid"].shape[0]
            if self.is_cell_empty(grid, x, y):
                if building_type in ["Park", "House"]:
                    if (
                        resources["money"] >= BUILDING_COSTS[building_type]["money"]
                        and resources["reputation"]
                        >= BUILDING_COSTS[building_type]["reputation"]
                    ):
                        available_actions.append(action_id)
        if available_actions:
            return random.choice(available_actions)
        else:
            # If no Park or House actions available, try to build Shop
            for action_id in range(
                len(BUILDING_TYPES) * observation["grid"].shape[0] ** 2
            ):
                building_type_idx = action_id // (observation["grid"].shape[0] ** 2)
                position_idx = action_id % (observation["grid"].shape[0] ** 2)
                building_type = BUILDING_TYPES[building_type_idx]
                x = position_idx // observation["grid"].shape[0]
                y = position_idx % observation["grid"].shape[0]
                if building_type == "Shop" and self.is_cell_empty(grid, x, y):
                    if (
                        resources["money"] >= BUILDING_COSTS["Shop"]["money"]
                        and resources["reputation"]
                        >= BUILDING_COSTS["Shop"]["reputation"]
                    ):
                        available_actions.append(action_id)
            if available_actions:
                return random.choice(available_actions)
        # If no actions available, return a no-op (0)
        return 0


class BalancedPlayer(BasePlayer):
    def select_action(self, observation):
        # Balance between building all types
        grid = observation["grid"]
        resources = observation["resources"]
        available_actions = []
        for action_id in range(len(BUILDING_TYPES) * observation["grid"].shape[0] ** 2):
            building_type_idx = action_id // (observation["grid"].shape[0] ** 2)
            position_idx = action_id % (observation["grid"].shape[0] ** 2)
            building_type = BUILDING_TYPES[building_type_idx]
            x = position_idx // observation["grid"].shape[0]
            y = position_idx % observation["grid"].shape[0]
            if self.is_cell_empty(grid, x, y):
                if (
                    resources["money"] >= BUILDING_COSTS[building_type]["money"]
                    and resources["reputation"]
                    >= BUILDING_COSTS[building_type]["reputation"]
                ):
                    available_actions.append(action_id)
        if available_actions:
            return random.choice(available_actions)
        # If no actions available, return a no-op (0)
        return 0
