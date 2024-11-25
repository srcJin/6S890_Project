# log.py

import logging
import os

# Setup logging
LOG_FILE = "game_log.txt"

# Clear the log file at the start of the run
if os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w") as f:
        f.truncate(0)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    filemode="a",  # Append mode
    datefmt="%Y-%m-%d %H:%M:%S",
)


def display_current_turn(turn, agent_name):
    logging.info(f"Current Turn: {turn}, Agent: {agent_name}")


def display_board(buildings, grid_scores, builders, agents):
    """
    Logs the detailed board state with uniform formatting.

    Parameters:
    - buildings (np.array): Grid of building types.
    - grid_scores (np.array): Grid of G, V, D scores.
    - builders (np.array): Grid of builder indices.
    - agents (list): List of agent names.
    """
    log_message = "Current Board State:\n"
    cell_width = 24  # Fixed width for each cell
    separator = ", "  # Separator between cells

    for x in range(buildings.shape[0]):
        row_cells = []
        for y in range(buildings.shape[1]):
            building = buildings[x][y]
            G, V, D = grid_scores[x][y]
            builder_idx = builders[x][y]
            if building is None:
                cell_content = f"[X|G:{G}|V:{V}|D:{D}|B:NA]"
            else:
                builder_name = agents[builder_idx] if builder_idx != -1 else "None"
                # Truncate builder name if it's too long
                builder_name = (
                    builder_name[:4] if len(builder_name) > 4 else builder_name
                )
                cell_content = f"[{building[0]}|G:{G}|V:{V}|D:{D}|B:{builder_name}]"
            # Pad the cell content to ensure uniform width
            cell_str_padded = cell_content.ljust(cell_width)
            row_cells.append(cell_str_padded)
        # Join all cells in the row with the separator
        row_str = separator.join(row_cells)
        log_message += row_str + "\n"
    log_message += "\n"
    logging.info(log_message)


def display_player_stats(players):
    log_message = "Player Statistics:\n"
    for player in players.values():
        log_message += f"{player.name}:\n"
        log_message += f"  Self Score: {player.self_score}\n"
        log_message += f"  Final Score: {player.final_score}\n"
        # Include any additional stats
    log_message += "\n"
    logging.info(log_message)
