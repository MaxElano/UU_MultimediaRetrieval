import sys
import os
sys.path.insert(0, os.getcwd() + "\\MRPipelineMLL") # location of src 

import matplotlib.pyplot as plt
from sklearn.metrics import auc
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
    # NOTE: DO NOT RUN THIS IT TAKES AGES
    def compute_results(self, force_rerun = False):
        self.force_rerun = force_rerun
        self.run_all_queries(ANN = False)
        self.run_all_queries(ANN = True)
        print("All done!")
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
                # skip the first one everytime because that should just be himself
                results.append((shape, category, row[2:]))
        return results

        # Calculates the TP, TN, FP, FN
    def calculate_truths(self, query_info, K):
        sensitivities = []
        specificities = []

        for _, true_class, results in query_info:
            retrieved = results[:K]

            relevant_total = sum(
                1 for shape in self.shapes
                if str(shape[1]) == true_class
            ) - 1

            current_TP = sum(
                1 for result in retrieved
                if result == true_class
            )

            current_FP = len(retrieved) - current_TP
            current_FN = relevant_total - current_TP

            total_irrelevant = len(self.shapes) - 1 - relevant_total
            current_TN = total_irrelevant - current_FP

            sensitivity = (
                current_TP / (current_TP + current_FN)
                if current_TP + current_FN else 0
            )

            specificity = (
                current_TN / (current_TN + current_FP)
                if current_TN + current_FP else 0
            )

            sensitivities.append(sensitivity)
            specificities.append(specificity)

        return np.mean(sensitivities), np.mean(specificities)

    def compute_metrics(self):
        ANN_query_info = self.get_query_results(ANN=True)
        KNN_query_info = self.get_query_results(ANN=False)
        
        # full ROC
        ANN_sens, ANN_spec = self.compute_ROC(ANN_query_info)
        KNN_sens, KNN_spec = self.compute_ROC(KNN_query_info)

        self.show_ROC(ANN_sens, ANN_spec, KNN_sens, KNN_spec,label="Full dataset")

        # ROC per category
        categories = sorted(set(shape[1] for shape in self.shapes))
        for category in categories:
            ANN_category = [item for item in ANN_query_info if item[1] == category]
            KNN_category = [item for item in KNN_query_info if item[1] == category]

            ANN_sens, ANN_spec = self.compute_ROC(ANN_category)
            KNN_sens, KNN_spec = self.compute_ROC(KNN_category)

            self.show_ROC(ANN_sens, ANN_spec, KNN_sens, KNN_spec, label=str(category))

    def compute_ROC(self, query_info):
        sens_vals = []
        spec_vals = []
        K_values = list(range(0, len(self.shapes) - 1, 10))
        K_values.append(len(self.shapes))
        for K in K_values:
            sensitivity, specificity = self.calculate_truths(query_info, K)
            sens_vals.append(sensitivity)
            spec_vals.append(specificity)

        return sens_vals, spec_vals

    def show_ROC(self, ANN_sens, ANN_spec, KNN_sens, KNN_spec, label="All Queries"):
        sorted_indices = np.argsort(ANN_sens)
        ANN_sens = np.array(ANN_sens)[sorted_indices]
        ANN_spec = np.array(ANN_spec)[sorted_indices]

        sorted_indices = np.argsort(KNN_sens)
        KNN_sens = np.array(KNN_sens)[sorted_indices]
        KNN_spec = np.array(KNN_spec)[sorted_indices]

        ANN_score = auc(ANN_sens, ANN_spec)
        KNN_score = auc(KNN_sens, KNN_spec)

        plt.figure(figsize=(8,6))

        plt.plot([0, 1], [1, 0], linestyle="--", color="gray", label="Random classifier", linewidth=1)
        plt.plot(ANN_sens, ANN_spec, label=f"ANN (AUC={ANN_score:.3f})", linewidth=2)
        plt.plot(KNN_sens, KNN_spec, label =f"KNN (AUC = {KNN_score:.3f})", linewidth=2)
        plt.xlabel("Sensitivity")
        plt.ylabel("Specificity")

        plt.xlim(0, 1)
        plt.ylim(0, 1)

        plt.title(f"ROC Curves - {label}")
        plt.legend()
        plt.grid(alpha=0.3)

        util.create_folder("Data\\DataAnalysis\\ROCs")
        filename = f"ROC_{label}.png"
        filepath = os.path.join("Data\\DataAnalysis\\ROCs", filename)
        plt.savefig(filepath, dpi=300)

        print("Saved ", filename, " to filepath ", filepath)


#mcomp = MetricsComputer()
#mcomp.compute_metrics()