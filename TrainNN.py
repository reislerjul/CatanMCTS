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
from NNetPlayer import NNetPlayer

class TrainNN():
    """
    This class executes the self-play + learning. It uses the functions defined
    in Game and NeuralNet. args are specified in main.py.
    """
    def __init__(self, args):
        #self.nnet = nnet
        self.nnet = nn()
        self.pnet = self.nnet.__class__()  # the competitor network
        self.args = args
        self.trainExamplesHistory = []    # history of examples from args.numItersForTrainExamplesHistory latest iterations
        self.skipFirstSelfPlay = False # can be overriden in loadTrainExamples()
        self.move_to_index = pickle.load(open("AllPossibleActionDict.p", "rb"))

    def versus_mode(self, iteration):
        '''
        Use this function for pitting the current neural network against the old one.
        '''
        # Initialize each player in a random spot
        print("ENTERING VERSUS MODE " + str(iteration))
        players = [NNetPlayer(1), NNetPlayer(2), RandomPlayer(3)]
        players[0].nnet = self.nnet 
        players[1].nnet = self.pnet
        pnet_num = 0
        nnet_num = 0
        shuffle(players)
        for j in range(len(players)):
            if players[j].player_num == 1:
                nnet_num = j + 1
            elif players[j].player_num == 2:
                pnet_num = j + 1
            players[j].player_num = j + 1

        # Play the game!
        deck = Deck()
        board = Board(players, True)
        game = Game(board, deck, players, self.args['round_threshold'], verbose=False)
        winner = game.play_game()
        if winner.player_num == pnet_num:
            return 0
        if winner.player_num == nnet_num:
            return 1
        return -1

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
        players = [NNetPlayer(1), NNetPlayer(2), NNetPlayer(3)]
        board = Board(players, True)
        winner = None

        while True:
            canonicalBoard = StateToFeatures.board_to_vector(board, deck)
            pi, value = self.nnet.predict(canonicalBoard)
            valids = StateToFeatures.possible_actions_to_vector(\
                board.active_player.get_legal_moves(board, deck), \
                board.active_player.player_num, len(players), self.move_to_index)
            pi = pi * valids
            sum_pi = sum(pi)
            if sum_pi <= 0:
                pi = pi + valids
            pi = pi / sum_pi
            if counter % 10 == 0:
                trainExamples.append([canonicalBoard, \
                    board.active_player.player_num, pi])
            action = np.random.choice(len(pi), p=pi)
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

    def versus_random_player(self, iteration):
        print("ENTERING VERSUS RANDOM MODE " + str(iteration))
        players = [NNetPlayer(1), RandomPlayer(2), RandomPlayer(3)]
        players[0].nnet = self.nnet 
        nnet_num = 0
        shuffle(players)
        for j in range(len(players)):
            if players[j].player_num == 1:
                nnet_num = j + 1
            players[j].player_num = j + 1

        # Play the game!
        deck = Deck()
        board = Board(players, True)
        game = Game(board, deck, players, self.args['round_threshold'], verbose=False)
        winner = game.play_game()
        if winner.player_num == nnet_num:
            return 1
        return 0

    def learn(self):
        """
        Performs numIters iterations with numEps episodes of self-play in each
        iteration. After every iteration, it retrains neural network with
        examples in trainExamples.
        It then pits the new neural network against the old one and a random player
        and accepts it if there is at least a marginal improvement in the win rate.
        """
        if self.args["load_from_checkpoint"] > 0:
            self.loadModel()

        for i in range(self.args["load_from_checkpoint"] + 1, self.args['numIters'] + 1):
            # bookkeeping
            print('------ITER ' + str(i) + '------')
            # examples of the iteration
            trainExamples = []

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
            self.pnet.load_checkpoint(folder=self.args['checkpoint'], filename='temp.pth.tar')

            # Batch training
            self.nnet.train(examples)

            print('PITTING AGAINST PREVIOUS VERSION')
            pwins = 0
            nwins = 0
            for j in range(self.args['arenaCompare']):
                winner = self.versus_mode(j + 1)
                if winner == 0:
                    pwins += 1
                elif winner == 1:
                    nwins += 1
            if (float(nwins) / self.args['arenaCompare']) + self.args['updateThreshold'] < \
            (float(pwins) / self.args['arenaCompare']):
                print('REJECTING NEW MODEL')
                self.nnet.load_checkpoint(folder=self.args['checkpoint'], filename='temp.pth.tar')
            else:
                print('ACCEPTING NEW MODEL')
                self.nnet.save_checkpoint(folder=self.args['checkpoint'], filename=self.getCheckpointFile(i))
                self.nnet.save_checkpoint(folder=self.args['checkpoint'], filename='best.pth.tar')   

                # For bookkeeping, play against a random player and keep track of how well it does
                nwins = 0
                for i in range(self.args['randomCompare']):
                    nwins += self.versus_random_player(i + 1)
                win_percent = nwins / self.args['randomCompare']
                self.saveWinPercentage(i, win_percent)

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

    def saveWinPercentage(self, iteration, win_percent):
        folder = self.args['checkpoint']
        if not os.path.exists(folder):
            os.makedirs(folder)
        filename = os.path.join(folder, self.getCheckpointFile(iteration)+".winPercentage")
        with open(filename, "wb+") as f:
            Pickler(f).dump(win_percent)
        f.closed

    def loadModel(self):
        self.nnet.load_checkpoint(self.args['load_folder_file'][0], self.args['load_folder_file'][1])        