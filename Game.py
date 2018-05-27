import random
import settings


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

        if settings.DEBUG:
            self.board.print_board_state()

        for player in self.players:
            # TODO: allow player to play dev card before rolling 

            dice1 = random.randint(1, 6)
            dice2 = random.randint(1, 6)

            # Player's state before their turn
            if settings.DEBUG:
                print("Player " + str(player.player_num) + "\'s turn.")
                print("State of player before turn:")
                player.printResources()
                print("Dice Roll: " + str(dice1 + dice2))

            self.board.allocate_resources(dice1 + dice2, self.players)

            # If the roll is 7, the player should move the robber and steal
            if dice1 + dice2 == 7:
                player.moveRobber(self.board)

            
            # If the player has won, the game is over.
            if player.make_turn(self.board, self.deck):
                self.won = player.player_num
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







