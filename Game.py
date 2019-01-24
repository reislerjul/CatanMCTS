import random
import settings


# This class takes care of the game state of the Catan game 
class Game():

    def __init__(self, board, deck, players, start_player=0, trading=False, verbose=True):
        self.board = board
        self.deck = deck
        self.num_players = len(players)
        self.won = None
        self.players = players
        self.num_rounds = 0
        self.verbose = verbose

        # Only used when a game is created from MCTS algorithm. In MCTS algorithm, 
        # the game may start from the middle of the round, so we don't want the 
        # game to always start with the first player
        self.start_player = start_player

    # This function represents a round in which each player 
    # has one turn.
    def round(self):
        # print the board state at the beginning of the round
        if self.verbose:
            print("****" + str(self.num_rounds) + "****") 

        '''
        if settings.DEBUG:
            self.board.print_board_state()
        '''

        self.board.round_num = self.num_rounds
        if self.num_rounds == 0:
            for i in range(self.start_player, len(self.players)):
                player = self.players[i]
                self.board.active_player = player
                player.make_turn(self.board, self.deck, self.players)

        elif self.num_rounds == 1:
            for i in range(1, len(self.players) + 1):
                player = self.players[len(self.players) - i]
                self.board.active_player = player
                player.make_turn(self.board, self.deck, self.players)
        else:
            for i in range(self.start_player, len(self.players)):
                player = self.players[i]
                self.board.active_player = player
                
                # If the player has won, the game is over.
                if player.make_turn(self.board, self.deck, self.players):
                    self.won = player
                    return 1

                '''
                # Player's state after their turn
                if settings.DEBUG:
                    print("State of player after turn:")
                    player.printResources()
                '''

        # We should only start in the middle of a round once when the MCTS algorithm calls the game
        self.start_player = 0

        '''
        # print the board state at the end of the round
        if settings.DEBUG:
            self.board.print_board_state()
        '''

        self.num_rounds += 1
        return 0


    # This function is called from the main method and is used to 
    # play the game. The function calls the round function until 
    # a player has won. 
    def play_game(self):        
        while True:
            if self.round():
                return self.won

            # The other win condition will occur when 500 turns are played. 
            # Take the player with the highest number of points.
            if self.num_rounds == 500:
                self.won = self.players[0]
                max_points = self.players[0].calculate_vp()
                for player in self.players[1:]:
                    curr_vp = player.calculate_vp()
                    if curr_vp > max_points:
                        max_points = curr_vp
                        self.won = player
                return self.won