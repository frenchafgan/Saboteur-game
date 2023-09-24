from une_ai.models import MCTSGraphNode, Agent
from card import PathCard, ActionCard
import random
import math

class MCTSAgent(Agent):
    """
    This class represents an agent that uses Monte Carlo Tree Search (MCTS) algorithm to play the Saboteur game.
    """

    def __init__(self, role, agent_program, num_simulations=1000, ucb1_const=2):
        """
        Initializes the MCTSAgent object.

        Args:
        - role (str): The role of the agent in the game.
        - agent_program (function): The program that the agent uses to select actions.
        - num_simulations (int): The number of simulations to run during each turn.
        - ucb1_const (float): The exploration constant used in the UCB1 formula.

        Returns:
        - None
        """
        super().__init__(role, agent_program)
        self.root = None
        self.num_simulations = num_simulations
        self.ucb1_const = ucb1_const
        self.add_all_sensors()
        self.add_all_actuators()
        self.add_all_actions()
        self._percepts = None
        self.role = role
        self._players = []
        for i in range(0, len(self._players)):
                self.current_player = self._players[i]        
        self.hand = []
        self._sensors = {
            'role-sensor': {'value': role},
            'hand-sensor': {'value': []},  # Initialize hand-sensor here
            'sabotaged': {'value': False},
            'game-board-sensor': {'value': None},
            'turn-taking-indicator': {'value': None}
        }
        

    def ucb1(self, parent_node):
        """
        Calculates the UCB1 value for a given node.

        Args:
        - parent_node (MCTSGraphNode): The parent node of the node for which the UCB1 value is to be calculated.

        Returns:
        - The child node with the highest UCB1 value.
        """
        parent_visits = parent_node.n()
        return max(
            parent_node.get_successors(),
            key=lambda child_node: (child_node.wins(self.role) / child_node.n()) +
                                    math.sqrt(self.ucb1_const * math.log(parent_visits) / child_node.n()),
        )
    
    def get_action_list(self, current_player, saboteur_env):
        """
        Returns a list of actions that the agent can take in the current state of the game.

        Args:
        - current_player (Player): The current player in the game.
        - saboteur_env (SaboteurEnv): The environment of the game.

        Returns:
        - A list of actions that the agent can take in the current state of the game.
        """
        self.root = MCTSGraphNode(saboteur_env, None, None)

        for _ in range(self.num_simulations):
            current_node = self.root
            current_env = saboteur_env.copy()

            while not current_node.is_leaf_node():
                current_node = self.ucb1(current_node)
                current_env.apply_action(current_player, current_node.get_action())

            available_actions = current_env.get_available_actions(current_player)
            if not available_actions:
                print("Debug: No available actions.")
                return None  # No available actions, return None

            for action in available_actions:
                new_env = current_env.copy()
                game_state = current_env.get_game_state()
                player = current_player._sensors
                new_env.apply_action(game_state, player, action)
                current_node.add_successor(new_env, action)

           
            child_node = random.choice(current_node.get_successors())
            while not current_env.is_terminal():
                available_actions = current_env.get_available_actions(current_player)
                if not available_actions:
                    print("Debug: No available actions during rollout.")
                    break  # Break out of the loop if no available actions

                action = random.choice(available_actions)
                current_env.apply_action(current_player, action)

            # Backpropagation
            winner = current_env.get_winner()
            child_node.backpropagate(winner)

        best_child = self.ucb1(self.root)
        if best_child:
            return best_child.get_action()
        else:
            print("Debug: No best child found.")
            return None
        

    
    def get_name(self):
        """
        Returns the name of the agent.

        Args:
        - None

        Returns:
        - The name of the agent.
        """
        return "MCTS Agent"
    
    def add_all_actions(self):
        """
        Adds all the actions that the agent can take in the game.

        Args:
        - None

        Returns:
        - None
        """
        return super().add_all_actions()
    
    def add_all_sensors(self):
        """
        Adds all the sensors that the agent can use in the game.

        Args:
        - None

        Returns:
        - None
        """
        return super().add_all_sensors()
    
    def add_all_actuators(self):
        """
        Adds all the actuators that the agent can use in the game.

        Args:
        - None

        Returns:
        - None
        """
        return super().add_all_actuators()
    
