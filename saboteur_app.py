import math
import random
from saboteur_base_environment import SaboteurBaseEnvironment

def main():
    """
    This function runs the main game loop for the Saboteur game. It initializes the environment, 
    gets the current player and available actions, chooses and validates the action, determines 
    the best action based on the role and distance to goal, applies the chosen action, and gets 
    the next player. It continues this loop until the game is over, at which point it prints the 
    winners of the game.
    """
    # Initialization
    env = SaboteurBaseEnvironment()

    # Main Game Loop
    while not env.is_terminal():
        # Get current player and available actions
        current_player = env.current_player

        # Choose and validate action
        available_actions = env.get_legal_actions(current_player)

        if available_actions:
            bestCard = None
            bestOption = []
            lastDistance = 100000000 if current_player.role == 'Gold-Digger' else 0

            # start empty
            goals = [ ]

            # get the 3 goal points
            goal1 = env.board.get_item_value(14,8)
            goal2 = env.board.get_item_value(14,10)
            goal3 = env.board.get_item_value(14,12)

            # we only add to the array any unrevealed cards, since if we've revealed and its Gold, then the game is finished anyways
            if goal1 is not None and goal1._special_card in ['gold', 'goal'] and goal1._revealed == False:
                goals.append([14,8])

            if goal2 is not None and goal2._special_card in ['gold', 'goal'] and goal2._revealed == False:
                goals.append([14,10])

            if goal3 is not None and goal3._special_card in ['gold', 'goal'] and goal3._revealed == False:
                goals.append([14,12])

            # Determine the best action based on the role and distance to goal
            for card in available_actions:
                for positions in available_actions[card]:
                    xy = [positions[0], positions[1]]

                    for goal in goals:
                        distance = math.dist(xy, goal)
                        if (current_player.role == 'Gold-Digger' and distance < lastDistance) or \
                           (current_player.role == 'Saboteur' and distance > lastDistance):
                            bestCard = card
                            bestOption = positions
                            lastDistance = distance

            # If there's no best card, select one at random
            if bestCard is None:
                chosen_card = random.choice(list(available_actions.keys()))
                chosen_action = available_actions[chosen_card]
                chosen_location = random.choice(list(chosen_action))
            else:
                chosen_card = bestCard
                chosen_location = bestOption

            # Apply the chosen action
            env.discard_card(current_player, chosen_card)
            if chosen_location[2] == 1:
                chosen_card.turn_card()
            env._board.add_path_card(x=chosen_location[0], y=chosen_location[1], path_card=chosen_card)
            env.board.draw_board()

        else:
            if len(current_player.hand) > 0:
                env.discard_card(current_player, current_player.hand[0])
            if not available_actions and not env.deck.is_empty():
                env.draw_card(current_player)

        env.get_next_player()

    winners = env.get_winner()
    print(f"Game Over. Winners: {winners}")

if __name__ == "__main__":
    main()



