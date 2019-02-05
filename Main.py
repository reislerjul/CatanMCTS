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
import csv
from utils import Card


# This will contain the main method which will be the entry point into
# playing the Catan game.
def run_game(player_list, random_board):
    # Create the game, board, deck, and settings
    settings.init()
    deck = Deck()
    board = Board(player_list, random_board)
    game = Game(board, deck, player_list)

    if settings.DEBUG:
        for element in board.resources.items():
            print("printing hexes")
            print(element)
        for coord in board.coords.items():
            if coord[1].ports != set():
                print("printing port coordinates")
                print(coord[0])
                print(coord[1].ports)

    # Play the game
    print("Starting Game.")
    #game.place_spots()
    winner = game.play_game()
    if player_list[0].player_type == Player.HUMAN:
        print("player 1 settlements: " + str(player_list[0].settlements))
        print("player 1 cities: " + str(player_list[0].cities))
        print("player 1 roads: " + str(player_list[0].roads))
        print("player 2 settlements: " + str(player_list[1].settlements))
        print("player 3 cities: " + str(player_list[1].cities))
        print("player 2 roads: " + str(player_list[1].roads))
        print("player 3 settlements: " + str(player_list[2].settlements))
        print("player 3 cities: " + str(player_list[2].cities))
        print("player 3 roads: " + str(player_list[2].roads))


    print("Total Rounds: " + str(board.round_num))
    print("Game Over. Player " + str(winner.player_num) + " won.")
    return(winner, board.round_num, board)


if __name__ == '__main__':
    # We will assume that the commandline arguments give the players in the
    # order that they should play
    player_list = []

    # The parameters should be specified in a json file. The file will contain 
    # the players/types of players, the number of simulations to run, a 
    # flag to indicate whether we should shuffle the order of play, and a 
    # flag to determine if we want to write to a csv file
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
            MCTS_player = MCTSPlayer(index, int(player["time"]), \
                int(player["weighted"]), int(player["thompson"]))
            player_list.append(MCTS_player)
        index += 1

    record_file = int(data["record_data"])
    if record_file:
        fields=['Winner Type','Winner Num','First Player Type', 
            'First Player VP', 'Second Player Type', 'Second Player VP',
            'Third Player Type', 'Third Player VP', 'Fourth Player Type', 
            'Fourth Player VP', 'Number Rounds', 'Largest Army Player', 
            'Largest Army Size', 'Longest Road Player', 'Longest Road Size', 
            'MCTS Num Ports', 'MCTS Num Cities', 'MCTS Num Settlements', 
            'MCTS Num Roads', 'MCTS Num Knights Played', 'MCTS Num YOP Played',
            'MCTS Num Monopoly Played', 'MCTS Num Road Builder Played', 
            'MCTS Num VP Dev Cards', 'MCTS Num Devs Bought', 
            'MCTS Total Trades Accepted', 'MCTS Total Trades Proposed', 
            'MCTS Trades Proposed Successfully', 'Total Trades with Bank', 
            'Average Move per Turn', 'Average Number of Moves Considered by MCTS Algorithm', 
            'Average Number of Cycles Run by MCTS Algorithm per Decided Move']

        with open(r'catan_results.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerow(fields)

    num_games = int(data["num_games"])
    shuffle = int(data["shuffle_order"])
    for i in range(num_games):
        MCTS_player = None
        if shuffle:
            random.shuffle(player_list)

        # We need to reset the players in the player list between rounds
        for j in range(len(player_list)):
            if player_list[j].player_type == Player.HUMAN:
                player_list[j] = Human(j + 1)
            elif player_list[j].player_type == Player.RANDOM_AI:
                player_list[j] = RandomPlayer(j + 1)
            elif player_list[j].player_type == Player.MCTS_AI:
                player_list[j] = MCTSPlayer(j + 1, player_list[j].time, \
                    player_list[j].weighted, player_list[j].thompson)
                MCTS_player = player_list[j]

        winner, num_rounds, board = run_game(player_list, bool(int(data["random_board"])))
        if record_file:
            row = []
            row.append(winner.to_string())
            row.append(winner.player_num)
            for player in player_list:
                row.append(player.to_string())
                row.append(player.calculate_vp())
            if len(player_list) == 3:
                row.append("")
                row.append("")
            row.append(num_rounds)
            if board.largest_army_player != None:
                row.append(board.largest_army_player.player_num)
                row.append(board.largest_army_size)
            else:
                row.append("")
                row.append("")
            if board.longest_road_player != None:
                row.append(board.longest_road_player.player_num)
                row.append(board.longest_road_size)
            else:
                row.append("")
                row.append("")
            if MCTS_player != None:
                row.append(len(MCTS_player.ports))
                row.append(len(MCTS_player.cities))
                row.append(len(MCTS_player.settlements))
                row.append(MCTS_player.total_roads)
                row.append(MCTS_player.num_knights_played)
                row.append(MCTS_player.num_yop_played)
                row.append(MCTS_player.num_monopoly_played)
                row.append(MCTS_player.num_road_builder_played)
                row.append(MCTS_player.dev_cards[Card.VICTORY_POINT])
                row.append(MCTS_player.devs_bought)
                row.append(MCTS_player.trades_accepted)
                row.append(MCTS_player.trades_proposed)
                row.append(MCTS_player.trades_proposed_successfully)
                row.append(MCTS_player.bank_trades)
                row.append(float(MCTS_player.avg_moves_round[1]) / MCTS_player.avg_moves_round[0])
                row.append(float(MCTS_player.avg_cycles_per_move[1]) / MCTS_player.avg_cycles_per_move[0])
                row.append(float(MCTS_player.avg_legal_moves[1]) / MCTS_player.avg_legal_moves[0])
            with open(r'catan_results.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerow(row)
