import random
import settings

from utils import Card

# This should represent the deck for dev cards. It should include the
# correct number of each dev card and should have this as a stack data
# structure. There should be a function that allows a player to take
# from the top of this stack.
class Deck():

    def __init__(self):
        self.cards_left = ()
        self.initialize_stack()

    def initialize_stack(self):
        '''
        initializes deck
        '''
        self.cards_left = ([Card.KNIGHT] * 14
                         + [Card.VICTORY_POINT] * 5
                         + [Card.ROAD_BUILDING] * 2
                         + [Card.MONOPOLY] * 2
                         + [Card.YEAR_OF_PLENTY] * 2)

    def take_card(self, card_index):
        '''
        pulls the dev card from the deck
        '''
        if card_index < len(self.cards_left):
            card = self.cards_left[card_index]
            self.cards_left.pop(card_index)
            return card
        return -1

    def peek(self):
        '''
        returns the index of a random card in the deck
        '''
        num_cards = len(self.cards_left)
        if num_cards > 0:
            selected = random.randint(0, num_cards - 1)
            return selected
        return -1

