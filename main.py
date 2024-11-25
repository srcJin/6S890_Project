# main.py

from environment import SimCityEnv
from players import EconomicPlayer, ReputationPlayer, BalancedPlayer
from log import display_board, display_player_stats, display_current_turn


def main():
    # Initialize the environment
    env = SimCityEnv()
    env.reset()

    # Initialize players with different strategies
    players = {
        "P1": EconomicPlayer(name="P1"),
        "P2": ReputationPlayer(name="P2"),
        "P3": BalancedPlayer(name="P3"),
    }

    max_moves = 50  # Set the maximum number of moves
    move_count = 0  # Initialize move counter

    # **Log Turn 0 (Initial State)**
    display_current_turn(0, "None")  # No agent has taken a turn yet
    display_board(
        env.buildings,
        env.grid,  # grid_scores
        env.builders,
        env.agents,  # agents list
    )
    display_player_stats(players)

    # Game loop using agent_iter
    for agent in env.agent_iter():
        observation, reward, termination, truncation, info = env.last()

        # Update player's scores based on the reward
        player = players.get(agent, None)
        if player:
            player.update_state(reward, info)

        if termination or truncation:
            # No action required
            action = None  # Pass or None
        else:
            # Player selects an action based on their strategy
            action = player.select_action(observation)
            if action is None:
                action = 0  # Fallback to a valid default action

        # Environment processes the action
        env.step(action)

        # Increment move counter
        move_count += 1

        # Calculate final environment score
        env_score = env.calculate_environment_score()

        # Calculate final scores for each player
        for player in players.values():
            player.final_score = 0.5 * player.self_score + 0.5 * env_score

        # Visualize the game state after each action
        current_turn = move_count
        current_agent = env.agent_selection
        display_current_turn(current_turn, current_agent)
        # Pass necessary parameters to display_board
        display_board(
            env.buildings,
            env.grid,  # grid_scores
            env.builders,
            env.agents,  # agents list
        )
        display_player_stats(players)

        # Forcefully end the game after max_moves moves
        if move_count >= max_moves:
            print(f"Game forcefully ended after {max_moves} moves.")
            break

    # Final results
    print("Game Over")

    display_player_stats(players)
    print(f"Global Environment Score: {env_score}\n")
    # Additional analysis or summary


if __name__ == "__main__":
    main()
