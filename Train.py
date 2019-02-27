from TrainNN import TrainNN

args = {
    'numIters': 50,
    'numEps': 40,
    'arenaCompare': 50,
    'round_threshold': 100,
    'checkpoint': 'trainExamples/',
    'load_folder_file': ('trainExamples/','temp.pth.tar'),
    'numItersForTrainExamplesHistory': 10, 
    'updateThreshold': 0.02, 
    'randomCompare': 50, 
    'load_from_checkpoint': 4
}

if __name__=="__main__":
    c = TrainNN(args)
    c.learn()