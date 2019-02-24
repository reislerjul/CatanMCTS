import os
from NNet import NNetWrapper as nn

class CurrentNN(object):
	def __init__(self):
		modelFile = os.path.join("trainExamples/", "best.pth.tar")
		self.currentNN = nn()
		if  os.path.isfile(modelFile):
			self.currentNN.nnet.model.load_weights(modelFile)