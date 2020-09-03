from sklearn.manifold import TSNE
import os
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
palette = sns.color_palette("bright", 2)

def plot_tsne(inf, n_iter=5000, perplexity=20, method='barnes_hut'):
    data = np.loadtxt(inf, delimiter=';', skiprows=1, dtype='str')
    x_test = data[:, 2:-1].astype(np.float)
    y_test = data[:,-1].astype(np.float)

    x_embedded = TSNE(n_components=2, n_iter=n_iter, method=method, perplexity=perplexity).fit_transform(x_test)
    y = np.array(range(10))
    plot = sns.scatterplot(x_embedded[:,0], x_embedded[:,1], hue=y_test, palette=palette, legend='full')
    figure = plot.get_figure()
    figure.savefig('../output/plots/balance/balance_{}_{}.png'.format(n_iter, perplexity))
    figure.clf()


def main():
    arfffiles = os.listdir('../output')
    arfffiles = ['../output/'+x for x in arfffiles if x.endswith('.arff')]
    files = ['../output/balance_data/balance_features_standardized.csv']
    perplexities = [x*5 for x in range(1, 11)]
    n_iters = [500, 1000, 2000, 5000, 10000]

    for file in files:
        for p in perplexities:
            for ni in n_iters:
                print("Working on {}, {}".format(p, ni))
                plot_tsne(file, ni, p)

#11SS p10 nit20000+ method none
if __name__ == '__main__':
    main()
    # plot_tsne('../output/balance_features_standardized.csv', n_iter=1000, perplexity=25)