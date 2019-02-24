import random
import settings

# This class takes care of the game state of the Catan game 
class Game():

    def __init__(self, board, deck, players, round_threshold, verbose=True, nn=None):
        self.board = board
        self.deck = deck
        self.num_players = len(players)
        self.players = players
        self.verbose = verbose
        self.round_threshold = round_threshold
        self.nn = nn

    # This function is called from the main method and is used to 
    # play the game. The function calls the round function until 
    # a player has won. 
    def play_game(self): 
        if self.verbose:
            print("*** ROUND 0 ***")     
            print("_____PLAYER 1 TURN_____")  
        self.board.verbose = self.verbose
        while True:
            move = self.board.active_player.decide_move(self.board, self.deck, self.players, self.nn)
            self.board.active_player.make_move(move, self.board, self.deck, self.players)
            if self.board.active_player.calculate_vp() >= settings.POINTS_TO_WIN:
                return self.board.active_player

            # The other win condition will occur when round_threshold turns are played. 
            # Take the player with the highest number of points.
            if self.board.round_num >= self.round_threshold:
                return max([(player, player.calculate_vp()) for player in self.players], 
                    key=lambda x: x[1])[0]