import random
import settings


# This class takes care of the game state of the Catan game 
class Game():

    def __init__(self, board, deck, players, verbose=True):
        self.board = board
        self.deck = deck
        self.num_players = len(players)
        self.won = None
        self.players = players
        self.num_rounds = 0
        self.verbose = verbose

    # This function represents the start of the game in which
    # each player chooses their spots. 
    def place_spots(self, mode='beginner'):
        if mode == 'beginner':
            a = [0,1,2,3]
            random.shuffle(a)
            for i, player in enumerate(self.players):
                player.choose_spot2(self.board, a[i])
        else:
            # Place first settlement/road
            for player in self.players:
                if settings.DEBUG:
                    print("Choose first settlement for player " + str(player.player_num))
                player.choose_spot(self.board, 1)
    
            # Place second settlement/road
            for player in self.players[::-1]:
                if settings.DEBUG:
                    print("Choose second settlement for player " + str(player.player_num))
                player.choose_spot(self.board, 2)
    


    # This function represents a round in which each player 
    # has one turn.
    def round(self):
        # print the board state at the beginning of the round
        if self.verbose:
            print(self.num_rounds)

        if settings.DEBUG:
            self.board.print_board_state()

        self.board.round_num = self.num_rounds
        if self.num_rounds == 0:
            for player in self.players:
                self.board.active_player = player
                player.make_turn(self.board, self.deck, self.players)

        elif self.num_rounds == 1:
            for player in self.players[::-1]:
                self.board.active_player = player
                player.make_turn(self.board, self.deck, self.players)
        else:
            for player in self.players:
                self.board.active_player = player
                
                # If the player has won, the game is over.
                if player.make_turn(self.board, self.deck, self.players):
                    self.won = player
                    return 1

                # Player's state after their turn
                if settings.DEBUG:
                    print("State of player after turn:")
                    player.printResources()


        # print the board state at the end of the round
        if settings.DEBUG:
            self.board.print_board_state()

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