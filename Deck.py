import random

# This should represent the deck for dev cards. It should include the 
# correct number of each dev card and should have this as a stack data
# structure. There should be a function that allows a player to take 
# from the top of this stack.
class Deck():

    # TODO: complete the constructor
    def __init__(self):
        '''
        0 - Knight
        1 - Victory point
        2 - Road building
        3 - Monopoly
        4 - Year of plenty
        '''
        self.cards_left = 25
        self.stack = [0] * 14 + [1] * 5 + [2] * 2 + [3] * 2 + [4] * 2
        random.shuffle(self.stack)
    
    def get_card_name(card):
        '''
        returns the name of the card id given
        '''
        return {0 : 'Knight', 1 : 'Victory Point',\
            2 : 'Road Building', 3 : 'Monopoly', 4 : 'Year of Plenty'}[card]


    # TODO: write a function that initializes a stack of cards. 
    def initialize_stack(self):
        self.cards_left = 25
        self.stack = [0] * 14 + [1] * 5 + [2] * 2 + [3] * 2 + [4] * 2
        random.shuffle(self.stack)


    # TODO: write a function that allows a player to pull a dev
    # card from the deck and updates the player's hand of dev cards.
    def take_card(self, player):
        if cards_left > 0:
            self.cards_left -= 1
            return self.stack[self.cards_left]
        return -1