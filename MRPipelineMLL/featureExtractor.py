import numpy as np
import os
import open3d as o3d
import config
from renderer import render_mode
import utility as util
import time
import random

class feature_Extractor():
    def __init__(self):
        config.initialize()

    # extracts from a given database and stores them in two numpy arrays
    def extract_features_from_database(self, directory ="Data\\NormalizedShapeDatabase"):
        index = 0
        feature_list = []
        metadata_list = []
        A3 = D1 = D2 = D3 = D4 = []

        start = time.time()
        all_files = util.get_all_files(directory)

        for file in all_files:
            _, shape_class, file_name = file
            mesh = config.ml.load_mesh(util.get_path(file))

            #metadata_list.append(np.array([index, file_name, shape_class]))
            #feature_list.append(self.extract_global_features(mesh, index))


            index += 1
   
        # saves both databases as numpy arrays in a file
        np.save("Data\\DataAnalysis\\metaDatabase.npy", metadata_list)
        np.save("Data\\DataAnalysis\\featureDatabase.npy", feature_list)
        #util.save_numpy_file("Data\\DataAnalysis\\distributionDatabases.npy", )

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
        #sph = self.sphericity(cmp)
        #centr = self.centroid(vertices)        

        # for Assignment:
        # surface area, compactness, 3D rectangularity, diameter, convexity, eccentricity 
        return np.array([index, surf, cmp, rect, dm, conv, ecc])

    def extract_distribution_features(self, mesh, index, samples = 10000, bins = 10):
        vertices = np.asarray(mesh.vertices)
        A3 = np.append(index, self.A3(vertices, samples, bins))
        '''
        D1 = self.D1(vertices)
        D2 = self.D2(vertices)
        D3 = self.D3(vertices)
        D4 = self.D4(vertices)        
        '''

        return A3

    # angle between 3 random vertices
    def A3(self, vertices, samples, bins):
        angles = []
        for i in range(samples):
            random_vertices = self.random_vertices(vertices, 3)
            v1 = random_vertices[0] -random_vertices[1]
            v2 = random_vertices[2] -random_vertices[1]
            v1_u = v1 / np.linalg.norm(v1)
            v2_u = v2 / np.linalg.norm(v2)
            # adds angle in radians, for degrees use np.degrees(angle)
            angles.append(np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0)))
        return self.distribute_values(angles, bins)
    
    # distance between barycenter and random vertex
    def D1(self, vertices, samples, bins):
        pass
    # distance between 2 random vertices
    def D2(self, vertices, samples, bins):
        
        pass
    # square root of area of triangle given by 3 random vertices
    def D3(self, vertices, samples, bins):
        pass
    # cube root of volume of tetrahedron formed by 4 random vertices 
    def D4(self, vertices, samples, bins):
        pass

    # returns the specified amount of unique vertices
    def random_vertices(self, vertices, amount):
        indices = random.sample(range(0, len(vertices)), amount)
        results = []
        for i in indices:
            results.append(vertices[i])
        return results

    def distribute_values(self, values, bin_amount):
        hist, bins = np.histogram(values, bins=bin_amount)
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
        config.rd.set_render_mode(render_mode.NORMAL)
        #config.rd.show_world_axis(True)
        config.rd.add_mesh(mesh, meshpath)
        config.rd.add_mesh(convex_hull.translate((2, 0, 0)), meshpath)
        config.rd.launch_renderer()

    # returns all features for a given mesh, if available in database with correct index, else newly calculated with index -1
    def retrieve_features(self, meshpath, filename):
        config.initialize()
        mesh = config.ml.load_mesh(meshpath)
        features = np.load("Data\\DataAnalysis\\featureDatabase.npy")
        meta_data = np.load("Data\\DataAnalysis\\metaDatabase.npy")

        mesh_index = self.get_mesh_index(filename, meta_data)
        if mesh_index < 0:
            features = self.extract_features(mesh, -1)
        else:
            features = features[mesh_index]

        return mesh, features

    def get_mesh_index(self, filename, meta_data):
        for row in meta_data:
            if row[1] == filename:
                print(row)
                return int(row[0])
        return -1

    
        

fe = feature_Extractor()

mesh = config.ml.load_mesh("Data\\NormalizedShapeDatabase\\Quadruped\\m94.npz")
vertices = np.asarray(mesh.vertices)

print(fe.extract_distribution_features(mesh, -1, 1000))
#print(fe.A3(vertices, 100, 5))


#fe.extract_features_from_database()
#print(np.load("Data\\DataAnalysis\\featureDatabase.npy"))
#print(np.load("Data\\DataAnalysis\\metaDatabase.npy"))

#_, row = fe.retrieve_features("Data\\NormalizedShapeDatabase\\AquaticAnimal\\m57.obj", '57.obj')
#print(row)
#fe.extract_features_from_database()
#print(fe.retrieve_features("Data\\SmallShapeDatabase\\Mug\\D00172.obj", 'D00172.obj'))

