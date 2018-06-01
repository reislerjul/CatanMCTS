from Main import run_game
import json
import random
import sys
import copy
from Player import Player
'''i think that with each game, we should record which player won, the types of each player, the victory points of each player, and the total rounds per game'''

if __name__ == "__main__":
    # We will assume that the commandline arguments give the players in the 
    # order that they should play
    assert(len(sys.argv) == 6 or len(sys.argv) == 7), "Incorrect number of args! first arg is number of games second through 5th is player types"
    n_games = sys.argv[1]
    # Process the commandline arguments. There should be 3 or 4 commandline
    # line arguments corresponding to each player. 0 means human player, 
    # 1 means random AI, 2 means MCTS AI.
    args = sys.argv[2:]
    results = []
    with open('output.txt', 'w') as f:
        for i in range(int(n_games)):
            # have the game do a random permutation of the order of players
            random.shuffle(args)
            vals = copy.deepcopy(args)
            player_list = []
            for idx, arg in enumerate(args):
                player_list.append(Player(int(arg), int(idx + 1)))
            winner, rounds, vps = run_game(player_list)
            result = (winner, rounds, vals, vps)
            f.write(json.dumps(result) + '\n')
    