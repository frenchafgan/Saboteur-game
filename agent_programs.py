from une_ai.models.MCTS_graph_node import MCTSGraphNode
import MCTS_functions
import time
from saboteur_base_environment import SaboteurBaseEnvironment
from game_board import GameBoard

def mcts_agent_program(percepts, actuators, time_limit=100):
    """
    This function is an implementation of the Monte Carlo Tree Search (MCTS) algorithm for the Saboteur game.
    It takes in the game state from percepts, creates a root node for the MCTS graph, and runs the MCTS algorithm
    to find the optimal move for the current player within the given time limit.
    
    Args:
    - percepts: a dictionary containing the current game state, including the game board and the turn-taking indicator.
    - actuators: a dictionary containing the available actions for the agent to take.
    - time_limit: an integer representing the maximum time (in seconds) that the MCTS algorithm is allowed to run.
    
    Returns:
    - A list containing the optimal move for the current player, if one is found within the time limit. Otherwise, an
    empty list is returned.
    """
    # Extract game state from percepts

    board = percepts['game-board']
    turn = percepts['turn-taking-indicator'] 
    
    game_data = {
        'game-board': board,
        'player-turn': turn
    }
    
    optimal_move = None 
    
    if not SaboteurBaseEnvironment.is_terminal(game_data['game-board']):
        root = MCTSGraphNode(game_data, None, None)
        # Original line
        optimal_move = MCTS_functions.new_mcts(root, turn, time_limit)
        optimal_move = None 
        # optimal_move = MCTS_functions.new_mcts(root, turn, time_limit)
        
        
        # elapsed_time = time.time() - start_time  # Calculate elapsed time
        # print(f"Debug: MCTS completed in {elapsed_time:.2f} seconds.")
        if optimal_move:
            return [optimal_move]
            
        # else:
        #     print("Debug: No optimal move found.")
        #     # Here you can return a fail-safe action, if you have one
    return []  # Return an empty list if no action is chosen


