# This represents the catan board. The board should essentially have a
# coordinate system that keeps track of where the ports are, where each
# resource is, the number that is on each hexagon, where cities/settlements
# are, where the robber is. 
class Board():

    def __init__(self, players):
        self.players = players
        self.robber = (2,0)
        self.resources = self.init_resources()
        self.coords = self.init_board(debug = False)
        self.r_allocator = {}
        
    def init_board(self, debug = False):
        '''creates the coordinate system and inits the board 
        the coordinate system for settlements and road is defined as
        0,0 is top row leftest open location. First coordinate is the row
        second coordinate is the column. dictionaries are used so we can store
        more info about the games state'''
        coords = {}
        coords[(0,0)] = {'player belonging to': 0,
                         'resources locs': [(0,0)], 
                         'ports': '3', 
                         'neighbours': [(1,0), (1,1)],
                         'roads' : [],
                         'available roads': [(1,0), (1,1)]
                         }
        coords[(0,1)] = {'player': 0,
                        'resources locs': [(0,1)], 
                        'ports': '2 w', 
                        'neighbours': [(1,1), (1,2)],
                        'roads' : [],
                        'available roads': [(1,1), (1,2)]
                                 } 
        coords[(0,2)] = {'player': 0,
                        'resources locs': [(0,2)], 
                        'ports': '', 
                        'neighbours': [(1,2), (1,3)],
                        'roads' : [],
                        'available roads': [(1,2), (1,3)]
                                 }   
        coords[(1,0)] = {'player': 0,
                        'resources locs': [(0,0)], 
                        'ports': '3', 
                        'neighbours': [(2,0), (0,0)],
                        'roads' : [],
                        'available roads': [(2,0), (0,0)]
                        }   
        coords[(1,1)] = {'player': 0,
                         'ports': '',
                        'resources locs': [(0,0), (0,1)], 
                        'neighbours': [(0,0), (0,1), (2,1)],
                        'roads' : [],
                        'available roads': [(0,0), (0,1), (2,1)]
                                               }   
        coords[(1,2)] = {'player': 0,
                         'ports': '2 w',
                        'resources locs': [(0,1), (0,2)], 
                        'neighbours': [(0,2), (0,1), (2,2)],
                        'roads' : [],
                        'available roads': [(0,2), (0,1), (2,2)]
                                               }
        coords[(1,3)] = {'player': 0,
                        'ports': '',
                        'resources locs': [(0,2)], 
                        'neighbours': [(0,2), (2,3)],
                        'roads' : [],
                        'available roads': [(0,2), (2,3)]}
        coords[(2,3)] = {'player': 0,
                        'ports': '3',
                        'resources locs': [(0,2), (1,3)], 
                        'neighbours': [(3,3), (1,3), (3,4)],
                        'roads' : [],
                        'available roads': [(3,3), (1,3), (3,4)]}
        coords[(2,2)] = {'player': 0,
                        'ports': '',
                        'resources locs': [(0,2), (0,1), (1,2)], 
                        'neighbours': [(3,2), (1,2), (3,3)],
                        'roads' : [],
                        'available roads': [(3,2), (1,2), (3,3)]}
        coords[(2,1)] = {'player': 0,
                         'ports': '',
                         'resources locs': [(0,0), (0,1),(1,1)], 
                         'neighbours': [(3,1), (1,1), (3,2)],
                         'roads' : [],
                         'available roads': [(3,1), (1,1), (3,2)]}
        coords[(2,0)] = {'player': 0,
                        'ports': '',
                        'resources locs': [(0,0), (1,0)], 
                        'neighbours': [(3,0), (1,0), (3,1)],
                        'roads' : [],
                        'available roads': [(3,0), (1,0), (3,1)]}
        coords[(3,0)] = {'player': 0,
                        'ports': '2 o',
                        'resources locs': [(1,0)], 
                        'neighbours': [(4,0), (2,0)],
                        'roads' : [],
                        'available roads': [(4,0), (2,0)]}
        coords[(3,1)] = {'player': 0,
                        'ports': '',
                        'resources locs': [(1,0), (0,0), (1,1)], 
                        'neighbours': [(4,1), (2,0), (2,1)],
                        'roads' : [],
                        'available roads': [(4,1), (2,0), (2,1)]} 
        coords[(3,2)] = {'player': 0,
                        'ports': '',
                        'resources locs': [(1,1), (0,1), (1,2)], 
                        'neighbours': [(4,2), (2,2), (2,1)],
                        'roads' : [],
                        'available roads': [(4,2), (2,2), (2,1)]}
        coords[(3,3)] = {'player': 0,
                        'ports': '',
                        'resources locs': [(1,2), (0,2), (1,3)], 
                        'neighbours': [(4,3), (2,3), (2,2)],
                        'roads' : [],
                        'available roads': [(4,3), (2,3), (2,2)]}          
        
        coords[(3,4)] = {'player': 0,
                        'ports': '3',
                        'resources locs': [(1,2)], 
                        'neighbours': [(2,3), (4,4)],
                        'roads' : [],
                        'available roads': [(2,3), (4,4)]}
        coords[(4,0)] = {'player': 0,
                        'ports': '2 o',
                        'resources locs': [(1,0), (2,0)], 
                        'neighbours': [(3,0), (5,0), (5,1)],
                        'roads' : [],
                        'available roads': [(3,0), (5,0), (5,1)]}
        coords[(4,1)] = {'player': 0,
                        'ports': '',
                        'resources locs': [(1,0), (1,1), (2,1)], 
                        'neighbours': [(3,1), (5,1), (5,2)],
                        'roads' : [],
                        'available roads': [(3,1), (5,1), (5,2)]}
        coords[(4,2)] = {'player': 0,
                        'ports': '',
                        'resources locs': [(1,1), (1,2), (2,2)], 
                        'neighbours': [(3,2), (5,2), (5,3)],
                        'roads' : [],
                        'available roads': [(3,2), (5,2), (5,3)]} 
        coords[(4,3)] = {'player': 0,
                        'ports': '',
                        'resources locs': [(1,2), (1,3), (2,3)], 
                        'neighbours': [(3,3), (5,3), (5,4)],
                        'roads' : [],
                        'available roads': [(3,3), (5,3), (5,4)]} 
        coords[(4,4)] = {'player': 0,
                        'ports': '',
                        'resources locs': [(1,3), (2,4)], 
                        'neighbours': [(3,4), (5,5), (5,4)],
                        'roads' : [],
                        'available roads': [(3,4), (5,5), (5,4)]} 
        coords[(5,0)] = {'player': 0,
                        'ports': '',
                        'resources locs': [(2,0)], 
                        'neighbours': [(4,0), (6,0)],
                        'roads' : [],
                        'available roads': [(4,0), (6,0)]} 
        coords[(5,1)] = {'player': 0,
                        'ports': '',
                        'resources locs': [(1,0), (2,0), (2,1)], 
                        'neighbours': [(6,1), (4,0), (4,1)],
                        'roads' : [],
                        'available roads': [(6,1), (4,0), (4,1)]} 
        coords[(5,2)] = {'player': 0,
                        'ports': '',
                        'resources locs': [(1,1), (2,1), (2,2)], 
                        'neighbours': [(6,2), (4,1), (4,2)],
                        'roads' : [],
                        'available roads': [(6,2), (4,1), (4,2)]}
        coords[(5,3)] = {'player': 0,
                        'ports': '',
                        'resources locs': [(1,2), (2,2), (2,3)], 
                        'neighbours': [(6,3), (4,2), (4,3)],
                        'roads' : [],
                        'available roads': [(6,3), (4,2), (4,3)]}
        coords[(5,4)] = {'player': 0,
                        'ports': '',
                        'resources locs': [(1,3), (2,3), (2,4)], 
                        'neighbours': [(6,4), (4,3), (4,4)],
                        'roads' : [],
                        'available roads': [(6,4), (4,3), (4,4)]}
        coords[(5,5)] = {'player': 0,
                        'ports': '3',
                        'resources locs': [(2,4)], 
                        'neighbours': [(6,5), (4,4)],
                        'roads' : [],
                        'available roads': [(6,5), (4,4)]}
        coords[(6,5)] = {'player': 0,
                        'ports': '3',
                        'resources locs': [(2,4)], 
                        'neighbours': [(5,5), (7,4)],
                        'roads' : [],
                        'available roads': [(5,5), (7,4)]}
        coords[(6,0)] = {'player': 0,
                        'ports': '',
                        'resources locs': [(2,0)], 
                        'neighbours': [(5,0), (7,0)],
                        'roads' : [],
                        'available roads': [(5,0), (7,0)]}        
        coords[(6,1)] = {'player': 0,
                        'ports': '',
                        'resources locs': [(3,0), (2,0), (2,1)], 
                        'neighbours': [(5,1), (7,0), (7,1)],
                        'roads' : [],
                        'available roads': [(5,1), (7,0), (7,1)]} 
        coords[(6,2)] = {'player': 0,
                        'ports': '',
                        'resources locs': [(3,1), (2,1), (2,2)], 
                        'neighbours': [(5,2), (7,1), (7,2)],
                        'roads' : [],
                        'available roads': [(5,2), (7,1), (7,2)]} 
        coords[(6,3)] = {'player': 0,
                        'ports': '',
                        'resources locs': [(3,2), (2,2), (2,3)], 
                        'neighbours': [(5,3), (7,2), (7,3)],
                        'roads' : [],
                        'available roads': [(5,3), (7,2), (7,3)]}  
        coords[(6,4)] = {'player': 0,
                        'ports': '',
                        'resources locs': [(3,3), (2,3), (2,4)], 
                        'neighbours': [(5,4), (7,3), (7,4)],
                        'roads' : [],
                        'available roads': [(5,4), (7,3), (7,4)]} 
        coords[(7,1)] = {'player': 0,
                        'ports': '',
                        'resources locs': [(3,0), (3,1), (2,1)], 
                        'neighbours': [(6,1), (6,2), (8,1)],
                        'roads' : [],
                        'available roads': [(6,1), (6,2), (8,1)]} 
        coords[(7,2)] = {'player': 0,
                        'ports': '',
                        'resources locs': [(3,1), (3,2), (2,2)], 
                        'neighbours': [(6,2), (6,3), (8,2)],
                        'roads' : [],
                        'available roads': [(6,2), (6,3), (8,2)]} 
        coords[(7,3)] = {'player': 0,
                        'ports': '',
                        'resources locs': [(3,2), (3,3), (2,3)], 
                        'neighbours': [(6,3), (6,4), (8,3)],
                        'roads' : [],
                        'available roads': [(6,3), (6,4), (8,3)]}
        coords[(7,4)] = {'player': 0,
                        'ports': '',
                        'resources locs': [(3,3), (2,4)], 
                        'neighbours': [(6,4), (6,5), (8,4)],
                        'roads' : [],
                        'available roads': [(6,4), (6,5), (8,4)]} 
        coords[(7,0)] = {'player': 0,
                        'ports': '2 g',
                        'resources locs': [(3,0), (2,0)], 
                        'neighbours': [(6,0), (6,1), (8,0)],
                        'roads' : [],
                        'available roads': [(6,0), (6,1), (8,0)]} 
        coords[(8,0)] = {'player': 0,
                        'ports': '2 g',
                        'resources locs': [(3,0)], 
                        'neighbours': [(7,0), (9,0)],
                        'roads' : [],
                        'available roads': [(7,0), (9,0)]} 
        coords[(8,4)] = {'player': 0,
                        'ports': '2 b',
                        'resources locs': [(3,3)], 
                        'neighbours': [(7,4), (9,3)],
                        'roads' : [],
                        'available roads': [(7,4), (9,3)]}  
        coords[(8,1)] = {'player': 0,
                        'ports': '',
                        'resources locs': [(3,0), (3,1), (4,0)], 
                        'neighbours': [(7,1), (9,0), (9,1)],
                        'roads' : [],
                        'available roads': [(7,1), (9,0), (9,1)]}
        coords[(8,2)] = {'player': 0,
                        'ports': '',
                        'resources locs': [(3,1), (3,2), (4,1)], 
                        'neighbours': [(7,2), (9,1), (9,2)],
                        'roads' : [],
                        'available roads': [(7,2), (9,1), (9,2)]}
        coords[(8,3)] = {'player': 0,
                        'ports': '',
                        'resources locs': [(3,2), (3,3), (4,2)], 
                        'neighbours': [(7,3), (9,2), (9,3)],
                        'roads' : [],
                        'available roads': [(7,3), (9,2), (9,3)]}
        coords[(9,0)] = {'player': 0,
                        'ports': '',
                        'resources locs': [(3,0), (4,0)], 
                        'neighbours': [(8,0), (10,0), (8,1)],
                        'roads' : [],
                        'available roads': [(8,0), (10,0), (8,1)]}   
        coords[(9,1)] = {'player': 0,
                        'ports': '',
                        'resources locs': [(3,1), (4,0), (4,1)], 
                        'neighbours': [(8,1), (10,1), (8,2)],
                        'roads' : [],
                        'available roads': [(8,1), (10,1), (8,2)]} 
        coords[(9,2)] = {'player': 0,
                        'ports': '',
                        'resources locs': [(3,2), (4,1), (4,2)], 
                        'neighbours': [(8,2), (10,2), (8,3)],
                        'roads' : [],
                        'available roads': [(8,2), (10,2), (8,3)]}
        coords[(9,3)] = {'player': 0,
                        'ports': '2 b',
                        'resources locs': [(3,3), (4,2)], 
                        'neighbours': [(8,3), (10,3), (8,4)],
                        'roads' : [],
                        'available roads': [(8,3), (10,3), (8,4)]}
        coords[(10,3)] = {'player': 0,
                        'ports': '',
                        'resources locs': [(4,2)], 
                        'neighbours': [(9,3), (11,2)],
                        'roads' : [],
                        'available roads': [(9,3), (11,2)]} 
        coords[(10,0)] = {'player': 0,
                        'ports': '3',
                        'resources locs': [(4,0)], 
                        'neighbours': [(9,0), (11,0)],
                        'roads' : [],
                        'available roads': [(9,0), (11,0)]}
        coords[(10,1)] = {'player': 0,
                        'ports': '',
                        'resources locs': [(4,0), (4,1)], 
                        'neighbours': [(9,1), (11,0), (11,1)],
                        'roads' : [],
                        'available roads': [(9,1), (11,0), (11,1)]} 
        coords[(10,2)] = {'player': 0,
                        'ports': '2 l',
                        'resources locs': [(4,1), (4,2)], 
                        'neighbours': [(9,2), (11,1), (11,2)],
                        'roads' : [],
                        'available roads': [(9,2), (11,1), (11,2)]}  
        coords[(11,0)] = {'player': 0,
                        'ports': '3',
                        'resources locs': [(4,0)], 
                        'neighbours': [(10,0), (10,1)],
                        'roads' : [],
                        'available roads': [(10,0), (10,1)]} 
        coords[(11,1)] = {'player': 0,
                        'ports': '2 l',
                        'resources locs': [(4,1)], 
                        'neighbours': [(10,1), (10,2)],
                        'roads' : [],
                        'available roads': [(10,1), (10,2)]}
        coords[(11,2)] = {'player': 0,
                        'ports': '',
                        'resources locs': [(4,2)], 
                        'neighbours': [(10,2), (10,3)],
                        'roads' : [],
                        'available roads': [(10,2), (10,3)]}          
        
        if debug == True:
            for key, val in coords.items():
                if val['available roads'] != val['neighbours']:
                    print key
                for i in val['resources locs']:
                    try:
                        a =self.resources[i[0]][i[1]]
                    except IndexError as e:
                        print key, e
                        
        
        
        return coords
    def init_resources(self):
        '''this function initializes the nodes of resources in a list like faction
        a resource is given by a tuple with the first element being the resource
        the second element being the number on the die needed to roll that resource
        and the third element being a 0, 1 value to denote whether a robbber is at that location and
        this list of resources is a list of list with each location being a hexagonal thing on the map
        i.e. the top left corner https://www.catan.com/en/download/?SoC_rv_Rules_091907.pdf of 
        this is a forestt with 11
        w = wool, b= brick, l = lumber, g= grain, o = ore n = none'''
        resource_list = [[('l',11, 0), ('w',12, 0), ('g', 9, 0)],
                       [('b',4,0), ('o', 6,0), ('b',5,0), ('w',10,0)],
                       [('n',-1,1), ('l',3,0), ('g',11,0), ('l', 4, 0), ('g',8,0)],
                       [('b',8,0),('w',10,0), ('w',9,0), ('o',3,0)],
                       [('o',5,0), ('g',2,0), ('l',6,0)]]
        return resource_list
    
    # TODO: This class needs a function that will allocate the correct resources to 
    # each player based on the number rolled on the dice. 
    def allocate_resources(self, dice_roll):
        if dice_roll in self.r_allocator:
            # here is where we add resources by accessing the player and resource
            pass
        return
    
    '''helper function to give a resource to a player'''
    def give_resouce(self):
        return
    def add_settlement(self, player, loc, initial_boost = False):
        self.coords[loc]['player'] = player
        resources = self.coords[loc]['resources locs']
        for loc in resources:
            r = loc[0]
            c = loc[1]
            vals = self.resources[r][c]
            die_val = vals[1]
            ret_resource = vals[0]
            if die_val in self.r_allocator:
                self.r_allocator[die_val].append((player, ret_resource))
            else: 
                self.r_allocator[die_val] = [(player, ret_resource)]
    # TODO: Update the board with the move that the player makes. 
    def update_board(self):
        return
    