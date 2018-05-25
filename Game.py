import random


# This class takes care of the game state of the Catan game 
class Game():

    def __init__(self, board, deck, players):
        self.board = board
        self.deck = deck
        self.num_players = len(players)
        self.won = None
        self.players = players
        self.num_rounds = 0


    # This function represents the start of the game in which
    # each player chooses their spots. 
    def place_spots(self):

        # Place first settlement/road
        for player in self.players:
            print('For player ', player.player_name)
            player.choose_spot(self.board, 1)

        # for i in range(1,12):
        #     if i != 7:
        #         self.board.allocate_resources(i+1, self.players)

        # Place second settlement/road
        for player in self.players[::-1]:
            print('For player ', player.player_name)
            player.choose_spot(self.board, 2)



    # This function represents a round in which each player 
    # has one turn.
    def round(self):

        for player in self.players:
            print('Player ', player.player_name)

            # TODO: allow player to play dev card before rolling 

            dice1 = random.randint(1, 6)
            dice2 = random.randint(1, 6)
            print('Die rolled:', dice1 + dice2)
            self.board.allocate_resources(dice1 + dice2, self.players)
            
            # If the player has won, the game is over.
            if player.make_turn(self.board, self.deck):
                self.won = player
                return 1

        self.num_rounds += 1
        return 0


    # This function is called from the main method and is used to 
    # play the game. The function calls the round function until 
    # a player has won. 
    def play_game(self):

        while True:
            if self.round():
                return self.won





