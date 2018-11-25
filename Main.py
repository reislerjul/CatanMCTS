#!/usr/bin/python3

import sys
from Player import Player
from Board import Board
from Deck import Deck
from Game import Game
from RandomPlayer import RandomPlayer
from MCTSPlayer import MCTSPlayer
from Human import Human
import settings
import json
import random


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

    # The parameters should be specified in a json file. The file will contain 
    # the players/types of players, the number of simulations to run, and a 
    # flag to indicate whether we should shuffle the order of play
    filename = "catan_input.json"
    index = 1
    with open(filename) as f:
        data = json.load(f)

    for player in data["players"]:
        if player["type"] == "human":
            player_list.append(Human(index))
        if player["type"] == "random":
            player_list.append(RandomPlayer(index))
        if player["type"] == "MCTS":
            player_list.append(MCTSPlayer(index, int(player["time"]), \
                int(player["max_moves"]), int(player["weighted"]), int(player["thompson"])))
        index += 1

    num_games = int(data["num_games"])
    shuffle = int(data["shuffle_order"])
    for i in range(num_games):
        if shuffle:
            random.shuffle(player_list)
        run_game(player_list)
        print(player_list)
