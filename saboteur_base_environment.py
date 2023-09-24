from une_ai.models.game_environment import GameEnvironment
from card import PathCard, ActionCard, GoalCard
from SaboteurPlayer import SaboteurPlayer
from game_board import GameBoard
from deck import Deck

from copy import deepcopy
import random


class SaboteurBaseEnvironment(GameEnvironment):
    """
    This class represents the base environment for the Saboteur game. It inherits from the GameEnvironment class.
    It initializes the game board and deck, creates a pool of roles and randomly selects 8 roles from the pool.
    It also initializes players, distributes cards and sets initial game state.
    It has methods to draw a card, get legal actions, check if the game is terminal and transition to a new game state.
    """
    def __init__(self, num_players=8):  # Number of players is always 8
        from agent_programs import mcts_agent_program
        # sys.setrecursionlimit(10000)

       # Initialize game board and deck
        self._board = GameBoard()
        self.deck = Deck()
        self.discard_pile = []      

        # Get the grid map from the game board
        self.board = GameBoard.get_grid_map(self)
        
        # Create a pool of roles and randomly select 8 roles from the pool
        role_pool = ['Gold-Digger'] * 6 + ['Saboteur'] * 3
        num_players = 8

        selected_roles = random.sample(role_pool, num_players)

        # Initialize players
        self.players = []
        self.current_player_index = 0

        for index, role in enumerate(selected_roles):
            # mcts_agent_instance = MCTSAgent(role, mcts_agent_program, num_simulations=1000, ucb1_const=2)
            player_instance = SaboteurPlayer(f'Player {index + 1}', mcts_agent_program, role)
            # Distribute cards and set initial game state
         # Distribute cards and set initial game state
            for giveCard in range(0, 4):
                self.draw_card(player_instance)
            self.players.append(player_instance)
        
        self.rounds = 0
        self.scores = {}
        # player._sensors['hand-sensor']['value'].append(new_card)    
        
        self._sensors = {
            'game-board-sensor' : { 'value':[] }, 
            'role-sensor' : { 'value':[] }, 
            'turn-taking-indicator' : { 'value':[] }, 
            'hand-sensor' : { 'value':[] }, 
        }
        
        self._actuators = {
            'path-card-handler' : { 'value':[] }, 
            'action-card-handler' : { 'value':[] }, 
            'pass-turn-handler' : { 'value':[] }, 
        }
        
        # Initialize the current player and update sensors
        self.current_player = self.players[self.current_player_index]
        

    def draw_card(self, player):
        """
        This method takes a player object and draws a card from the deck.
        It adds the card to the player's hand and also updates the hand-sensor value.
        """
        # print(f"Type of player object: {type(player)}")
        # print(f"Value of player object: {player}")
        # Safety Check: If 'hand-sensor' doesn't exist, create it
        if 'hand-sensor' not in player._sensors:
            player._sensors['hand-sensor'] = {'type': 'list', 'value': []}
            
        if not self.deck.is_empty():
            new_card = self.deck.draw()
            player.hand.append(new_card)
            #add card to hand-sensor value also
            player._sensors['hand-sensor']['value'].append(new_card)    
    
 
        
    
    def get_legal_actions(self, current_player):
        """
        This method takes the current player object and returns a dictionary of valid card placements.
        It checks if the card is a PathCard and its _exits are not [0, 0, 0, 0].
        It then checks if the card can be placed on the game board and adds it to the dictionary if it can.
        It also rotates the card and checks if it can be placed in the new orientation and adds it to the dictionary if it can.
        """
        # print("Debug: Checking if conditions are met.")
        
        validCardPlacements = {}

        for i in range(0, len(current_player.hand)): 
                card = current_player.hand[i]
        
                # Check if it's a PathCard and its _exits are not [0, 0, 0, 0]
                if isinstance(card, PathCard) and card._exits != [0, 0, 0, 0]:
                    
                    for x in range(0, 20):
                        for y in range(0, 20):
                            if self._board.check_path_card(x, y, card):
                                if card not in validCardPlacements:
                                    validCardPlacements[card] = []
                                validCardPlacements[card].append((x, y, 0))
                            
                            # Rotate and do the same
                            card.turn_card()
                            if self._board.check_path_card(x, y, card):
                                if card not in validCardPlacements:
                                    validCardPlacements[card] = []
                                validCardPlacements[card].append((x, y, 1))
                            
                            # Rotate it back, so we know that position 0 is this position
                            card.turn_card()
                
        return validCardPlacements
   
    def is_terminal(self):
        """
        This method checks if the game is terminal.
        It checks if all players have no cards in their hands, if the gold goal card is revealed or if the deck is empty.
        """
        #check to see if players have cards in their hands
        if all(len(player.hand) == 0 for player in self.players):
            return True
       
        # Check if the gold goal card is revealed
        for x, y in [(14, 8), (14, 10), (14, 12)]:
            card = self.board.get_item_value(x, y)
            if card._special_card == 'gold' and card._revealed == True:
                return True

        # Check if the deck is empty
        if len([Deck.get_deck]) == 0:
            return True
        return False
    

    #TODO: Improve this function
    def transition_result(current_state, action):
            """
            Takes the current game state and an action, and returns the new game state after applying the action.
            """
            # Make a deep copy of the current state to avoid modifying it directly
            new_state = deepcopy(current_state)

            # Extract relevant information from the current state
            board = new_state.board
            deck = new_state.deck
            rounds = new_state.rounds
            scores = new_state.scores
            current_player_index = new_state.current_player_index
            players = new_state.players

            # Validate that all necessary keys exist
            if board is None or deck is None or rounds is None or scores is None:
                # raise Exception("Missing current_player_index or players in game_state")
                pass

            # Apply the action to update the game state
            action_type = []
             
            if action_type == 'place_card':
                x, y = action[1], action[2]
                card_to_place = deck.pop()  # Assuming the top card in the deck is the one to be placed
                board[x][y] = card_to_place  # Place the card on the board

            elif action_type == 'draw_card':
                # Draw a card from the deck and give it to the current player
                drawn_card = deck.pop()
                players[current_player_index]['hand'].append(drawn_card)

            # Update other state variables as necessary
            rounds += 1
            current_player_index = (current_player_index + 1)

            # Update the new_state dictionary
            new_state._sensors['game-board-sensor']['value'] = board
            new_state.deck = deck
            new_state.rounds = rounds
            new_state.scores = scores  # Update if necessary
            new_state.current_player_index = current_player_index
            new_state.players = players

            return new_state   
    
    def get_game_state(self):
        # Construct the game_state dictionary
        game_state = {
            'game-board': self._board,
            'deck': self.deck,
            'rounds': self.rounds,
            'scores': self.scores,
            # 'current_player_index': self.current_player_index,  # Added this line to include current_player_index in game_state
            'current_player_index': self.current_player_index,           
            'player-turn': self.players[self.current_player_index]._agent_name,
            'hand-sensor': self.players[self.current_player_index]._sensors['hand-sensor'],
        }
        return game_state
    
    def get_percepts(self):
        game_state = self.get_game_state()
        return {
            'game-board-sensor' : game_state['game-board'], 
            'turn-taking-indicator': game_state['player-turn'],
            'hand-sensor': game_state['hand-sensor']
            
        }
    
    def get_player_state(self, player):
        # Initialize an empty list to hold player information
        player_info = []
        
        # Loop through each player in self._players to collect their information
        for player in self.players:
            player_sensors = {
                'name': player._agent_name,
                'role': player.role,
                'hand': player.hand,
                'agent': player._agent_program,
                'sabotaged': player.sabotaged,
                'score': self.scores[player]
            }
        player_info.append(player_sensors)
        
        return player_info        
    
    @staticmethod
    def turn(game_state):
        return game_state['players'][game_state['current_player_index']].name
    
    @staticmethod
    def payoff(game_state, player_name):
        player = next(player for player in game_state['players'] if player.name == player_name)
        if player.role == 'Gold-Digger' and game_state['game_board'].gold_found():
            return 1  # Gold-Diggers win when gold is found
        elif player.role == 'Saboteur' and not game_state['game_board'].gold_found():
            return 1  # Saboteurs win when gold is not found
        else:
            return 0  # Otherwise, this player did not achieve their objective
                    
    #TODO : Implement this function
    def state_transition(self):
       pass
    

    # def pass_turn(self, player):
    #     print(f"{player} passed their turn.")

    # def copy(self):
    #     # Create a new environment object
    #     new_env = SaboteurBaseEnvironment()
        
    #     # Deep copy the game board and deck
    #     new_env.game_board = deepcopy(self._board)
    #     new_env.deck = deepcopy(self.deck)
        
    #     # Deep copy players if they have a copy method, otherwise just reference them
    #     new_env.players = [player.copy() if hasattr(player, "copy") else deepcopy(player) for player in self._players]
        
    #     # Copy other attributes
    #     new_env.current_player_index = self.current_player_index
    #     new_env.rounds = self.rounds
    #     new_env.scores = deepcopy(self.scores)
        
    #     return new_env

    # def apply_action(self, game_state, player, agent, action):
    #     # print(f"Debug: Inside apply_action with action = {action}")
    #     card_to_discard = self.choose_card_to_discard(game_state, player)

    #     if action == 'place-path-card':
    #         if not self.place_path_card(agent, player):
    #             GameBoard.handle_invalid_placement(player, game_state)
    #         else:
    #             self.discard_card(player, card_to_discard)
    #             self.draw_card(player)
                    
    #     elif action == 'use-action-card':
    #         if not self.use_action_card(player, game_state):
    #             GameBoard.handle_invalid_placement(player, game_state)
    #         else:
    #             self.discard_card(player)
    #             self.draw_card(player)
                    
    #     elif action == 'pass-turn':
    #         card_to_discard = self.choose_card_to_discard(game_state, player)
    #         self.pass_turn(player)
    #         self.discard_card(player)
    #         self.draw_card(player)
                
    #     else:
    #         print("Invalid action.")

    # def calculate_card_value(self, card, role, game_board_state):
    #     print ("Debug: Inside calculate_card_value with card = ", card, "role = ", role, "game_board_state = ", game_board_state)
    #     if role == 'Gold-Digger':
    #         if isinstance(card, PathCard):
    #             # Heuristic: A PathCard is more valuable if it extends a path towards the goal
    #             return self.evaluate_path_extension(card, game_board_state)
    #         elif isinstance(card, ActionCard):
    #             # Heuristic: An ActionCard might be valuable based on its action type
    #             return self.evaluate_action_card_for_gold_digger(card)
    #     elif role == 'Saboteur':
    #         if isinstance(card, PathCard):
    #             # Heuristic: A PathCard is valuable if it blocks a path towards the goal
    #             return self.evaluate_path_blockage(card, game_board_state)
    #         elif isinstance(card, ActionCard):
    #             # Heuristic: An ActionCard might be valuable based on its action type
    #             return self.evaluate_action_card_for_saboteur(card)
    #     return 0  # Default case or for unknown card types
    
    
    
    def discard_card(self, player, card_to_discard):
        # print ("Debug: Inside discard_card with card_to_discard = ", card_to_discard)
        # print("Player's hand before removal:", self._sensors['hand-sensor']['value'])
        # print("Card to discard:", card_to_discard)
        #print gameboard to see what cards are in the players hand
        # print("Gameboard:", self.game_board)
        
        if card_to_discard in player.hand:
            player.hand.remove(card_to_discard)
        else:
            print("Card not found in player's hand.")
     
    def get_next_player(self):
        current_player_index = self.players.index(self.current_player)
        next_player_index = (current_player_index + 1) 
        next_player_index = next_player_index % 8

        self.current_player = self.players[next_player_index]
           

    def get_winner(self):
        for card in self._board._goal_cards:
            if card._special_card == 'gold' and card._revealed == True:
                return 'Gold-Digger'
            
        return "Saboteur"

    # def choose_goal_card(self, game_board):
    #     goal_positions = [(14, 8), (14, 10), (14, 12)] 
    #     chosen_goal_position = random.choice(goal_positions)
    #     return chosen_goal_position

    # def choose_path_card_to_remove(self, game_board):
    #     # print ("Debug: Inside choose_path_card_to_remove with game_board = ", game_board)
    #     # Randomly choose a path card to remove (excluding special cards)
    #     x, y = random.randint(0, 19), random.randint(0, 19)
    #     while game_board.get_grid_map().get_item_value(x, y) is None or game_board.get_grid_map().get_item_value(x, y).is_special_card():
    #         x, y = random.randint(0, 19), random.randint(0, 19)
    #     return (x, y)
        
    # def choose_target_player(self):
    #     # Assuming you have a list of players, randomly choose one to be the target
    #     target_player = random.choice(self.players)
    #     return target_player
    
        
    def add_player(self, player):
        self.players.append(player)
        self.scores[player] = 0





