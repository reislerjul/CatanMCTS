# The player class. Each player should keep track of their roads, cities, 
# settlements, dev cards, whether they're on a port, number of victory
# points, and resource cards. 
class Player():


    # TODO: Complete this constructor. player_type should be 0 if the player is
    # human, 1 if the player is the random AI, and 2 if the player is the 
    # MCTS AI
    def __init__(self, player_type):
        self.resources = {}
        self.vp_dev_cards = 0
        self.player_type = player_type
        self.dev_cards = {}
        self.num_knights_played = 0
        self.longest_road = 0
        self.largest_army = 0
        self.ports = {}
        self.cities = {}
        self.settlements = {}


    # A getter function to return the player's hand of dev cards
    def get_dev_cards(self):
        return self.dev_cards

    # Allows the game to access the number of victory points that a player has
    def calculate_vp(self):
        return self.vp_dev_cards + len(self.cities.items()) + \
        len(self.settlements.items()) + self.longest_road + self.largest_army


    # TODO: implement a function that allows the players to choose their 
    # settlement and road placement at the beginning of the game
    def choose_spot(self):
        return


    # TODO: this function should check that the move made is a legal move. 
    # Consider making one of these for each move type. 
    # If it is not, the board should not be updated and the player should 
    # choose a different move. Return 1 if the move is legal and 0 
    # otherwise. A few things to check for: 
    # Roads: built next to another road or settlement belonging to player, 
    # does not overlap with already created road
    # Settlements: built next to road belonging to player, is at least 
    # 2 spaces away from any other settlement
    # Cities: Placed over settlement belonging to player, not placed over
    # another city
    # Drawing dev card: there is at least one dev card in the deck
    # Moving robber: robber is moved to a valid space
    # Playing dev card: card is not a victory point or an already used knight, 
    # a max of 1 dev card is used per turn, dev card is not used the turn its 
    # drawn 
    # Trading with bank: player has the required resources to make the trade
    # based on the ports that the player has
    # General: Make sure the player can only play the move if they have the 
    # required resources
    def check_legal_move(self, board):
        return 1


    # TODO: this should represent a single move within a turn. Return 
    # 0 if we are passing our turn, 1 if the move is a valid move, 
    # -1 if the move is not legal
    def make_move(self, move_type):

        # End turn
        if move_type == 0:
            return 0

        # Build a road
        elif move_type == 1:
            return 1

        # Build a settlement
        elif move_type == 2:
            return 1 

        # Build a city
        elif move_type == 3:
            return 1 

        # Draw a dev card
        elif move_type == 4:
            return 1 

        # Play a dev card 
        elif move_type == 5:
            return 1 

        # Trade with bank
        elif move_type == 6:
            return 1 

    
    # TODO: this function will be used to choose the move. it should 
    # be different depending on whether the player is a random AI, 
    # human, or MCTS AI
    def decide_move(self):
        return 0


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
    def make_turn(self, board):

        while True:
            move = self.decide_move()

            # We made a move that is not passing our turn
            if self.make_move(move) == 1:
                board.update_board()

                # Did the move cause us to win?
                if self.calculate_vp() >= 10:
                    return 1

            # TODO: change this to 0 when we atually have the game playable
            elif self.make_move(move) == 0:
                return 1
            

