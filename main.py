# main.py

import logging
from environment import SimCityEnv
from players import BalancedPlayer
from log import display_current_turn, display_board, display_player_stats


def main():
    players = {
        "P1": BalancedPlayer("P1"),
        "P2": BalancedPlayer("P2"),
        "P3": BalancedPlayer("P3"),
    }

    env = SimCityEnv()

    env.players = players

    env.run_game()

    print("Game Over!")


if __name__ == "__main__":
    main()
