import sys
from keras.models import *
from keras.layers import *
from keras.optimizers import *

class CatanNNet():
    def __init__(self, args):
        # game params
        self.board_x = 1101 
        self.action_size = 3151
        self.args = args

        # Neural Net
        self.input_board = Input(shape=(self.board_x,))
        l1 = Activation('relu')(BatchNormalization(axis=1)(Dense(512, use_bias=False)(self.input_board)))
        l2 = Dropout(args['dropout'])(Activation('relu')(BatchNormalization(axis=1)(Dense(216, use_bias=False)(l1))))
        l3 = Dropout(args['dropout'])(Activation('relu')(BatchNormalization(axis=1)(Dense(216, use_bias=False)(l1))))
        self.pi = Dense(self.action_size, activation='softmax', name='pi')(l2)  
        self.v = Dense(1, activation='tanh', name='v')(l3)                    

        self.model = Model(inputs=self.input_board, outputs=[self.pi, self.v])
        self.model.compile(loss=['categorical_crossentropy','mean_squared_error'], optimizer=Adam(args['lr']))