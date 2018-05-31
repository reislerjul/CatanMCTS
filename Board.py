import random
import settings

# This represents the catan board. The board should essentially have a
# coordinate system that keeps track of where the ports are, where each
# resource is, the number that is on each hexagon, where cities/settlements
# are, where the robber is. 
class Board():

    def __init__(self, players):
        self.players = players
        self.robber = (2,0)
        self.resources = self.init_resources()
        self.hex = self.init_hexes()
        self.coords = self.init_board(debug = False)
        self.r_allocator = {}
        self.adjacent = {}
        self.largest_army_size = 2
        self.largest_army_player = None
        self.longest_road_size = 4
        self.longest_road_player = None
        self.resource_list = ['w', 'b', 'l', 'g', 'o']
        

    def init_board(self, debug = False):
        '''creates the coordinate system and inits the board 
        the coordinate system for settlements and road is defined as
        0,0 is top row leftest open location. First coordinate is the row
        second coordinate is the column. dictionaries are used so we can store
        more info about the games state
        '''
        coords = {}
        coords[(0,0)] = {'player': 0,
                         'settlement': True,
                         'resources locs': [(0,0)], 
                         'ports': '3', 
                         'neighbours': [(1,0), (1,1)],
                         'roads' : {(1,0) : 0, (1,1) : 0},
                         'available roads': [(1,0), (1,1)]
                         }
        coords[(0,1)] = {'player': 0,
                         'settlement': True,
                        'resources locs': [(0,1)], 
                        'ports': '2 w', 
                        'neighbours': [(1,1), (1,2)],
                        'roads' : {(1, 1): 0, (1, 2): 0},
                        'available roads': [(1,1), (1,2)]
                                 } 
        coords[(0,2)] = {'player': 0,
                         'settlement': True,
                        'resources locs': [(0,2)], 
                        'ports': '', 
                        'neighbours': [(1,2), (1,3)],
                        'roads' : {(1, 2): 0, (1, 3): 0},
                        'available roads': [(1,2), (1,3)]
                                 }   
        coords[(1,0)] = {'player': 0,
                         'settlement': True,
                        'resources locs': [(0,0)], 
                        'ports': '3', 
                        'neighbours': [(2,0), (0,0)],
                        'roads' : {(2, 0): 0, (0, 0): 0},
                        'available roads': [(2,0), (0,0)]
                        }   
        coords[(1,1)] = {'player': 0,
                         'settlement': True,
                         'ports': '',
                        'resources locs': [(0,0), (0,1)], 
                        'neighbours': [(0,0), (0,1), (2,1)],
                        'roads' : {(0, 0): 0, (0,1): 0, (2,1): 0},
                        'available roads': [(0,0), (0,1), (2,1)]
                                               }   
        coords[(1,2)] = {'player': 0,
                         'settlement': True,
                         'ports': '2 w',
                        'resources locs': [(0,1), (0,2)], 
                        'neighbours': [(0,2), (0,1), (2,2)],
                        'roads' : {(0,2): 0, (0,1): 0, (2,2): 0},
                        'available roads': [(0,2), (0,1), (2,2)]
                                               }
        coords[(1,3)] = {'player': 0,
                         'settlement': True,
                        'ports': '',
                        'resources locs': [(0,2)], 
                        'neighbours': [(0,2), (2,3)],
                        'roads' : {(0,2): 0, (2,3): 0},
                        'available roads': [(0,2), (2,3)]}
        coords[(2,3)] = {'player': 0,
                         'settlement': True,
                        'ports': '3',
                        'resources locs': [(0,2), (1,3)], 
                        'neighbours': [(3,3), (1,3), (3,4)],
                        'roads' : {(3,3): 0, (1,3): 0, (3,4): 0},
                        'available roads': [(3,3), (1,3), (3,4)]}
        coords[(2,2)] = {'player': 0,
                         'settlement': True,
                        'ports': '',
                        'resources locs': [(0,2), (0,1), (1,2)], 
                        'neighbours': [(3,2), (1,2), (3,3)],
                        'roads' : {(3,2): 0, (1,2): 0, (3,3): 0},
                        'available roads': [(3,2), (1,2), (3,3)]}
        coords[(2,1)] = {'player': 0,
                         'settlement': True,
                         'ports': '',
                         'resources locs': [(0,0), (0,1),(1,1)], 
                         'neighbours': [(3,1), (1,1), (3,2)],
                         'roads' : {(3,1): 0, (1,1): 0, (3,2): 0},
                         'available roads': [(3,1), (1,1), (3,2)]}
        coords[(2,0)] = {'player': 0,
                         'settlement': True,
                        'ports': '',
                        'resources locs': [(0,0), (1,0)], 
                        'neighbours': [(3,0), (1,0), (3,1)],
                        'roads' : {(3,0): 0, (1,0): 0, (3,1): 0},
                        'available roads': [(3,0), (1,0), (3,1)]}
        coords[(3,0)] = {'player': 0,
                         'settlement': True,
                        'ports': '2 o',
                        'resources locs': [(1,0)], 
                        'neighbours': [(4,0), (2,0)],
                        'roads' : {(4,0): 0, (2,0): 0},
                        'available roads': [(4,0), (2,0)]}
        coords[(3,1)] = {'player': 0,
                         'settlement': True,
                        'ports': '',
                        'resources locs': [(1,0), (0,0), (1,1)], 
                        'neighbours': [(4,1), (2,0), (2,1)],
                        'roads' : {(4,1): 0, (2,0): 0, (2,1): 0},
                        'available roads': [(4,1), (2,0), (2,1)]} 
        coords[(3,2)] = {'player': 0,
                         'settlement': True,
                        'ports': '',
                        'resources locs': [(1,1), (0,1), (1,2)], 
                        'neighbours': [(4,2), (2,2), (2,1)],
                        'roads' : {(4,2): 0, (2,2): 0, (2,1): 0},
                        'available roads': [(4,2), (2,2), (2,1)]}
        coords[(3,3)] = {'player': 0,
                        'settlement': True,
                        'ports': '',
                        'resources locs': [(1,2), (0,2), (1,3)], 
                        'neighbours': [(4,3), (2,3), (2,2)],
                        'roads' : {(4,3): 0, (2,3): 0, (2,2): 0},
                        'available roads': [(4,3), (2,3), (2,2)]}          
        
        coords[(3,4)] = {'player': 0,
                        'settlement': True,
                        'ports': '3',
                        'resources locs': [(1,2)], 
                        'neighbours': [(2,3), (4,4)],
                        'roads' : {(2,3): 0, (4,4): 0},
                        'available roads': [(2,3), (4,4)]}
        coords[(4,0)] = {'player': 0,
                        'settlement': True,
                        'ports': '2 o',
                        'resources locs': [(1,0), (2,0)], 
                        'neighbours': [(3,0), (5,0), (5,1)],
                        'roads' : {(3,0): 0, (5,0): 0, (5,1): 0},
                        'available roads': [(3,0), (5,0), (5,1)]}
        coords[(4,1)] = {'player': 0,
                        'settlement': True,
                        'ports': '',
                        'resources locs': [(1,0), (1,1), (2,1)], 
                        'neighbours': [(3,1), (5,1), (5,2)],
                        'roads' : {(3,1): 0, (5,1): 0, (5,2): 0},
                        'available roads': [(3,1), (5,1), (5,2)]}
        coords[(4,2)] = {'player': 0,
                        'settlement': True,
                        'ports': '',
                        'resources locs': [(1,1), (1,2), (2,2)], 
                        'neighbours': [(3,2), (5,2), (5,3)],
                        'roads' : {(3,2): 0, (5,2): 0, (5,3): 0},
                        'available roads': [(3,2), (5,2), (5,3)]} 
        coords[(4,3)] = {'player': 0,
                        'settlement': True,
                        'ports': '',
                        'resources locs': [(1,2), (1,3), (2,3)], 
                        'neighbours': [(3,3), (5,3), (5,4)],
                        'roads' : {(3,3): 0, (5,3): 0, (5,4): 0},
                        'available roads': [(3,3), (5,3), (5,4)]} 
        coords[(4,4)] = {'player': 0,
                        'settlement': True,
                        'ports': '',
                        'resources locs': [(1,3), (2,4)], 
                        'neighbours': [(3,4), (5,5), (5,4)],
                        'roads' : {(3,4): 0, (5,5): 0, (5,4): 0},
                        'available roads': [(3,4), (5,5), (5,4)]} 
        coords[(5,0)] = {'player': 0,
                        'settlement': True,
                        'ports': '',
                        'resources locs': [(2,0)], 
                        'neighbours': [(4,0), (6,0)],
                        'roads' : {(4,0): 0, (6,0): 0},
                        'available roads': [(4,0), (6,0)]} 
        coords[(5,1)] = {'player': 0,
                        'settlement': True,
                        'ports': '',
                        'resources locs': [(1,0), (2,0), (2,1)], 
                        'neighbours': [(6,1), (4,0), (4,1)],
                        'roads' : {(6,1): 0, (4,0): 0, (4,1): 0},
                        'available roads': [(6,1), (4,0), (4,1)]} 
        coords[(5,2)] = {'player': 0,
                        'settlement': True,
                        'ports': '',
                        'resources locs': [(1,1), (2,1), (2,2)], 
                        'neighbours': [(6,2), (4,1), (4,2)],
                        'roads' : {(6,2): 0, (4,1): 0, (4,2): 0},
                        'available roads': [(6,2), (4,1), (4,2)]}
        coords[(5,3)] = {'player': 0,
                        'settlement': True,
                        'ports': '',
                        'resources locs': [(1,2), (2,2), (2,3)], 
                        'neighbours': [(6,3), (4,2), (4,3)],
                        'roads' : {(6,3): 0, (4,2): 0, (4,3): 0},
                        'available roads': [(6,3), (4,2), (4,3)]}
        coords[(5,4)] = {'player': 0,
                        'settlement': True,
                        'ports': '',
                        'resources locs': [(1,3), (2,3), (2,4)], 
                        'neighbours': [(6,4), (4,3), (4,4)],
                        'roads' : {(6,4): 0, (4,3): 0, (4,4): 0},
                        'available roads': [(6,4), (4,3), (4,4)]}
        coords[(5,5)] = {'player': 0,
                        'settlement': True,
                        'ports': '3',
                        'resources locs': [(2,4)], 
                        'neighbours': [(6,5), (4,4)],
                        'roads' : {(6,5): 0, (4,4): 0},
                        'available roads': [(6,5), (4,4)]}
        coords[(6,5)] = {'player': 0,
                        'settlement': True,
                        'ports': '3',
                        'resources locs': [(2,4)], 
                        'neighbours': [(5,5), (7,4)],
                        'roads' : {(5,5): 0, (7,4): 0},
                        'available roads': [(5,5), (7,4)]}
        coords[(6,0)] = {'player': 0,
                        'settlement': True,
                        'ports': '',
                        'resources locs': [(2,0)], 
                        'neighbours': [(5,0), (7,0)],
                        'roads' : {(5,0): 0, (7,0): 0},
                        'available roads': [(5,0), (7,0)]}        
        coords[(6,1)] = {'player': 0,
                        'settlement': True,
                        'ports': '',
                        'resources locs': [(3,0), (2,0), (2,1)], 
                        'neighbours': [(5,1), (7,0), (7,1)],
                        'roads' : {(5,1): 0, (7,0): 0, (7,1): 0},
                        'available roads': [(5,1), (7,0), (7,1)]} 
        coords[(6,2)] = {'player': 0,
                        'settlement': True,
                        'ports': '',
                        'resources locs': [(3,1), (2,1), (2,2)], 
                        'neighbours': [(5,2), (7,1), (7,2)],
                        'roads' : {(5,2): 0, (7,1): 0, (7,2): 0},
                        'available roads': [(5,2), (7,1), (7,2)]} 
        coords[(6,3)] = {'player': 0,
                        'settlement': True,
                        'ports': '',
                        'resources locs': [(3,2), (2,2), (2,3)], 
                        'neighbours': [(5,3), (7,2), (7,3)],
                        'roads' : {(5,3): 0, (7,2): 0, (7,3): 0},
                        'available roads': [(5,3), (7,2), (7,3)]}  
        coords[(6,4)] = {'player': 0,
                        'settlement': True,
                        'ports': '',
                        'resources locs': [(3,3), (2,3), (2,4)], 
                        'neighbours': [(5,4), (7,3), (7,4)],
                        'roads' : {(5,4): 0, (7,3): 0, (7,4): 0},
                        'available roads': [(5,4), (7,3), (7,4)]} 
        coords[(7,1)] = {'player': 0,
                        'settlement': True,
                        'ports': '',
                        'resources locs': [(3,0), (3,1), (2,1)], 
                        'neighbours': [(6,1), (6,2), (8,1)],
                        'roads' : {(6,1): 0, (6,2): 0, (8,1): 0},
                        'available roads': [(6,1), (6,2), (8,1)]} 
        coords[(7,2)] = {'player': 0,
                        'settlement': True,
                        'ports': '',
                        'resources locs': [(3,1), (3,2), (2,2)], 
                        'neighbours': [(6,2), (6,3), (8,2)],
                        'roads' : {(6,2): 0, (6,3): 0, (8,2): 0},
                        'available roads': [(6,2), (6,3), (8,2)]} 
        coords[(7,3)] = {'player': 0,
                        'settlement': True,
                        'ports': '',
                        'resources locs': [(3,2), (3,3), (2,3)], 
                        'neighbours': [(6,3), (6,4), (8,3)],
                        'roads' : {(6,3): 0, (6,4): 0, (8,3): 0},
                        'available roads': [(6,3), (6,4), (8,3)]}
        coords[(7,4)] = {'player': 0,
                        'settlement': True,
                        'ports': '',
                        'resources locs': [(3,3), (2,4)], 
                        'neighbours': [(6,4), (6,5), (8,4)],
                        'roads' : {(6,4): 0, (6,5): 0, (8,4): 0},
                        'available roads': [(6,4), (6,5), (8,4)]} 
        coords[(7,0)] = {'player': 0,
                        'settlement': True,
                        'ports': '2 g',
                        'resources locs': [(3,0), (2,0)], 
                        'neighbours': [(6,0), (6,1), (8,0)],
                        'roads' : {(6,4): 0, (6,5): 0, (8,4): 0},
                        'available roads': [(6,0), (6,1), (8,0)]} 
        coords[(8,0)] = {'player': 0,
                        'settlement': True,
                        'ports': '2 g',
                        'resources locs': [(3,0)], 
                        'neighbours': [(7,0), (9,0)],
                        'roads' : {(7,0): 0, (9,0): 0},
                        'available roads': [(7,0), (9,0)]} 
        coords[(8,4)] = {'player': 0,
                        'settlement': True,
                        'ports': '2 b',
                        'resources locs': [(3,3)], 
                        'neighbours': [(7,4), (9,3)],
                        'roads' : {(7,4): 0, (9,3): 0},
                        'available roads': [(7,4), (9,3)]}  
        coords[(8,1)] = {'player': 0,
                        'settlement': True,
                        'ports': '',
                        'resources locs': [(3,0), (3,1), (4,0)], 
                        'neighbours': [(7,1), (9,0), (9,1)],
                        'roads' : {(7,1): 0, (9,0): 0, (9,1): 0},
                        'available roads': [(7,1), (9,0), (9,1)]}
        coords[(8,2)] = {'player': 0,
                        'settlement': True,
                        'ports': '',
                        'resources locs': [(3,1), (3,2), (4,1)], 
                        'neighbours': [(7,2), (9,1), (9,2)],
                        'roads' : {(7,2): 0, (9,1): 0, (9,2): 0},
                        'available roads': [(7,2), (9,1), (9,2)]}
        coords[(8,3)] = {'player': 0,
                        'settlement': True,
                        'ports': '',
                        'resources locs': [(3,2), (3,3), (4,2)], 
                        'neighbours': [(7,3), (9,2), (9,3)],
                        'roads' : {(7,3): 0, (9,2): 0, (9,3): 0},
                        'available roads': [(7,3), (9,2), (9,3)]}
        coords[(9,0)] = {'player': 0,
                        'settlement': True,
                        'ports': '',
                        'resources locs': [(3,0), (4,0)], 
                        'neighbours': [(8,0), (10,0), (8,1)],
                        'roads' : {(8,0): 0, (10,0): 0, (8,1): 0},
                        'available roads': [(8,0), (10,0), (8,1)]}   
        coords[(9,1)] = {'player': 0,
                        'settlement': True,
                        'ports': '',
                        'resources locs': [(3,1), (4,0), (4,1)], 
                        'neighbours': [(8,1), (10,1), (8,2)],
                        'roads' : {(8,1): 0, (10,1): 0, (8,2): 0},
                        'available roads': [(8,1), (10,1), (8,2)]} 
        coords[(9,2)] = {'player': 0,
                        'settlement': True,
                        'ports': '',
                        'resources locs': [(3,2), (4,1), (4,2)], 
                        'neighbours': [(8,2), (10,2), (8,3)],
                        'roads' : {(8,2): 0, (10,2): 0, (8,3): 0},
                        'available roads': [(8,2), (10,2), (8,3)]}
        coords[(9,3)] = {'player': 0,
                        'settlement': True,
                        'ports': '2 b',
                        'resources locs': [(3,3), (4,2)], 
                        'neighbours': [(8,3), (10,3), (8,4)],
                        'roads' : {(8,3): 0, (10,3): 0, (8,4): 0},
                        'available roads': [(8,3), (10,3), (8,4)]}
        coords[(10,3)] = {'player': 0,
                        'settlement': True,
                        'ports': '',
                        'resources locs': [(4,2)], 
                        'neighbours': [(9,3), (11,2)],
                        'roads' : {(9,3): 0, (11,2): 0},
                        'available roads': [(9,3), (11,2)]}
        coords[(10,0)] = {'player': 0,
                        'settlement': True,
                        'ports': '3',
                        'resources locs': [(4,0)], 
                        'neighbours': [(9,0), (11,0)],
                        'roads' : {(9,0): 0, (11,0): 0},
                        'available roads': [(9,0), (11,0)]}
        coords[(10,1)] = {'player': 0,
                        'settlement': True,
                        'ports': '',
                        'resources locs': [(4,0), (4,1)], 
                        'neighbours': [(9,1), (11,0), (11,1)],
                        'roads' : {(9,1): 0, (11,0): 0, (11,1): 0},
                        'available roads': [(9,1), (11,0), (11,1)]} 
        coords[(10,2)] = {'player': 0,
                        'settlement': True,
                        'ports': '2 l',
                        'resources locs': [(4,1), (4,2)], 
                        'neighbours': [(9,2), (11,1), (11,2)],
                        'roads' : {(9,2): 0, (11,1): 0, (11,2): 0},
                        'available roads': [(9,2), (11,1), (11,2)]}  
        coords[(11,0)] = {'player': 0,
                        'settlement': True,
                        'ports': '3',
                        'resources locs': [(4,0)], 
                        'neighbours': [(10,0), (10,1)],
                        'roads' : {(10,0): 0, (10,1): 0},
                        'available roads': [(10,0), (10,1)]} 
        coords[(11,1)] = {'player': 0,
                        'settlement': True,
                        'ports': '2 l',
                        'resources locs': [(4,1)], 
                        'neighbours': [(10,1), (10,2)],
                        'roads' : {(10,1): 0, (10,2): 0},
                        'available roads': [(10,1), (10,2)]}
        coords[(11,2)] = {'player': 0,
                        'settlement': True,
                        'ports': '',
                        'resources locs': [(4,2)], 
                        'neighbours': [(10,2), (10,3)],
                        'roads' : {(10,2): 0, (10,3): 0},
                        'available roads': [(10,2), (10,3)]}          
        
        if debug == True:
            for key, val in coords.items():
                if val['available roads'] != val['neighbours']:
                    print (key)
                for i in val['resources locs']:
                    try:
                        a = self.resources[i[0]][i[1]]
                    except IndexError as e:
                        print (key, e)

        return coords


    # Print the board state
    def print_board_state(self):

        # Print the coordinates if there is a settlement or city there.
        board_items = self.coords.items()
        for coordinate in board_items:
            if coordinate[1]['player'] != 0:
                print("Coordinates: " + str(coordinate[0]))
                print(str(coordinate[1]))
                print("\n")
        print("Robber location " + str(self.robber))
        

    def init_resources(self):
        '''this function initializes the nodes of resources in a list like faction
        a resource is given by a tuple with the first element being the resource
        the second element being the number on the die needed to roll that resource
        and the third element being a 0, 1 value to denote whether a robbber is at that location and
        this list of resources is a list of list with each location being a hexagonal thing on the map
        i.e. the top left corner https://www.catan.com/en/download/?SoC_rv_Rules_091907.pdf of 
        this is a forestt with 11
        w = wool, b= brick, l = lumber, g= grain, o = ore n = none'''
        return {(0, 0): ('l',11,0), (0, 1): ('w',12,0), (0, 2): ('g', 9,0),
                (1, 0): ('b', 4,0), (1, 1): ('o', 6,0), (1, 2): ('b', 5,0), (1, 3): ('w',10,0),
                (2, 0): ('n',-1,1), (2, 1): ('l', 3,0), (2, 2): ('g',11,0), (2, 3): ('l', 4,0), (2, 4): ('g', 8,0),
                (3, 0): ('b', 8,0), (3, 1): ('w',10,0), (3, 2): ('w', 9,0), (3, 3): ('o', 3,0),
                (4, 0): ('o', 5,0), (4, 1): ('g', 2,0), (4, 2): ('l', 6,0)}
    
    def init_hexes(self):
        '''
        input to hexes is a die roll, output is a list of hex coordinates representing the locations
        '''
        return {2: [(4, 1)], 3: [(2, 1), (3, 3)], 4: [(1, 0), (2, 3)], 5: [(1, 2), (4, 0)],
                6: [(1, 1), (4, 2)], 7: [], 8: [(2, 4), (3, 0)], 9: [(0, 2), (3, 2)],
                10: [(1, 3), (3, 1)], 11: [(0, 0), (2, 2)], 12: [(0, 1)]}
    
    def discard_random(self, player):
        '''
        removes a random resource from the given player and returns it
        '''
        total_resources = 0
        for resource in self.resource_list:
            #if player.resources[resource] > 0:
            total_resources += player.resources[resource]
        
        if total_resources > 0:
            r = random.randint(1, total_resources)
            for resource in self.resource_list:
                if r <= player.resources[resource]:
                    player.resources[resource] -= 1
                    return resource
                else:
                    r -= player.resources[resource]
    
    def steal_from(self, victim_player, thief_player):
        '''
        gives thief_player a random resource card stolen from victim_player
        '''

        # There is a case where robber is moved and nobody is stolen from
        if victim_player != None:
            resource = self.discard_random(victim_player)

            # If the player doesn't have a resource, nothing should happen
            if resource != None:
                self.give_resource(resource, thief_player)
    
    def players_adjacent_to_hex(self, loc):
        '''
        returns a list of players adjacent to that hex
        '''
        if loc in self.adjacent:
            return self.adjacent[loc]
        else:
            return []
    
    def move_robber(self, loc, knight=False, player=None):
        '''
        moves the robber to the given hex coordinate
        '''
        self.robber = loc
        if knight:
            if player.num_knights_played > self.largest_army_size:
                # update army size
                self.largest_army_size = player.num_knights_played
                
                # move largest army card
                if self.largest_army_player is not None:
                    self.largest_army_player.largest_army = 0
                self.largest_army_player = player
                player.largest_army = 2
    
    def allocate_resources(self, die_roll, players):
        '''
        given a die roll, gives the resources to the appropriate players
        if the die roll is 7, instead, all players with more than 7 resources will discard half of their
        total resources, rounded down
        '''
        if die_roll in self.r_allocator:
            vals = self.r_allocator[die_roll]
            for player, resource, loc in vals:
                if self.robber is not loc:
                    self.give_resource(resource, player)
        if die_roll == 7:
            for player in players:

                total_resources = 0
                
                for resource in self.resource_list:
                    total_resources += player.resources[resource]
            
                if total_resources >= 8:
                    discard = total_resources // 2
                    for _ in range(discard):
                        self.discard_random(player)

        # In debug mode, print the resources that each player now has
        if settings.DEBUG:
            for player in self.players:
                print("Player " + str(player.player_num) + " has resources:")
                print("     w: " + str(player.resources['w']))
                print("     l: " + str(player.resources['l']))
                print("     b: " + str(player.resources['b']))
                print("     o: " + str(player.resources['o']))
                print("     g: " + str(player.resources['g']))
            
    def give_resource(self, resource, player):
        '''
        helper function to give a resource to a player
        '''
        if resource in player.resources:
            player.resources[resource] += 1
        else:
            player.resources[resource] = 1
    
    def build_road(self, loc1, loc2, player):
        '''
        builds a road from loc1 to loc2 (assuming they are adjacent)
        '''
        self.coords[loc1]['roads'][loc2] = player
        self.coords[loc2]['roads'][loc1] = player
        self.coords[loc1]['available roads'].remove(loc2)
        self.coords[loc2]['available roads'].remove(loc1)
        
        longest_road = self.longest_road(frozenset([(loc1, loc2)]), loc1, loc2, player, 1)
        if longest_road > self.longest_road_size:
            self.longest_road_size = longest_road
            
            if self.longest_road_player is not None:
                self.longest_road_player.longest_road = 0
            self.longest_road_player = player
            player.longest_road = 2
    
    def longest_road(self, visited, current1, current2, player, length):
        '''
        helper function for finding longest road
        '''
        longest = length
        
        for neighbour in self.coords[current1]['neighbours']:
            if neighbour in list(self.coords[current1]['roads'].keys()):
                if self.coords[current1]['roads'][neighbour] == player \
                and (current1, neighbour) not in visited \
                and (neighbour, current1) not in visited:
                    new_visited = visited | set([(current1, neighbour)])
                    new_longest = self.longest_road(new_visited, neighbour, current2, player, length + 1)
                    longest = max(longest, new_longest)
        
        for neighbour in self.coords[current2]['neighbours']:
            if neighbour in list(self.coords[current2]['roads'].keys()):
                if self.coords[current2]['roads'][neighbour] == player \
                and (current2, neighbour) not in visited \
                and (neighbour, current2) not in visited:
                    new_visited = visited | set([(current2, neighbour)])
                    new_longest = self.longest_road(new_visited, current1, neighbour, player, length + 1)
                    longest = max(longest, new_longest)
        
        return longest
    
    def add_settlement(self, player, loc, initial_boost = False):
        '''
        adds a settlement at a given coordinate
        '''
        assert(self.coords[loc]['player'] == 0)
        self.coords[loc]['player'] = player
        resources = self.coords[loc]['resources locs']
        for hex_loc in resources:
            vals = self.resources[hex_loc]
            die_val = vals[1]
            ret_resource = vals[0]
            if die_val in self.r_allocator:
                self.r_allocator[die_val].append((player, ret_resource, hex_loc))
            else: 
                self.r_allocator[die_val] = [(player, ret_resource, hex_loc)]
            if hex_loc in self.adjacent:
                if player not in self.adjacent[hex_loc]:
                    self.adjacent[hex_loc].append(player)
            else:
                self.adjacent[hex_loc] = [player]
            if initial_boost:
                self.give_resource(ret_resource, player)

    def upgrade_settlement(self, player, loc):
        '''
        upgrades a settlement to a city
        '''
        assert(self.coords[loc]['player'] == player)
        assert(self.coords[loc]['settlement'])
        self.coords[loc]['settlement'] = False
        resources = self.coords[loc]['resources locs']
        for loc in resources:
            vals = self.resources[loc]
            die_val = vals[1]
            ret_resource = vals[0]
            if die_val in self.r_allocator:
                self.r_allocator[die_val].append((player, ret_resource, loc))
            else: 
                self.r_allocator[die_val] = [(player, ret_resource, loc)]
    
    def update_board(self, player, move_type, move, additional=None):
        '''
        args:
            player: Player object - 
            move_type: int - 
            move: move_type 1 - (loc1, loc2) - two coordinates to build a road between
                  move_type 2 - loc - coordinate to build a settlement at
                  move_type 3 - loc - coordinate to upgrade settlement
                  move_type 5 - string - either 'Knight', 'Road Building',
                                        'Monopoly', or 'Year of Plenty'
                  move_type 7 - loc - coordinate to move robber to
            additional:
                  move_type 5, move 'Knight' - [loc, player] - array of 2 elements
                                                               location to move robber and player
                                                               to steal from
                  move_type 5, move 'Road Building' - [loc1, loc2] - array of 2 elements
                                                                     location 1 and location 2
                                                                     to build road between
                  move_type 5, move 'Monopoly' - string - resource to steal
                  move_type 7 - string - player to steal from
        '''
        # End turn
        if move_type == 0:
            return 0

        # Build a road
        elif move_type == 1:
            self.build_road(move[0], move[1], player)

        # Build a settlement
        elif move_type == 2:
            self.add_settlement(player, move)

        # Build a city
        elif move_type == 3:
            self.upgrade_settlement(player, move)

        # Draw a dev card
        elif move_type == 4:
            pass

        # Play a dev card 
        elif move_type == 5:
            if move == 'Knight':
                self.move_robber(additional[0], knight=True, player=player)
                self.steal_from(additional[1], player)
            elif move == 'Road Building':
                self.build_road(additional[0], additional[1], player)
            elif move == 'Monopoly':
                total = 0
                for p in self.players:
                    count = p.resources[additional]
                    total += count
                    p.resources[additional] = 0
                player.resources[additional] = total
            elif move == 'Year of Plenty':
                pass
            
        # Trade with bank
        elif move_type == 6:
            pass

        # Move robber
        if move_type == 7:
            print(additional, player)
            self.move_robber(move)
            self.steal_from(additional, player)


    def getCost(self, player):
        '''this function calculates the cost for the given state and player.
        The cost is higher for a "better" state. Points given for building:
        1. Road: 2
        2. Settlement: 5
        3. Cities: 10 
        4. Ports: 3
        Points for player dev cards / resources:
        1. Dev Cards: 3
        2. Resources: 0.5 (numCards <= 7), -0.5 (numCards > 7)'''

        cost = 0.0
        dieRoll_probs = {2:1, 3:2, 4:3, 5:4, 6:5, 8:5, 9:4, 10:3, 11:2, 12:1}
        for coord in self.coords:
            if coord['player'] == player:
                # If player has settlement
                if coord['settlement']:
                    cost += 5
                else:
                # If player has city
                    cost += 10
                # Add probability of getting resources, provided there is no robber
                for loc in coord['resources locs']:
                        die_val = self.resources[loc][1]
                        isRobber = self.resources[loc][2]
                        cost += (dieRoll_probs[die_val]*isRobber/12)
                # If the player has a settlement/city at a port
                if coord['ports'] != '':
                    cost += 3
        # If player has a road
        cost += (2*player.total_roads)

        # Cost for resources
        numRes = 0
        for resource in list(player.resources.keys()):
            numRes = numRes + player.resources[resource]
            if numRes <= 7:
                cost += (0.5*player.resources[resource])
            else:
                cost = cost - (0.5*player.resources[resource])

        # If player has longest road
        cost = cost + (self.longest_road * 5)
        # If player has largest army
        cost = cost + (self.largest_army * 5)
        
        for card in list(player.dev_cards.keys()):
            cost = cost + (3*player.dev_cards[cards])

        return cost

    # This is a helper function for making the value dictionaries of coords hashable
    def hashable_values(self, value):
        hash_tuple = [0, 0, 0, 0, 0, 0, 0]
        hash_tuple[0] = ('player', value['player'])
        hash_tuple[1] = ('settlement', value['settlement'])
        hash_tuple[2] = ('resources locs', tuple(sorted(value['resources locs'])))
        hash_tuple[3] = ('ports', value['ports'])
        hash_tuple[4] = ('neighbours', tuple(sorted(value['neighbours'])))
        hash_tuple[5] = ('roads', tuple(sorted(value['roads'].items())))
        hash_tuple[6] = ('available roads', tuple(sorted(value['available roads'])))
        return tuple(hash_tuple)


    # Create a helper function that will return the current board state in a way that 
    # is hashable
    def hashable_board(self):
        board_tuple = ()

        # Add elements from the coords dictionary to the hashable state
        key_sort = sorted(self.coords.keys())
        for element in key_sort:
            entry = ((element, self.hashable_values(self.coords[element])))
            board_tuple = board_tuple + entry

        # Add the location of the robber to the hashable state
        board_tuple = board_tuple + (('robber', self.robber))
        return board_tuple        


        