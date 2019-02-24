from MCTSNN import MCTSNN
import numpy as np
import os, sys
from pickle import Pickler, Unpickler
from random import shuffle
from Deck import Deck
from Board import Board
from MCTSNNPlayer import MCTSNNPlayer
from RandomPlayer import RandomPlayer
from Game import Game
import StateToFeatures
import settings
import multiprocessing as mp
from NNet import NNetWrapper as nn
from CurrentNN import CurrentNN


def executeEpisode(iteration):
    """
    This function executes one episode of self-play, starting with player 1.
    As the game is played, each turn is added as a training example to
    trainExamples. The game is played till the game ends. After the game
    ends, the outcome of the game is used to assign values to each example
    in trainExamples. We use a game threshold of 100 rounds
    Returns:
        trainExamples: a list of examples of the form (canonicalBoard,pi,v)
                       pi is the MCTS informed policy vector, v is +1 if
                       the player eventually won the game, else -1.
    """
    print("STARTING EPISODE " + str(iteration))

    trainExamples = []
    deck = Deck()
    players = [MCTSNNPlayer(1, 20, None), \
    MCTSNNPlayer(2, 20, None), \
    MCTSNNPlayer(3, 20, None)]
    board = Board(players, True)
    winner = None
    new_nn = CurrentNN()
    nnet = new_nn.currentNN 
    counter = 0
    while True:
        counter += 1
        if counter == 10:
            print(board.round_num)
            count = 0
        AI = MCTSNN(board, 20, deck, board.active_player.player_num, \
            nnet, board.active_player.move_to_index)
        pi = board.active_player.getActionProb(AI)
        trainExamples.append([AI.canonicalBoard, \
            board.active_player.player_num, pi])
        action = np.random.choice(len(pi), p=pi)
        move = StateToFeatures.action_to_move(action, board.active_player.move_array, \
            board.active_player, len(board.players), deck)
        board.active_player.make_move(move, board, deck, players)        
        if board.active_player.calculate_vp() >= settings.POINTS_TO_WIN:
            winner = board.active_player.player_num
        if board.round_num >= 50:
            winner = max([(player, player.calculate_vp()) for player in players], 
                key=lambda x: x[1])[0].player_num
        if winner:
            return [[x[0], x[2], (-1) ** int(x[1] != winner)] for x in trainExamples]

def versus_mode(iteration):
    '''
    Use this function for pitting the current neural network against the old one.
    '''
    # Initialize each player in a random spot
    print("STARTING VERSUS MODE " + str(iteration))
    nnet = nn()
    nnet.load_checkpoint(folder='trainExamples/', filename='best.pth.tar')
    pnet = nn()
    pnet.load_checkpoint(folder='trainExamples/', filename='temp.pth.tar')
    players = [RandomPlayer(1), MCTSNNPlayer(2, 1), \
    MCTSNNPlayer(3, 1)]
    pnet_num = 0
    nnet_num = 0
    shuffle(players)
    for j in range(len(players)):
        if players[j].player_num == 2:
            nnet_num = j + 1
        elif players[j].player_num == 3:
            pnet_num = j + 1
        players[j].player_num = j + 1

    # Play the game!
    deck = Deck()
    board = Board(players, True)

    while True:
        print(board.round_num)
        if board.active_player.player_num == pnet_num:
            move = self.board.active_player.decide_move(board, deck, players, pnet)
        elif board.active_player.player_num == nnet_num:
            move = self.board.active_player.decide_move(board, deck, players, nnet)
        else:
            move = self.board.active_player.decide_move(board, deck, players, None)
        self.board.active_player.make_move(move, board, deck, players)
        if self.board.active_player.calculate_vp() >= settings.POINTS_TO_WIN:
            if self.board.active_player.player_num == pnet_num:
                return 0
            if self.board.active_player.player_num == nnet_num:
                return 1
            return -1
        if self.board.round_num >= 3:
            if self.board.active_player.player_num == pnet_num:
                return 0
            if self.board.active_player.player_num == nnet_num:
                return 1
            return -1  

class Coach():
    """
    This class executes the self-play + learning. It uses the functions defined
    in Game and NeuralNet. args are specified in main.py.
    """
    def __init__(self, args):
        #self.nnet = nnet
        self.pnet = nn()  # the competitor network
        self.nnet = nn()
        self.args = args
        self.trainExamplesHistory = []    # history of examples from args.numItersForTrainExamplesHistory latest iterations
        self.skipFirstSelfPlay = False # can be overriden in loadTrainExamples()

    def learn(self):
        """
        Performs numIters iterations with numEps episodes of self-play in each
        iteration. After every iteration, it retrains neural network with
        examples in trainExamples.
        It then pits the new neural network against the old one and a random player
        and accepts it if there is at least a marginal improvement in the win rate.
        """

        for i in range(1, self.args['numIters'] + 1):
            # bookkeeping
            print('------ITER ' + str(i) + '------')
            # examples of the iteration

            if not self.skipFirstSelfPlay or i > 1:
                iterationTrainExamples = []
    
                # Run the episodes in parallel
                #eps = [(self.nnet) for i in range(self.args['numEps'])]
                eps = [i for i in range(self.args['numEps'])]
                num_workers = mp.cpu_count()
                with mp.Pool(num_workers) as p:
                    iterationTrainExamples = p.map(executeEpisode, eps)

                iterationExamples = []
                for element in iterationTrainExamples:
                    iterationExamples.extend(element)
    
                # save the iteration examples to the history 
                self.trainExamplesHistory.append(iterationExamples)
               
            if len(self.trainExamplesHistory) > self.args['numItersForTrainExamplesHistory']:
                print("len(trainExamplesHistory) =", len(self.trainExamplesHistory), " => remove the oldest trainExamples")
                self.trainExamplesHistory.pop(0)
            
            # backup history to a file
            # NB! the examples were collected using the model from the previous iteration, so (i-1)  
            self.saveTrainExamples(i - 1)
            
            trainExamples = []
            for e in self.trainExamplesHistory:
                trainExamples.extend(e)
            shuffle(trainExamples)

            # training new network, keeping a copy of the old one
            self.nnet.save_checkpoint(folder=self.args['checkpoint'], filename='temp.pth.tar')
            #self.pnet.load_checkpoint(folder=self.args['checkpoint'], filename='temp.pth.tar')
            
            self.nnet.train(trainExamples)
            self.nnet.save_checkpoint(folder=self.args['checkpoint'], filename='best.pth.tar')


    def getCheckpointFile(self, iteration):
        return 'checkpoint_' + str(iteration) + '.pth.tar'

    def saveTrainExamples(self, iteration):
        folder = self.args['checkpoint']
        if not os.path.exists(folder):
            os.makedirs(folder)
        filename = os.path.join(folder, self.getCheckpointFile(iteration)+".examples")
        with open(filename, "wb+") as f:
            Pickler(f).dump(self.trainExamplesHistory)
        f.closed

    def loadTrainExamples(self):
        modelFile = os.path.join(self.args['load_folder_file'][0], self.args['load_folder_file'][1])
        examplesFile = modelFile + ".examples"
        if not os.path.isfile(examplesFile):
            print(examplesFile)
            r = input("File with trainExamples not found. Continue? [y|n]")
            if r != "y":
                sys.exit()
        else:
            print("File with trainExamples found. Read it.")
            with open(examplesFile, "rb") as f:
                self.trainExamplesHistory = Unpickler(f).load()
            f.closed
            # examples based on the model were already collected (loaded)
            self.skipFirstSelfPlay = True