from sklearn.manifold import TSNE
import numpy as np
import csv
import open3d as o3d
from matplotlib import pyplot as plt
import Utility.utility as util
from FeatureExtraction.featureTester import DistFeature 
import Utility.config as config

class CustomTSNE():
    def __init__(self, global_features_path, distribution_features_path):
        self.global_features_path = global_features_path
        self.distribution_features_path = distribution_features_path
        config.initialize(skip_renderer=True)

    def get_features(self, global_features_path, distribution_features_path):
        feature_databases = util.load_numpy_file(global_features_path)
        meta_db = feature_databases['metadata']
        feature_db = feature_databases['features']
        dist_db = util.load_numpy_file(distribution_features_path)
        total_features = util.combine_feature_vectors(feature_db, dist_db)
        weights1 = feature_databases['weight_factors']
        weights2 = dist_db['weight_factors'] / 20
        weights3 = np.repeat(weights2, 20)
        total_weights = np.concat((weights1, weights3), axis=0)
        classes = meta_db[:,2]
        paths = [f"{meta_db[x,2]}/{meta_db[x,1]}" for x in range(meta_db.shape[0])]
        weighted_features = np.multiply(total_features, total_weights)
        return weighted_features, classes, paths

    def create_tsne(self, *, n_components=2, perplexity=40, max_iter=5000, early_exaggeration=12,learning_rate='auto',n_iter_without_progress=300, min_grad_norm=1e-07, metric='euclidean', metric_params=None, verbose=0, random_state=None, method='barnes_hut', init="random",angle=0.5, n_jobs=None):
        # Load feature vectors for db shapes
        features_total, labels, paths = self.get_features(self.global_features_path, self.distribution_features_path)

        # Embed feature vectors in lower-dimensional space using T-distributed Stochastic Neighbor Embedding (t-SNE)
        # https://scikit-learn.org/stable/modules/generated/sklearn.manifold.TSNE.html
        features_embedded = TSNE(n_components=n_components, 
                                 perplexity=perplexity, 
                                 max_iter=max_iter, 
                                 early_exaggeration=early_exaggeration, 
                                 learning_rate=learning_rate, 
                                 n_iter_without_progress=n_iter_without_progress, 
                                 min_grad_norm=min_grad_norm, 
                                 metric=metric,
                                 metric_params=metric_params,
                                 verbose=verbose,
                                 random_state=random_state,
                                 method=method,
                                 angle=angle,
                                 n_jobs=n_jobs,
                                 init="random").fit_transform(features_total)
        return features_embedded, labels, paths
    
    def plot(self, features_embedded, labels, paths, show=True, save=False, name_folder='', name_image='', show_legend=False, include=None, exclude=None):
        # --- Visualize results --- #
        # Create colors map
        color_base = [[242,121,121], [115,92,0], [0,230,61], [115,135,153], [242,191,255], [153,115,115], [242,206,61], [121,242,170], [0,92,230], [153,77,148], [140,19,0], [76,69,38], [153,204,173], [38,84,153], [255,0,204], [89,31,22], [255,242,191], [0,77,41], [0,31,115], [166,0,111], [229,103,57], [153,150,115], [38,153,115], [0,0,166], [89,0,60], [153,97,77], [234,242,121], [0,230,214], [191,191,255], [77,57,70], [204,167,153], [148,153,77], [191,255,251], [120,115,153], [153,115,135], [89,36,0], [161,242,0], [115,153,150], [68,0,255], [242,121,170], [255,140,64], [51,77,0], [0,71,77], [17,0,64], [140,0,37], [242,170,121], [225,255,191], [38,145,153], [89,70,140], [76,0,20], [140,75,0], [152,217,108], [0,184,230], [124,48,191], [242,61,109], [51,27,0], [0,140,0], [35,105,140], [49,32,64], [255,0,34], [255,166,64], [0,115,0], [191,234,255], [204,0,255], [153,77,87], [127,98,64], [86,115,86], [0,41,77], [71,0,89], [255,191,200], [204,170,102], [38,51,38], [61,157,242], [218,121,242]]
        color_base = np.asarray(color_base) / 255

        unique_classes, start_indices, counts = np.unique(labels,return_index=True,return_counts=True)

        color_map = {}
        for idx, label in enumerate(unique_classes):
            color_map[label] = color_base[idx]

        fig, ax = plt.subplots()

        scatters = []
        for classs, start_idx, count in zip(unique_classes, start_indices, counts):
            if (include is not None and classs not in include):
                continue
            if (exclude is not None and classs in exclude):
                continue
            scat = ax.scatter(features_embedded[start_idx:start_idx+count,0], features_embedded[start_idx:start_idx+count,1], c=[color_map[classs]], label=classs)
            scatters.append(scat)
        scatters = np.asarray(scatters)

        if (show_legend or len(include) < 15):
            ax.legend(loc="upper right", ncols = 1, fontsize= 'x-small',  title="Classes") # mode='expand', , bbox_to_anchor=(1.1, 0.5)

        annot = ax.annotate("", xy=(0,0), xytext=(20,20),textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="w"),
                    arrowprops=dict(arrowstyle="->"))
        annot.set_visible(False)

        if (save):
            util.create_folder(f"Data\\Screenshots\\TSNE\\{name_folder}")
            plt.savefig(f"Data\\Screenshots\\TSNE\\{name_folder}\\{name_image}")
        
        if (show):
            def update_annot(ind, sc, scidx):
                pos = sc.get_offsets()[ind["ind"][0]]
                annot.xy = pos
                mask = unique_classes == sc.get_label()
                start_pos = start_indices[mask][0]
                mesh = paths[start_pos+ind["ind"][0]]
                text = mesh.replace(".npz", "")
                annot.set_text(text)
                annot.get_bbox_patch().set_facecolor(color_base[scidx])
                annot.get_bbox_patch().set_alpha(0.4)
    
            def hover(event):
                vis = annot.get_visible()
                if event.inaxes == ax:
                    fcont, find, fsc, scid = False, 0, None, 0
                    for idx, sc in enumerate(scatters):
                        fsc = sc
                        fcont, find = sc.contains(event) 
                        scid = idx
                        if fcont:
                            break
                    
                    if fcont:
                        update_annot(find, fsc, scid)
                        annot.set_visible(True)
                        fig.canvas.draw_idle()
                    else:
                        if vis:
                            annot.set_visible(False)
                            fig.canvas.draw_idle()

            fig.canvas.mpl_connect("motion_notify_event", hover)
            plt.show()
        plt.close()


    def create_test_array(self, **kwargs):
        ranges = []
        names = []
        for k, val in kwargs.items():
            (lb,ub,ss) = val
            ranges.append(np.arange(lb, ub+ss, ss))
            names.append(k)

        if len(kwargs) > 1:
            total_test = util.cartesian_product(*ranges)
        else:
            total_test = np.transpose(ranges)
            names = names
        return names, total_test

