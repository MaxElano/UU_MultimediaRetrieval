import sys
import os
sys.path.insert(0, os.getcwd() + "\\MRPipelineMLL") # location of src 
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc, roc_auc_score
import sklearn

# puter
class MetricsComputer(force_rerun_queries = False):
    def __init__(self):
        pass
        # If no allquery database exists, run that shi, for both ANN and KNN
        # choice to force run allquery db

    # Create a csv file with shape, and then all returns (in which category they are)
    # exclude the shape itself from returns?
    # Choice between ANN and KNN
    def run_all_queries():
        pass
    # Inspired by the function in the tutorial

    # change queen
    def get_query_results(results_path):
        results = {}
        ground_truth = {}
        with open(results_path, newline='') as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=';', quotechar='|')
            for i, row in enumerate(csv_reader):
                row_items = row[0].split(",")
                query_path = row_items.pop(0)
                query_class = row_items.pop(0)
                k = len(row_items)
                results[query_path] = [result_class for result_class in row_items]
                ground_truth[query_path] = [query_class for _ in range(k)]
        
        return results, ground_truth

    # Calculates the TP, TN, FP, FN
    def calculate_truths(query_info, K):
        for mesh, true_class, results in query_info:
            TP = results.count(true_class)
            FP = K - TP
            FN = results.count(true_class) - TP
            TN = len(results) - TP - FP - FN
            
            TPR = TP/(TP+FN)
            FPR = FP/(FP+TN)

    def compute_metrics():
        pass

    def compute_ROC():
        sklearn.metrics.roc_curve()

    def compute_AUROC():
        sklearn.metrics.roc_auc_score()

    def plot_scalar_metric():
        pass

    def show_ROC():
        pass

    

