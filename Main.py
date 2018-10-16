#!/usr/bin/python3

import sys
from Player import Player
from Board import Board
from Deck import Deck
from Game import Game
import settings


# This will contain the main method which will be the entry point into
# playing the Catan game.
def run_game(player_list):
    # Create the game, board, deck, and settings
    settings.init()
    deck = Deck()
    deck.initialize_stack()
    board = Board(player_list)
    board.init_board()
    game = Game(board, deck, player_list)

    # Play the game
    print("Starting Game.")
    game.place_spots()
    winner = game.play_game()
    print("Total Rounds: " + str(game.num_rounds))
    print("Game Over. Player " + str(winner) + " won.")
    vp_lst = []
    for player in player_list:
        vp_lst.append(player.calculate_vp())
    return(winner, game.num_rounds, vp_lst)




if __name__ == '__main__':
    # We will assume that the commandline arguments give the players in the
    # order that they should play
    player_list = []

    # Process the commandline arguments. There should be 3 or 4 commandline
    # line arguments corresponding to each player. 0 means human player,
    # 1 means random AI, 2 means MCTS AI.
    args = sys.argv[1:]
    assert(len(args) == 3 or len(args) == 4), "Incorrect number of players!"

    for idx, arg in enumerate(args):

        player_type = int(arg)

        if player_type == Player.HUMAN:
            player_list.append(Human(int(idx + 1)))

        else if player_type == Player.Random_AI:
            player_list.append(RandomPlayer(int(idx + 1)))

        else if player_type == Player.MCTS_AI:
            time = int(input("Time parameter for MCTS?"))
            max_moves = int(input("Maximum moves parameter for MCTS?"))
            weighted = int(input("Weighted parameter for MCTS? (0 or 1)"))
            thompson = int(input("Thompson sampling for MCTS? (0 or 1)"))
            player_list.append(MCTSPlayer(int(idx + 1), time, max_moves, weighted, thompson))

    run_game(player_list)
