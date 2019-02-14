import settings
from utils import Move
import pickle

# from reference of current player, assume that its player num is 1 and everyone elses 
# is subsequnt depending on the order of play. assume three total players
settings.init()
count = 0

# We first need a mapping of actions to vector
all_possible_actions = [Move(Move.END_TURN)]
print("end turn: 1")

# All possible roads
for i in range(len(settings.roads)):
    count += 1
    source = settings.roads[i][0]
    sink = settings.roads[i][1]
    all_possible_actions.append(Move(Move.BUY_ROAD, road=frozenset([source, sink])))

print("build road: " + str(count))
count = 0

# All possible settlements and cities
for i in range(len(settings.vertices)):
    count += 1
    all_possible_actions.append(Move(Move.BUY_SETTLEMENT, coord=settings.vertices[i]))
    all_possible_actions.append(Move(Move.BUY_CITY, coord=settings.vertices[i]))

print("buying settlements/cities: " + str(count))

# Buy dev card. Note: we don't include the dev card bought or the player number
all_possible_actions.append(Move(Move.BUY_DEV))
print("buy dev card: 1")
count = 0

# Playing all possible dev cards (except victory point)
# Knight and Moving Robber
for i in range(len(settings.hexes)):
    for j in range(2, 4):
        count += 1
        all_possible_actions.append(Move(Move.PLAY_DEV, card_type=0, 
            coord=settings.hexes[i], player=j))
        all_possible_actions.append(Move(Move.MOVE_ROBBER,
            coord=settings.hexes[i], player=j))

    all_possible_actions.append(Move(Move.PLAY_DEV, card_type=0, coord=settings.hexes[i]))
    all_possible_actions.append(Move(Move.MOVE_ROBBER, coord=settings.hexes[i]))
    count += 1

print("knight/moving robber: " + str(count))
count = 0
# Road Building
combos = set()
for i in range(len(settings.roads)):

    first_road = frozenset([settings.roads[i][0], settings.roads[i][1]])
    # Build one road
    all_possible_actions.append(Move(Move.PLAY_DEV, card_type=2, road=first_road))
    count += 1

    # Build combo of 2 roads
    for j in range(len(settings.roads)):
        second_road = frozenset([settings.roads[j][0], settings.roads[j][1]])

        if first_road != second_road and frozenset([first_road, second_road]) not in combos:
            count += 1
            combos.add(frozenset([first_road, second_road]))
            all_possible_actions.append(
                Move(Move.PLAY_DEV, card_type=2, road=first_road, road2=second_road))

print("roads in road builder: " + str(count))
count = 0 
# Monopoly
for i in range(len(settings.resources)):
    all_possible_actions.append(Move(Move.PLAY_DEV, card_type=3, resource=settings.resources[i]))
    count += 1
print("monopoly count: " + str(count))
count = 0

# Year of plenty
yop_set = set()
for i in range(len(settings.resources)):
    for j in range(len(settings.resources)):
        if frozenset([i, j]) not in yop_set:
            count += 1
            yop_set.add(frozenset([i, j]))
            all_possible_actions.append(Move(Move.PLAY_DEV, card_type=4, 
                resource=settings.resources[i], resource2=settings.resources[j]))
print("yop count: " + str(count))
count = 0

# Trading Bank. Here, we won't worry about quantity of resources, only focusing on which resource
# maps to other resource
for i in range(len(settings.resources)):
    for j in range(len(settings.resources)):
        if i != j:
            count += 1
            all_possible_actions.append(Move(Move.TRADE_BANK, 
                give_resource=settings.resources[i], resource=settings.resources[j]))
print("trade with bank count: " + str(count))
count = 0

# Propose Trade. Don't include player number
for i in range(len(settings.resources)):
    for j in range(len(settings.resources)):
        if i != j:
            for k in range(1, 4):
                for h in range(1, 4):
                    count += 1
                    gain = (settings.resources[i], k)
                    loss = (settings.resources[j], h)
                    all_possible_actions.append(Move(Move.PROPOSE_TRADE, give_resource=loss, resource=gain))
print("trade with other player count: " + str(count))

# Accept Trade
all_possible_actions.append(Move(Move.ACCEPT_TRADE))
print("accept trade: 1")
# Roll dice. doesnt include number rolled or player number
all_possible_actions.append(Move(Move.ROLL_DICE))
print("roll dice: 1")
# Decline Trade
all_possible_actions.append(Move(Move.DECLINE_TRADE))
print("decline trade: 1")
count = 0
# Choose Trader
for i in range(2, 4):
    all_possible_actions.append(Move(Move.CHOOSE_TRADER, player=i))
    count += 1

all_possible_actions.append(Move(Move.CHOOSE_TRADER))
count += 1
print("choose trader: " + str(count))

# Discard Half. Don't specify the combination of cards
all_possible_actions.append(Move(Move.DISCARD_HALF))
print("discard half: 1")
print("number of possible moves " + str(len(all_possible_actions)))
#for move in all_possible_actions:
#    print(move)
#    print("")

actions_dict = {}
for i in range(len(all_possible_actions)):
    actions_dict[all_possible_actions[i]] = i
pickle.dump(all_possible_actions, open( "AllPossibleActionDict.p", "wb" ))
pickle.dump(all_possible_actions, open( "AllPossibleActionVector.p", "wb" ))


