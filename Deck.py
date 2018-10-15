import random
import settings

class Card():
    '''
    Represents each of the card types
    '''
    KNIGHT = 0
    VICTORY_POINT = 1
    ROAD_BUILDING = 2
    MONOPOLY = 3
    YEAR_OF_PLENTY = 4

    def get_card_name(self, card):
        '''
        Returns name of the card id given
        '''
        return {0 : 'Knight', 1 : 'Victory Point',\
            2 : 'Road Building', 3 : 'Monopoly', 4 : 'Year of Plenty'}[card]


# This should represent the deck for dev cards. It should include the
# correct number of each dev card and should have this as a stack data
# structure. There should be a function that allows a player to take
# from the top of this stack.
class Deck():

    def __init__(self):
        self.cards_left = 20
        self.initialize_stack()

    def initialize_stack(self):
        '''
        initializes deck
        '''
        self.cards_left = [Card.KNIGHT] * 14\
                        + [Card.VICTORY_POINT] * 5\
                        + [Card.ROAD_BUILDING] * 2\
                        + [Card.MONOPOLY] * 2\
                        + [Card.YEAR_OF_PLENTY] * 2

    def take_card(self, player):
        '''
        takes a random card and gives it to the player
        '''
        num_cards = len(self.cards_left)
        if num_cards > 0:
            selected = random.randint(0, num_cards - 1)
            card = self.cards_left[selected]
            self.cards_left[selected] = self.cards_left[-1]
            del self.cards_left[-1]
            player.dev_cards[card] += 1
            return 1
        return -1

    def remove_card_type(self, card_type):
        '''
        removes a card of the given type
        '''
        index = self.cards_left.index(card_type)
        self.cards_left[index] = self.cards_left[-1]
        del self.cards_left[-1]

    '''
    def hashable_deck(self):
        s = ''
        for card in self.stack:
            s += str(card) + ' '
        return s
    '''
