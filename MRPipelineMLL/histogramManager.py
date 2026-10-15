from matplotlib import pyplot as plt
import numpy as np

class histogramManager():
    def __init__(self):
        1=1

    def generate_histogram(self,
                           data_attribute,
                           items,
                           no_bins = None
                           ):
        if no_bins is None:
            no_bins = int(round(np.sqrt(len(items))))


    def plot_histogram(self,
                       data,
                       title,
                       xlabel,
                       save_path,
                       no_bins = None,
                       average=None,
                       median=None,
                       categorical = False
                       ):
        """
        plots a visualisation for a given variable
        data: array data to plot
        title: str, plot title
        xlabel: str, x-axis label
        """

        plt.figure(figsize=(8,5))

        if categorical:
            # Find each class and how often it occurs
            values, counts = np.unique(data, return_counts = True)
            plt.bar(values, counts, edgecolor = 'black')
            plt.xlabel(xlabel)
            plt.ylabel("Number of shapes")
            plt.title(title)
            plt.xticks(rotation=90, fontsize=8)

        else:
            # Choose the number of bins based on amt of data (maybe?)
            plt.hist(data, bins=no_bins, edgecolor='black')

            if average is not None:
                plt.axvline(average, color='red', linestyle='--', label='Mean')
            if median is not None:
                plt.axvline(median, color='blue', linestyle=':', label='Median')

            plt.xlabel(xlabel)
            plt.ylabel("Number of shapes")
            plt.title(title)

            if average is not None or median is not None:
                plt.legend()

        plt.tight_layout()
        plt.savefig(save_path, dpi=300)
        plt.close()

    def print_histograms(self,
                         plots):
        1=1

    def normalize_histogram(self):
        1=1
    
    def compare_two_histograms(self):
        1=1


