import sys
import os
sys.path.insert(0, os.getcwd() + "\\MRPipelineMLL") # location of src 
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc, roc_auc_score, precision_score, recall_score, f1_score
import sklearn
from Matching.matcher import Matcher
import Utility.utility as util
import csv
import gc
import numpy as np

# puter
class MetricsComputer():
    def __init__(self, force_rerun_queries = False, db = "Data\\OriginalShapeDatabase"):
        self.matcher = Matcher()
        self.db = db
        self.force_rerun = force_rerun_queries
        self.shapes = util.get_all_files(self.db)
        self.query_info = []
        self.category_lookup = {
            str(shape[2]): str(shape[1])
            for shape in self.shapes
        }

    # If no allquery database exists, run that shi, for both ANN and KNN
    # choice to force run allquery db
    def compute_results(self):
        self.run_all_queries()
        print("slay and yas")
            #self.run_all_queries(ANN=False, start=i+20, end= i+21)

    # Create a csv file with shape, and then all returns (in which category they are)
    # exclude the shape itself from returns?
    # Choice between ANN and KNN
    def run_all_queries(self, ANN = False, start = 0, end = None):
        shape_amt = len(self.shapes)
        if end is None:
            end = shape_amt
        # lekker gehardcode mb
        if ANN:
            file = "Data\\DataAnalysis\\ANNruns.csv"
        else:
            file = "Data\\DataAnalysis\\KNNruns.csv"

        # sorry im lazy
        # basically if you rerun, just get the whole bunch
        if self.force_rerun:
            with open(file, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                for shape in self.shapes[start:end]:
                    sorted_shapes, _ = self.matcher.get_meta_sorted_by_distance(util.get_path(shape), use_ann=ANN, k=shape_amt, mesh_exists = True)
                    result = [str(shape[2])] + [str(s[2]) for s in sorted_shapes]
                    writer.writerow(result)

                    csvfile.flush()
                    del sorted_shapes
                    del result
                    gc.collect()
        # otherwise adddd
        else:
            with open(file, "a", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                for shape in self.shapes[start:end]:
                    sorted_shapes, _ = self.matcher.get_meta_sorted_by_distance(util.get_path(shape), use_ann=ANN, k=shape_amt, mesh_exists = True)
                    result = [str(shape[2])] + [str(s[2]) for s in sorted_shapes]
                    writer.writerow(result)

                    csvfile.flush()
                    del sorted_shapes
                    del result
                    gc.collect()


    # change queen
    def get_query_results(self, ANN = True):
        results=[]
        #lekker gehardcode mb
        if ANN:
            file = "Data\\DataAnalysis\\ANNruns.csv"
        else:
            file = "Data\\DataAnalysis\\KNNruns.csv"
        with open(file, "r", newline="", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                shape = row[0]
                category = self.category_lookup[shape]
                results.append((shape, category, row[1:]))
        return results

    # Calculates the TP, TN, FP, FN
    def calculate_truths(self, query_info, K):
        TP = FP = FN = TN = 0
        for mesh, true_class, results in query_info:
            retrieved = results[:K]

            relevant_total = sum(
                1 for shape in self.shapes
                if str(shape[1]) == true_class
            )

            current_TP = sum(
                1 for result in retrieved
                if result == true_class
            )

            current_FP = len(retrieved) - current_TP
            current_FN = relevant_total - current_TP

            total_irrelevant = len(self.shapes) - 1 - relevant_total
            current_TN = total_irrelevant - current_FP

            TP += current_TP
            FP += current_FP
            FN += current_FN
            TN += current_TN

        TPR = TP / (TP + FN) if TP + FN else 0
        FPR = FP / (FP + TN) if FP + TN else 0

        return 1 - FPR, TPR

    def compute_metrics(self):
        query_info = self.get_query_results(ANN=True)

        # full ROC
        fpr, tpr = self.compute_ROC(query_info)
        self.show_ROC(fpr, tpr, "ANN")

        # ROC per category

        # ROC for a random shape fuck it we ball

    def compute_ROC(self, query_info):
        fpr_values = []
        tpr_values = []
        K_values = range(0, len(self.shapes), 10)
        for K in K_values:
            TPR, FPR = self.calculate_truths(query_info, K)
            tpr_values.append(TPR)
            fpr_values.append(FPR)

        return fpr_values, tpr_values

    def plot_scalar_metric():
        pass

    def show_ROC(self, fpr, tpr, label="slay"):
        sorted_indices = np.argsort(fpr)

        fpr = np.array(fpr)[sorted_indices]
        tpr = np.array(tpr)[sorted_indices]

        score = auc(fpr, tpr)

        plt.plot(fpr, tpr, marker="o", label=f"{label} (AUC={score:.3f})")
        plt.xlabel("False Postive Rate")
        plt.ylabel("True Positive Rate")
        plt.legend()
        plt.grid()
        plt.show()


mcomp = MetricsComputer()
mcomp.compute_results()