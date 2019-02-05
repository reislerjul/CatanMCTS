import random
import settings


# This class takes care of the game state of the Catan game 
class Game():

    def __init__(self, board, deck, players, verbose=True):
        self.board = board
        self.deck = deck
        self.num_players = len(players)
        self.players = players
        self.verbose = verbose

    # This function is called from the main method and is used to 
    # play the game. The function calls the round function until 
    # a player has won. 
    def play_game(self): 
        if self.verbose:
            print("*** ROUND 0 ***")     
            print("_____PLAYER 1 TURN_____")  
        self.board.verbose = self.verbose
        while True:
            move = self.board.active_player.decide_move(self.board, self.deck, self.players)
            if not isinstance(move, int):
                self.board.active_player.make_move(move, self.board, self.deck, self.players)
                if self.board.active_player.calculate_vp() >= settings.POINTS_TO_WIN:
                    return self.board.active_player

            # The other win condition will occur when 500 turns are played. 
            # Take the player with the highest number of points.
            if self.board.round_num >= 500:
                winner = self.players[0]
                max_points = self.players[0].calculate_vp()
                for player in self.players[1:]:
                    curr_vp = player.calculate_vp()
                    if curr_vp > max_points:
                        max_points = curr_vp
                        winner = player
                return winner