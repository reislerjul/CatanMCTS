from MCTSNN import MCTSNN
import numpy as np
import os, sys
from pickle import Pickler, Unpickler
import pickle
from random import shuffle
from Deck import Deck
from Board import Board
from RandomPlayer import RandomPlayer
from Game import Game
import StateToFeatures
import settings
from NNet import NNetWrapper as nn
from MCTSNNPlayer import MCTSNNPlayer

class Coach():
    """
    This class executes the self-play + learning. It uses the functions defined
    in Game and NeuralNet. args are specified in main.py.
    """
    def __init__(self, args):
        #self.nnet = nnet
        self.nnet = nn()
        self.args = args
        self.trainExamplesHistory = []    # history of examples from args.numItersForTrainExamplesHistory latest iterations
        self.skipFirstSelfPlay = False # can be overriden in loadTrainExamples()
        self.move_to_index = pickle.load(open("AllPossibleActionDict.p", "rb"))

    def executeEpisode(self, iteration):
        """
        This function executes one episode of self-play, starting with player 1.
        As the game is played, each turn is added as a training example to
        trainExamples. The game is played until the game ends. After the game
        ends, the outcome of the game is used to assign values to each example
        in trainExamples. We use a game threshold of 100 rounds
        Only collect data every few moves because otherwise, the data is too large to 
        be stored.
        Returns:
            trainExamples: a list of examples of the form (canonicalBoard,pi,v)
                           pi is the MCTS informed policy vector, v is +1 if
                           the player eventually won the game, else -1.
        """
        print("EXECUTING EPISODE" + str(iteration))
        trainExamples = []
        counter = 0
        deck = Deck()
        players = [MCTSNNPlayer(1, self.args['num_simulations']), \
        MCTSNNPlayer(2, self.args['num_simulations']), MCTSNNPlayer(3, self.args['num_simulations'])]
        board = Board(players, True)
        winner = None

        while True:
            AI = MCTSNN(board, self.args['num_simulations'], deck, \
                board.active_player.player_num, self.nnet, self.move_to_index)
            pi = AI.getActionProb(temp=1)
            action = np.random.choice(len(pi), p=pi)
            canonicalBoard = AI.canonicalBoard
            if counter % 5 == 0:
                trainExamples.append([canonicalBoard, \
                    board.active_player.player_num, pi])
            move = StateToFeatures.action_to_move(action, board.active_player.move_array, \
                board.active_player, len(board.players), deck)
            board.active_player.make_move(move, board, deck, players)    

            if board.active_player.calculate_vp() >= settings.POINTS_TO_WIN:
                winner = board.active_player.player_num
            if board.round_num >= self.args['round_threshold']:
                winner = max([(player, player.calculate_vp()) for player in players], 
                    key=lambda x: x[1])[0].player_num
            if winner:
                return [[x[0], x[2], (-1) ** int(x[1] != winner)] for x in trainExamples]
            counter += 1

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
            trainExamples = []

            if not self.skipFirstSelfPlay or i > 1:
                # Run the episodes
                for j in range(self.args['numEps']):
                    trainExamples.extend(self.executeEpisode(j + 1))

            self.saveTrainExamples(i - 1, trainExamples)
            self.trainExamplesHistory.append(trainExamples)
            if len(self.trainExamplesHistory) > self.args['numItersForTrainExamplesHistory']:
                self.trainExamplesHistory.pop()
            examples = []
            for example in self.trainExamplesHistory:
                examples.extend(example)    
            shuffle(examples)            

            # training new network, keeping a copy of the old one
            self.nnet.save_checkpoint(folder=self.args['checkpoint'], filename='temp.pth.tar')

            self.nnet.train(examples)

    def getCheckpointFile(self, iteration):
        return 'checkpoint_' + str(iteration) + '.pth.tar'

    def saveTrainExamples(self, iteration, examples):
        folder = self.args['checkpoint']
        if not os.path.exists(folder):
            os.makedirs(folder)
        filename = os.path.join(folder, self.getCheckpointFile(iteration)+".examples")
        with open(filename, "wb+") as f:
            Pickler(f).dump(examples)
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