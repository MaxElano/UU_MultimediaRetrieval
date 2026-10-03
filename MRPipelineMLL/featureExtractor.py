import numpy as np
import os
import open3d as o3d

class feature_Extractor():
    def __init__(self):
        pass

    # extracts from a given database and stores them in two numpy arrays
    def extract_features_from_database(self, directory ="Data\\SmallShapeDatabase"):
        index = 0
        feature_list = []
        metadata_list = []
        for shape_class in os.listdir(directory):
            class_folder = os.path.join(directory, shape_class)
            if not os.path.isdir(class_folder):
                continue

            for file_name in os.listdir(class_folder):
                if not file_name.lower().endswith(".obj"):
                    continue

                metadata_list.append(np.array([index, file_name, shape_class]))

                file_path = os.path.join(class_folder, file_name)
                mesh = o3d.io.read_triangle_mesh(file_path)

                feature_list.append(self.extract_features(mesh, index))

                index += 1
                
        # saves both databases as numpy arrays in a file
        np.save("Data\\DataAnalysis\\metaDatabase.npy", metadata_list)
        np.save("Data\\DataAnalysis\\featureDatabase.npy", feature_list)


    # extracts all features of an objects and saves them as tuple
    def extract_features(self, mesh, index):
        vertices = np.asarray(mesh.vertices)
        triangles = np.asarray(mesh.triangles)
        # DEFINE OTHER MESH DESCRIPTORS HERE


        vol = self.volume(triangles, vertices)
        surf = self.surface_area(mesh)
        cmp = self.compactness(surf, vol)
        sph = self.sphericity(cmp)

        # for Assignment:
        # surface area, compactness, 3D rectangularity, diameter, convexity, eccentricity 
        return np.array([index, surf, cmp,])

   
    def volume(self, triangles, vertices):
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

    def centroid(self):
        return 0
    
    # shape volume divided by OBB volume
    def rectangularity(self):
        return 0

    def diameter(self):
        return 0

    # ratio of largest to smallest eigenvalues of covariance matrix
    def eccentricity(self):
        return 0

    # shape volume divided by convex hull volume
    def convexity(self):
        return 0

fe = feature_Extractor()

'''
mesh = o3d.io.read_triangle_mesh("Data\\SmallShapeDatabase\\Cup\\m500.obj")
vertices = np.asarray(mesh.vertices)
triangles = np.asarray(mesh.triangles)

print(fe.volume(triangles, vertices))
print(mesh.get_volume())
'''
fe.extract_features_from_database()

#print(np.load("Data\\DataAnalysis\\metaDatabase.npy"))