import random

# This should represent the deck for dev cards. It should include the 
# correct number of each dev card and should have this as a stack data
# structure. There should be a function that allows a player to take 
# from the top of this stack.
class Deck():

    def __init__(self):
        '''
        0 - Knight
        1 - Victory point
        2 - Road building
        3 - Monopoly
        4 - Year of plenty
        '''
        self.cards_left = 20
        self.initialize_stack()
    
    def get_card_name(self, card):
        '''
        returns the name of the card id given
        '''
        return {0 : 'Knight', 1 : 'Victory Point',\
            2 : 'Road Building', 3 : 'Monopoly', 4 : 'Year of Plenty'}[card]


    def initialize_stack(self):
        '''
        initializes deck
        '''
        self.cards_left = 25
        self.stack = [0] * 14 + [1] * 5 + [2] * 2 + [3] * 2 + [4] * 2
        random.shuffle(self.stack)


    def take_card(self, player):
        '''
        takes a card from the top of the stack and gives it to the player
        '''
        if self.cards_left > 0:
            self.cards_left -= 1
            card = self.stack[self.cards_left]
            if player.dev_cards[self.get_card_name(card)] > 1:
                player.dev_cards[self.get_card_name(card)] += 1
            else:
                player.dev_cards[self.get_card_name(card)] = 1
            return 1
        return -1