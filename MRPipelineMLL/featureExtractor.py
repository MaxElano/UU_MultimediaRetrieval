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
        convex_hull, _ = mesh.compute_convex_hull()
        obb = convex_hull.get_axis_aligned_bounding_box() #we can use axis aligned here bc of normalization step

        vol = self.volume(vertices, triangles)
        surf = self.surface_area(mesh)
        cmp = self.compactness(surf, vol)
        sph = self.sphericity(cmp)
        centr = self.centroid(vertices)
        rect = self.rectangularity(vol, obb)
        dm = self.diameter(convex_hull)
        conv = self.convexity(vol, convex_hull)
        ecc = self.eccentricity(obb)

        # for Assignment:
        # surface area, compactness, 3D rectangularity, diameter, convexity, eccentricity 
        return np.array([index, surf, cmp, rect, dm, conv, ecc])

   
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

fe = feature_Extractor()

fe.extract_features_from_database()

print(np.load("Data\\DataAnalysis\\featureDatabase.npy"))


