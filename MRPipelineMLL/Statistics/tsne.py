from sklearn.manifold import TSNE
import numpy as np
import csv
import open3d as o3d
from matplotlib import pyplot as plt
import Utility.utility as util
from FeatureExtraction.featureTester import DistFeature 

class CustomTSNE():
    def __init__(self, global_features_path, distribution_features_path, tsne_perplexity = 200, tsne_no_components = 2):
        self.global_features_path = global_features_path
        self.distribution_features_path = distribution_features_path
        self.tsne_perplexity = tsne_perplexity
        self.tsne_no_components = tsne_no_components

    def get_features(self, global_features_path, distribution_features_path):
        feature_databases = util.load_numpy_file(global_features_path)
        meta_db = feature_databases['metadata']
        feature_db = feature_databases['features']
        dist_db = util.load_numpy_file(distribution_features_path)
        total_features = feature_db[:,1:]

        for feature in DistFeature:
            _, name = feature.value
            current_dist = dist_db[name]
            total_features = np.concatenate((total_features, current_dist[:,1:]), axis=1)

        classes = meta_db[:,2]
        paths = [f"{meta_db[x,2]}/{meta_db[x,1]}" for x in range(meta_db.shape[0])]
        
        return total_features, classes, paths

    def show_tsne(self):
        # Load feature vectors for db shapes
        features_total, labels, paths = self.get_features(self.global_features_path, self.distribution_features_path)

        # Embed feature vectors in lower-dimensional space using T-distributed Stochastic Neighbor Embedding (t-SNE)
        #features_embedded = TSNE(n_components=self.tsne_no_components, perplexity=self.tsne_perplexity).fit_transform(features_total)
        features_embedded = TSNE(n_components=self.tsne_no_components, perplexity=self.tsne_perplexity, max_iter=10000, init="random").fit_transform(features_total)

        # --- Visualize results --- #
        # Create colors map
        colors_map = {}
        prev_color = 0
        for label in labels:
            if label not in colors_map.keys():
                colors_map[label] = prev_color + 0.1
                prev_color += 0.3

        # Create colors per class
        colors = []
        for label in labels:
            colors.append(colors_map[label])
        colors = np.array(colors)

        # Create plot
        fig, ax = plt.subplots()
        ax.scatter(features_embedded[:,0], features_embedded[:,1], c=colors)
        for path, x, y in zip(paths, features_embedded[:,0], features_embedded[:,1]):
            pass
            #ax.annotate(path.replace("/m", "-").replace(".npz", ""), (x, y))
        plt.show()