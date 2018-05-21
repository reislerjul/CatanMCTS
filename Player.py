# The player class. Each player should keep track of their roads, cities, 
# settlements, dev cards, whether they're on a port, number of victory
# points, and resource cards. 
class Player():


    # TODO: Complete this constructor. player_type should be 0 if the player is
    # human, 1 if the player is the random AI, and 2 if the player is the 
    # MCTS AI
    def __init__(self, player_type):
        self.resources = []
        self.vp = 2
        self.player_type = player_type
        self.dev_cards = []


    # A getter function to return the player's hand of dev cards
    def get_dev_cards(self):
        return self.dev_cards

    # Allows the game to access the number of victory points that a player has
    def get_vp(self):
        return self.vp


    # TODO: implement a function that allows the players to choose their 
    # settlement and road placement at the beginning of the game
    def choose_spot(self):
        return


    # TODO: 
    # function in which the player can have a turn. This should be handled
    # differently depending on whether the player is real or is an AI.
    # If the player is real, the make_move function should prompt the player
    # to enter moves from the command line, check if they are legal, and update
    # the board state if they are legal. The function returns when the player 
    # has entered a command to end their turn. For an AI, we should first code
    # a basis random AI. This AI will consider the set of legal moves that they
    # can make and choose one at random. This will occur until they randomly 
    # choose to end their turn. If a player makes a move that causes their 
    # victory points to be greater than or equal to 10, the function should 
    # immediately return 1. Otherwise, return 0 when the turn is over. 
    def make_turn(self):
        return 1
