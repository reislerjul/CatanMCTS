from Coach import Coach

args = {
    'numIters': 10,
    'numEps': 10,
    'round_threshold': 50,
    'checkpoint': 'trainExamplesMCTS/',
    'load_folder_file': ('trainExamplesMCTS','temp.pth.tar'),
    'numItersForTrainExamplesHistory': 5, 
    'num_simulations': 10,
}

if __name__=="__main__":
    c = Coach(args)
    c.learn()