import sys
import os
sys.path.insert(0, os.getcwd() + "\\MRPipelineMLL") # location of src 

import numpy as np
import Utility.config as config
import Utility.utility as util
import Utility.distanceFunctions as distFunc
from renderer import RenderMode
import time
import random
import math


class FeatureExtractor():
    def __init__(self):
        config.initialize()

    # extracts from a given database and stores them in two numpy arrays
    def extract_features_from_database(self, directory ="Data\\NormalizedShapeDatabase"):
        index = 0
        feature_list = []
        metadata_list = []
        a3_list = []
        d1_list = []
        d2_list = []
        d3_list = []
        d4_list = []

        start = time.time()
        all_files = util.get_all_files(directory)

        for file in all_files:
            _, shape_class, file_name = file
            mesh = config.ml.load_mesh(util.get_path(file))

            metadata_list.append(np.array([index, file_name, shape_class]))
            feature_list.append(self.extract_global_features(mesh, index))

            a3, d1, d2, d3, d4 = self.extract_distribution_features(mesh, index)
            a3_list.append(a3)
            d1_list.append(d1)
            d2_list.append(d2)
            d3_list.append(d3)
            d4_list.append(d4)

            index += 1
   
        # saves meta and feature databases as numpy arrays in a seperate file
        util.save_numpy_file("Data\\DataAnalysis\\featureDatabases.npz", metadata=metadata_list, features=feature_list)

        # save all distributions in one file
        util.save_numpy_file("Data\\DataAnalysis\\distributionDatabases.npz", 
                             A3=a3_list, D1=d1_list, D2=d2_list, D3=d3_list, D4=d4_list)

        end = time.time()
        config.lg.log(f"Finished feature extraction for {index} objects in {round(((end-start)) / 60, 2) } minutes")
      
    # extracts all features of an objects and saves them as tuple
    def extract_global_features(self, mesh, index):
        vertices = np.asarray(mesh.vertices)
        triangles = np.asarray(mesh.triangles)
        convex_hull, _ = mesh.compute_convex_hull()
        obb = convex_hull.get_axis_aligned_bounding_box() #we can use axis aligned here bc of normalization step

        vol = self.volume(vertices, triangles)
        surf = self.surface_area(mesh)
        cmp = self.compactness(surf, vol)
        rect = self.rectangularity(vol, obb)
        dm = self.diameter(convex_hull)
        conv = self.convexity(vol, convex_hull)
        ecc = self.eccentricity(obb)
        sph = self.sphericity(cmp)
        #centr = self.centroid(vertices)        

        # for Assignment:
        # surface area, sphericity, 3D rectangularity, diameter, convexity, eccentricity 
        return np.array([index, surf, sph, rect, dm, conv, ecc])

    def extract_distribution_features(self, mesh, index, samples = 10000, bins = 20):
        vertices = np.asarray(mesh.vertices)
        A3 = np.append(index, self.A3(vertices, samples, bins))
        D1 = np.append(index, self.D1(vertices, samples, bins))
        D2 = np.append(index, self.D2(vertices, samples, bins))   
        D3 = np.append(index, self.D3(vertices, samples, bins))
        D4 = np.append(index, self.D4(vertices, samples, bins))       
        
        return A3, D1, D2, D3, D4

    # angle between 3 random vertices
    def A3(self, vertices, samples, bins):
        angles = []
        k = math.ceil(pow(samples, 1.0/3.0))
        for a in range(k):
            va = random.choice(vertices)
            for b in range(k):
                vb = random.choice(vertices)
                if np.array_equal(va, vb):          # do not allow duplicates
                    continue
                for c in range(k):
                    vc = random.choice(vertices)
                    if np.array_equal(va, vc) or np.array_equal(vb, vc):          # do not allow duplicates
                        continue
                    v1 = va -vb
                    v2 = vc -vb
                    v1_u = v1 / np.linalg.norm(v1)
                    v2_u = v2 / np.linalg.norm(v2)
                    # adds angle in radians, for degrees use np.degrees(angle)
                    angles.append(np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0)))            
        return self.distribute_values(angles, bins)
    
    # distance between barycenter and random vertex
    def D1(self, vertices, samples, bins):
        rvs = []
        for i in range(samples):
            rvs.append(random.choice(vertices))
        distances = np.linalg.norm(rvs, axis=1)
        return self.distribute_values(distances, bins)

    # distance between 2 random vertices
    def D2(self, vertices, samples, bins):
        vectors = []
        k = int(pow(samples, 1.0/2.0))  #compute number of samples along 2 dimensions
        for a in range(k):
            va = random.choice(vertices)
            for b in range(k):
                vb = random.choice(vertices)
                if np.array_equal(va, vb):          # do not allow duplicates
                    continue
                vectors.append(va - vb)
        distances = np.linalg.norm(vectors, axis=1)
        return self.distribute_values(distances, bins)

    # square root of area of triangle given by 3 random vertices
    def D3(self, vertices, samples, bins):
        normals = []
        k = math.ceil(pow(samples, 1.0/3.0))
        for a in range(k):
            va = random.choice(vertices)
            for b in range(k):
                vb = random.choice(vertices)
                if np.array_equal(va, vb):          # do not allow duplicates
                    continue
                for c in range(k):
                    vc = random.choice(vertices)
                    if np.array_equal(va, vc) or np.array_equal(vb, vc):          # do not allow duplicates
                        continue
                    v1 = va -vb
                    v2 = vc -vb
                    normals.append(np.cross(v1, v2))
        areas = np.linalg.norm(normals, axis=1) / 2
        return self.distribute_values(np.sqrt(areas), bins)

    # cube root of volume of tetrahedron formed by 4 random vertices 
    def D4(self, vertices, samples, bins):
        volumes = []
        k = int(pow(samples, 1.0/4.0))
        for a in range(k):
            va = random.choice(vertices)
            for b in range(k):
                vb = random.choice(vertices)
                if np.array_equal(va, vb):          # do not allow duplicates
                    continue
                for c in range(k):
                    vc = random.choice(vertices)
                    if np.array_equal(va, vc) or np.array_equal(vb, vc):       
                        continue
                    for d in range(k):
                        vd = random.choice(vertices)
                        if np.array_equal(va, vd) or np.array_equal(vb, vd) or np.array_equal(vc, vd):   
                            continue
                        # vertices of base triangle, translated by last point so its at
                        v1 = vb-va
                        v2 = vc-va
                        v3 = vd-va
                        volumes.append(np.dot(np.cross(v1, v2), v3)/6)
        return self.distribute_values(np.cbrt(volumes), bins)

    # returns the specified amount of unique vertices
    def random_vertices(self, vertices, amount):
        indices = random.sample(range(len(vertices)), amount)
        results = []
        for i in indices:
            results.append(vertices[i])
        return results
  
    def distribute_values(self, values, bin_amount):
        hist, _ = np.histogram(values, bins=bin_amount)
        return hist
    
    def volume(self, vertices, triangles):
        vol = 0
        for t in triangles:
            p1, p2, p3 = t
            vol += np.dot(np.cross(vertices[p1], vertices[p2]), vertices[p3])/6
        return np.absolute(vol)

    def surface_area(self, mesh):
        return mesh.get_surface_area()
    
    # Surface^3/(36*pi*Vol^2); how close is the shape to a sphere
    def compactness(self, surface, volume):
        return pow(surface, 3)/(36*np.pi*pow(volume, 2))

    def sphericity(self, compactness):
        return 1/compactness

    def centroid(self, vertices):
        cnt = 0
        vertex_sum = np.array([0, 0, 0])
        for vertex in vertices:
            vertex_sum = np.add(vertex_sum, vertex)
            cnt += 1
        return vertex_sum/cnt
    
    # shape volume divided by OBB volume
    def rectangularity(self, vol, obb):
        return vol/(obb.volume())

    def diameter(self, convex_hull):
        longest_dist = 0
        vertices = convex_hull.vertices
        for v1 in vertices:
            for v2 in vertices:
                dist = np.absolute(np.linalg.norm(v1 - v2))
                if dist > longest_dist:
                    longest_dist = dist
        return longest_dist

    # ratio of largest to smallest eigenvalues of covariance matrix
    def eccentricity(self, obb):
        eigenvalues = obb.get_extent()
        return np.max(eigenvalues)/np.min(eigenvalues)

    # shape volume divided by convex hull volume
    def convexity(self, vol, convex_hull):
        ch_vol = self.volume(np.asarray(convex_hull.vertices), np.asarray(convex_hull.triangles))
        return vol/ch_vol

    # function to showcase convex hull
    def render_convex_hull(self, meshpath):
        config.initialize()
        mesh = config.ml.load_mesh(meshpath)
        convex_hull, _ = mesh.compute_convex_hull()
        print(mesh)
        print(convex_hull)

        # Render mesh
        config.rd.set_render_mode(RenderMode.NORMAL)
        #config.rd.show_world_axis(True)
        config.rd.add_mesh(mesh, meshpath)
        config.rd.add_mesh(convex_hull.translate((2, 0, 0)), meshpath)
        config.rd.launch_renderer()

    # returns all features for a given mesh, if available in database with correct index, else newly calculated with index -1
    # DOES NOT WORK WITH NEW TYPE OF SAVING YET
    def retrieve_features(self, meshpath, filename):
        config.initialize()
        mesh = config.ml.load_mesh(meshpath)
        features = np.load("Data\\DataAnalysis\\featureDatabase.npy")
        meta_data = np.load("Data\\DataAnalysis\\metaDatabase.npy")
        #distributions = np.load("Data\\DataAnalysis\\metaDatabase.npz")

        mesh_index = self.get_mesh_index(filename, meta_data)
        if mesh_index < 0:
            features = self.extract_global_features(mesh, -1)
            #distributions = self.extract_distribution_features(mesh, -1) #??? Does nothing no? At least assigning
        else: 
            features = features[mesh_index]

        return mesh, features

    def get_mesh_index(self, filename, meta_data):
        for row in meta_data:
            if row[1] == filename:
                print(row)
                return int(row[0])
        return -1

    # Extremely heavy function cuz of nr_meshes * nr_meshes * nr_feat
    def compute_feature_weights(self, all_global_features, all_distribution_features):
        nr_of_global_features = all_global_features.shape[1]
        nr_of_shapes = all_global_features.shape[0]

        for i in range(nr_of_shapes):
            for j in i + range(nr_of_shapes - i - 1) + 1: #Only need half of 2d table, cuz d(a,b) == d(b,a)
                for f in range(nr_of_global_features):
                    dist = distFunc.get_euclidean_distance(all_global_features[i,f], all_global_features[j,f])
                #calc_dist(i, j)

        return 

    def compute_variance

# config.initialize(skip_renderer=True)    
# fe = FeatureExtractor()
# fe.extract_features_from_database()
