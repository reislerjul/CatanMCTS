import os
import random
import numpy as np
from CatanNNet import CatanNNet as cnnet
import keras

args = {
    'lr': 0.001,
    'dropout': 0.3,
    'epochs': 10,
    'batch_size': 64,
    'cuda': False,
}

class Generator(keras.utils.Sequence):

    def __init__(self, filenames, batch_size):
        self.filenames = filenames
        self.batch_size = batch_size

    def __len__(self):
        return len(self.filenames)

    def __getitem__(self, idx):
        example = self.filenames[idx]
        input_boards, target_pis, target_vs = list(zip(*example))
        input_boards = np.asarray(input_boards)
        target_pis = np.asarray(target_pis)
        target_vs = np.asarray(target_vs)
        return input_boards, [target_pis, target_vs]

class NNetWrapper():
    def __init__(self):
        self.nnet = cnnet(args)
        self.board_x = 1101
        self.action_size = 3151

    def train(self, examples):
        """
        examples: list of examples, each example is of form (board, pi, v)
        """
        input_boards, target_pis, target_vs = list(zip(*examples))
        input_boards = np.asarray(input_boards)
        target_pis = np.asarray(target_pis)
        target_vs = np.asarray(target_vs)
        self.nnet.model.fit(x=input_boards, y=[target_pis, target_vs], \
            batch_size=args['batch_size'], epochs=args['epochs'])

    def predict(self, board):
        """
        board: np array with board
        """
        # preparing input
        board = board[np.newaxis, :]
        # run
        pi, v = self.nnet.model.predict(board)
        return pi[0], v[0]

    def save_checkpoint(self, folder='checkpoint', filename='checkpoint.pth.tar'):
        filepath = os.path.join(folder, filename)
        if not os.path.exists(folder):
            print("Checkpoint Directory does not exist! Making directory {}".format(folder))
            os.mkdir(folder)
        else:
            print("Checkpoint Directory exists! ")
        self.nnet.model.save_weights(filepath)

    def load_checkpoint(self, folder='checkpoint', filename='checkpoint.pth.tar'):
        # https://github.com/pytorch/examples/blob/master/imagenet/main.py#L98
        filepath = os.path.join(folder, filename)
        if not os.path.exists(filepath):
            raise("No model in path {}".format(filepath))
        self.nnet.model.load_weights(filepath)