# <-------------- CALLABLE FUNCTIONS -------------->

    def show_tsne(self, include=None, exclude=None):
        config.lg.log(f"Showing TSNE")
        features_embedded, labels, paths = self.create_tsne(max_iter=750, perplexity=50, early_exaggeration=10)
        config.lg.log(f"\\_TSNE created")
        self.plot(features_embedded, labels, paths, show=True, save=False, include=include, exclude=exclude)

    # TSNE parameters are allowed as kwargs: https://scikit-learn.org/stable/modules/generated/sklearn.manifold.TSNE.html
    # Each test parameter must consist of (lowerbound, upperbound, stepsize)
    # Include and exclude only for showing, still computes with all classes
    def test_tsne_values(self, test_case_folder_name="Default", include=None, exclude=None, **kwargs):
        config.lg.log(f"Starting TSNE test with parameters {kwargs}")
        parameter_names, total_test_values = self.create_test_array(**kwargs)
        config.lg.log(f"\\_Test cases generated")
        pc = util.ProgressCounter(len(total_test_values), 25, "cases tested")

        for case in total_test_values:
            parameter_list = {k: v for k, v in zip(parameter_names, case)}
            features_embedded, labels, paths = self.create_tsne(n_jobs=-1,**parameter_list)
            lines = [f"{k}_{val}" for k,val in parameter_list.items()]
            name = "-".join(lines)
            self.plot(features_embedded, labels, paths, show=False, save=True, name_folder=test_case_folder_name, name_image=name, include=include, exclude=exclude)
            pc.increment()

        config.lg.log(f"Done with TSNE test")
