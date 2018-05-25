import sys
from Player import Player
from Board import Board
from Deck import Deck
from Game import Game

# This will contain the main method which will be the entry point into 
# playing the Catan game.
def main():

    # We will assume that the commandline arguments give the players in the 
    # order that they should play
    player_list = []

    # Process the commandline arguments. There should be 3 or 4 commandline
    # line arguments corresponding to each player. 0 means human player, 
    # 1 means random AI, 2 means MCTS AI.
    args = sys.argv[1:]
    assert(len(args) == 3 or len(args) == 4), "Incorrect number of players!"

    for idx, arg in enumerate(args):
    	player_list.append(Player(int(arg), str(idx+1)))

    # Create the game, board, and deck
    deck = Deck()
    deck.initialize_stack()
    board = Board(player_list)
    board.init_board()
    game = Game(board, deck, player_list)

    # Play the game
    print("Starting Game.")
    game.place_spots()
    winner = game.play_game()
    print("Game Over.")


if __name__ == '__main__':
    main()
