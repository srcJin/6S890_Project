# environment.py
from pettingzoo.utils import AECEnv, agent_selector
from gymnasium import spaces
import numpy as np

# Define building types
BUILDING_TYPES = ["Park", "House", "Shop"]
BUILDING_COSTS = {
    "Park": {"money": 1, "reputation": 3},
    "House": {"money": 2, "reputation": 2},
    "Shop": {"money": 3, "reputation": 1},
}
BUILDING_UTILITIES = {
    "Park": {"money": -1, "reputation": 3},
    "House": {"money": 2, "reputation": 0},
    "Shop": {"money": 3, "reputation": -1},
}
BUILDING_EFFECTS = {
    "Park": {"G": 30, "V": -30, "D": 0, "neighbors": {"G": 10, "V": -10, "D": 0}},
    "House": {"G": -30, "V": 0, "D": 30, "neighbors": {"G": -10, "V": 10, "D": 10}},
    "Shop": {"G": -30, "V": 30, "D": -30, "neighbors": {"G": -10, "V": 10, "D": -10}},
}


class SimCityEnv(AECEnv):
    metadata = {"render.modes": ["human"]}

    def __init__(self):
        super().__init__()
        self.grid_size = 4
        self.agents = ["P1", "P2", "P3"]
        self.possible_agents = self.agents[:]
        self._agent_selector = agent_selector(self.agents)
        self.agent_selection = self._agent_selector.next()
        self.action_spaces = {
            agent: spaces.Discrete(self.grid_size**2 * len(BUILDING_TYPES))
            for agent in self.agents
        }
        self.observation_spaces = {
            agent: spaces.Dict(
                {
                    "grid": spaces.Box(
                        low=0,
                        high=100,
                        shape=(self.grid_size, self.grid_size, 3),
                        dtype=np.int32,
                    ),
                    "resources": spaces.Dict(
                        {
                            "money": spaces.Discrete(100),
                            "reputation": spaces.Discrete(100),
                        }
                    ),
                    "builders": spaces.Box(
                        low=-1,
                        high=len(self.agents) - 1,
                        shape=(self.grid_size, self.grid_size),
                        dtype=np.int32,
                    ),
                }
            )
            for agent in self.agents
        }
        self.reset()

    def reset(self):
        # Reset the game state
        self.grid = np.full(
            (self.grid_size, self.grid_size, 3), 30, dtype=np.int32
        )  # G, V, D
        self.buildings = np.full(
            (self.grid_size, self.grid_size), None
        )  # To track building types
        self.builders = np.full(
            (self.grid_size, self.grid_size), -1, dtype=np.int32
        )  # -1 indicates no builder
        self.rewards = {agent: 0 for agent in self.agents}
        self.infos = {agent: {} for agent in self.agents}
        self.terminations = {agent: False for agent in self.agents}
        self.truncations = {agent: False for agent in self.agents}
        self.players_resources = {
            agent: {"money": 10, "reputation": 10} for agent in self.agents
        }
        self.env_score = self.calculate_environment_score()
        self._cumulative_rewards = {agent: 0 for agent in self.agents}
        self._agent_selector.reset()
        self.agent_selection = self._agent_selector.next()
        self.num_moves = 0
        self.has_reset = True  # Indicate that the environment is ready for a step

    def step(self, action):
        if not self.has_reset:
            raise RuntimeError("Environment must be reset before calling step.")

        agent = self.agent_selection

        if self.terminations[agent]:
            # No action required if agent is terminated
            self._was_done_step(action)
            return

        # Reset the cumulative reward for this agent
        self._cumulative_rewards[agent] = 0

        # Initialize info
        self.infos[agent] = {}

        # Initialize reward for this step
        reward = 0

        # Decode action
        building_type, x, y = self.decode_action(action)

        # Check if the cell is empty
        if self.buildings[x][y] is not None:
            # Invalid action: cell already occupied
            # Assign a penalty
            reward -= 5  # Example penalty
        else:
            # Valid action
            # Get building details
            building_cost = BUILDING_COSTS[building_type]
            building_utility = BUILDING_UTILITIES[building_type]
            building_effect = BUILDING_EFFECTS[building_type]

            # Get player's resources
            player_resources = self.players_resources[agent]

            # Check if the player has enough resources
            if (
                player_resources["money"] < building_cost["money"]
                or player_resources["reputation"] < building_cost["reputation"]
            ):
                # Not enough resources to build
                # Assign a penalty
                reward -= 5  # Example penalty
            else:
                # Deduct resources
                player_resources["money"] -= building_cost["money"]
                player_resources["reputation"] -= building_cost["reputation"]

                # Apply building utility
                player_resources["money"] += building_utility["money"]
                player_resources["reputation"] += building_utility["reputation"]

                # Place the building
                self.buildings[x][y] = building_type

                # Record the builder
                self.builders[x][y] = self.agents.index(agent)

                # Update grid indices
                self.grid[x][y][0] += building_effect["G"]
                self.grid[x][y][1] += building_effect["V"]
                self.grid[x][y][2] += building_effect["D"]

                # Update adjacent cells
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                        self.grid[nx][ny][0] += building_effect["neighbors"]["G"]
                        self.grid[nx][ny][1] += building_effect["neighbors"]["V"]
                        self.grid[nx][ny][2] += building_effect["neighbors"]["D"]

                # Assign rewards based on building's utility
                # For simplicity, assign the utility as reward
                # Adjust this based on self_score and environment_score
                reward += building_utility["money"] + building_utility["reputation"]

        # Update cumulative reward for the agent
        self._cumulative_rewards[agent] += reward

        # Update rewards and infos for PettingZoo
        self.rewards[agent] = self._cumulative_rewards[agent]
        self.infos[agent] = self.infos[agent]

        # Check for game end conditions
        self.num_moves += 1
        if self.is_game_over():
            for ag in self.agents:
                self.terminations[ag] = True

        # Advance to the next agent
        self.agent_selection = self._agent_selector.next()

        # Allow the next step
        self.has_reset = True

    def decode_action(self, action):
        # Decode action to building type and position
        if (
            not isinstance(action, int)
            or action < 0
            or action >= self.grid_size**2 * len(BUILDING_TYPES)
        ):
            # Invalid action, return default action
            return "Park", 0, 0
        total_positions = self.grid_size**2
        building_type_idx = action // total_positions
        position_idx = action % total_positions
        building_type = BUILDING_TYPES[building_type_idx]
        x = position_idx // self.grid_size
        y = position_idx % self.grid_size
        return building_type, x, y

    def calculate_environment_score(self):
        G_avg = np.mean(self.grid[:, :, 0])
        V_avg = np.mean(self.grid[:, :, 1])
        D_avg = np.mean(self.grid[:, :, 2])
        env_score = (1 / 3) * G_avg + (1 / 3) * V_avg + (1 / 3) * D_avg
        return env_score

    def is_game_over(self):
        # Game ends when the board is filled or environment score < 10
        board_filled = np.all(self.buildings != None)
        env_score = self.calculate_environment_score()
        if board_filled or env_score < 10:
            return True
        return False

    def observe(self, agent):
        # Return the observation for the agent
        observation = {
            "grid": self.grid.copy(),
            "resources": self.players_resources[agent].copy(),
            "builders": self.builders.copy(),
        }
        return observation

    def render(self, mode="human"):
        # Render the game state as text
        display_grid = ""
        for x in range(self.grid_size):
            row = ""
            for y in range(self.grid_size):
                building = self.buildings[x][y]
                if building is None:
                    row += "[ ]"
                elif building == "Park":
                    row += "[P]"
                elif building == "House":
                    row += "[H]"
                elif building == "Shop":
                    row += "[S]"
            display_grid += row + "\n"
        print(display_grid)

    def close(self):
        pass

    def _was_done_step(self, action):
        # Required by PettingZoo
        self._cumulative_rewards[self.agent_selection] = 0
        self.rewards[self.agent_selection] = 0
        self.infos[self.agent_selection] = {}
        # Advance to the next agent
        self.agent_selection = self._agent_selector.next()
