import sys
import os
sys.path.insert(0, os.getcwd() + "\\MRPipelineMLL") # location of src 

import numpy as np
from matplotlib import pyplot as plt

'''
A tool that gives back the following statistics about a .csv file output by shapeAnalysis.py
It includes:
The average shape in the database (in terms of vetex and face counts)
If there are significant outliers from this average (e.g. shapes having many, or few, vertices or cells)
It does this by showing a histogram counting how many shapes are in the database for every range of the properties of interest.
The properties of interest are: number of vertices, number of faces, shape class

Then, it shows an average shape and a few outliers (if any) using the viewer.
'''

class ShapeStatistics():
    def __init__(self):
        shape_data = None

    def plot_histogram(self, 
                       data, 
                       title="Data"):
        no_bins = int(round(np.sqrt(len(data[0]))))
        counts, bins = np.histogram(data, bins=no_bins)

        # Plot histogram
        _, ax = plt.subplots()
        ax.hist(bins[:-1], bins, weights=counts)
        ax.set_title(title)
        ax.set_ylabel("Number of samples per bin")
        ax.set_xlabel("Bins")
        plt.show()

    def retrieve_data(self,
                      file_name='data_info.csv'):
        file_path = "Data\\DataAnalysis\\" + file_name
        self.shape_data = np.loadtxt(file_path, delimiter=',',dtype=str)

    def plot_histogram(self,
                       data,
                       title,
                       xlabel,
                       save_path,
                       average=None,
                       median=None,
                       categorical = False):
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
            no_bins = int(round(np.sqrt(len(data))))

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

    def get_close_shape(self, 
                          vertices, 
                          faces,
                          vertex_value,
                          face_value):
        '''
        Given the vertex and face value to apprach, this function gives back the shape
        closest to reaching those values
        '''

        distances = ((vertices - vertex_value) ** 2 + (faces - face_value) ** 2)   
        index = np.argmin(distances)
        return self.shape_data[index]

    def get_outliers(self,
                     values):
        q1 = np.percentile(values, 25)
        q3 = np.percentile(values, 75)
        iqr = q3 - q1

        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr  

        high_outliers = self.shape_data[values > upper]
        low_outliers = self.shape_data[values < lower]

        return high_outliers, low_outliers

    def show_statistics(self,
                        folder = "Data\\DataAnalysis\\statistics"):
        if not os.path.exists(folder):
            os.makedirs(folder)
        
        # Column nums
        filename_col = 0
        class_col = 1
        vertices_col =2
        faces_col = 3

        vertices = self.shape_data[:, vertices_col].astype(int)
        faces = self.shape_data[:, faces_col].astype(int)
        classes = self.shape_data[:, class_col]

        average_vertices = np.mean(vertices)
        average_faces = np.mean(faces)

        median_vertices = np.median(vertices)
        median_faces = np.median(faces)

        high_vertices, low_vertices = self.get_outliers(vertices)
        high_faces, low_faces = self.get_outliers(faces)

        average_shape = self.get_close_shape(vertices, faces, average_vertices, average_faces)
        median_shape = self.get_close_shape(vertices, faces, median_vertices, median_faces)
        simple_shape = self.get_close_shape(vertices, faces, min(vertices), min(faces))
        complex_shape = self.get_close_shape(vertices, faces, max(vertices), max(faces))

        with open(folder + "\\statistics.txt", "w") as file:
            file.write("DATABASE STATISTICS\n")
            file.write(f"Numer of shapes: {len(vertices)}\n")
            file.write(f"Average vertices: {average_vertices}\n")
            file.write(f"Average_faces: {average_faces}\n")
            file.write(f"Median vertices: {median_vertices} \n")
            file.write(f"Median faces: {median_faces}\n")
            file.write(f"Vertex Range: {min(vertices)} - {max(vertices)}\n")
            file.write(f"Face Range: {min(faces)} - {max(faces)}\n")
            file.write(f"Example average shape: \n {average_shape}\n")
            file.write(f"Example median shape: \n {median_shape}\n")
            file.write(f"Example simple shape: \n {simple_shape}\n")
            file.write(f"Example complex shape: \n {complex_shape}\n")
            file.write("\nOutliers:\n")
            file.write(f"High vertex outliers: {len(high_vertices)}\n")
            file.write(f"Low vertex outliers: {len(low_vertices)}\n")
            file.write(f"High face outliers: {len(high_faces)}\n")
            file.write(f"Low face outliers: {len(low_faces)}\n")

        self.plot_histogram(
            faces, 
            title="Distribution of Face Counts",
            xlabel = "Number of faces",
            save_path = folder + "\\face_histogram.png",
            average = average_faces,
            median = median_faces,
            )
        
        self.plot_histogram(
            vertices, 
            title="Distribution of Vertice Counts",
            xlabel = "Number of vertices",
            save_path = folder + "\\vertex_histogram.png",
            average = average_vertices,
            median = median_vertices
            )

        self.plot_histogram(
            classes, 
            title="Distribution of Shape Classes",
            xlabel = "Shape class",
            save_path = folder + "\\class_histogram.png",
            categorical = True
            )


