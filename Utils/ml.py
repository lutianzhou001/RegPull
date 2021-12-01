import pandas as pd
from sklearn.cluster import KMeans
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.manifold import TSNE

def analize_cluster(X, clusters):
    for cluster in clusters:
        df_clus = X.loc[X["Target"] == cluster]
        print(df_clus)

def do_kmeans(X):
    scaler = StandardScaler()
    X_scal = scaler.fit_transform(X)
    #model = DBSCAN(eps=3, min_samples=2)
    model = KMeans(n_clusters=4, random_state=20)
    # fit model and predict clusters
    yhat = model.fit_predict(X_scal)
    # retrieve unique clusters
    clusters = np.unique(yhat)
    X["Target"] = yhat
    analize_cluster(X, clusters)
    # create scatter plot for samples from each cluster
    X_scal = TSNE(n_components=2, learning_rate=100, random_state=1997).fit_transform(X_scal)
    for cluster in clusters:
        # get row indexes for samples with this cluster
        row_ix = np.where(yhat == cluster)
        # create scatter of these samples
        plt.scatter(X_scal[row_ix, 0], X_scal[row_ix, 1])
    # show the plot
    plt.savefig("KMeans.png")


df = pd.read_csv("../data/features.csv", index_col="Unnamed: 0").replace(float('nan'), 0).replace(float('inf'), 0).drop(["activity","total_variance"], axis=1)
do_kmeans(df)
print(df)
