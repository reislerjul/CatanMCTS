from Coach import Coach

args = {
    'numIters': 40,
    'numEps': 20,
    'round_threshold': 70,
    'checkpoint': 'trainExamplesMCTS/',
    'load_folder_file': ('bestNNet','best.pth.tar'),
    'numItersForTrainExamplesHistory': 10, 
    'num_simulations': 20,
}

if __name__=="__main__":
    c = Coach(args)
    c.learn()