import math
import matrix_math as x_math

class Matrix():
    """ A matrix object that has zero based indexing"""
    def __init__(self, *args):
        """ Overloading to create a new matrix with specified dimension or initialise with a 2d array """
        if len(args) > 1:
            self.rows = args[0]
            self.cols = args[1]
            if len(args) > 2:
                self.matrix = [[args[2] for x in range(self.cols)] for y in range(self.rows)]
            else:
                self.matrix = [[0 for x in range(self.cols)] for y in range(self.rows)]
        elif len(args) == 1:
            self.rows = len(args[0])
            self.cols = len(args[0][0])
            self.matrix = args[0]
        else:
            print('ERROR: Invalid arguments provided when initialising matrix: ', args)

    def __iter__(self):
        for y in range(self.rows):
            yield self.matrix[y]

    def __len__(self):
        return self.rows

    def show(self):
        """ Displays the entire matrix and its dimension """
        print("Matrix: ", self.rows, "x", self.cols)
        for y in range(self.rows):
            for x in range(self.cols):
                print(self.matrix[y][x], " ", end="")
            print("")
    
    def no_rows(self):
        return self.rows
    
    def no_cols(self):
        return self.cols
    
    def access_index(self, y, x):
        return self.matrix[y][x]
    
    def set_index(self, y, x, value):
        self.matrix[y][x] = value
    
    def access_row(self, y):
        return self.matrix[y]
    
    def set_row(self, y, values):
        self.matrix[y] = values
    
    def matrix_to_point3d(self):
        if self.no_rows() > 2:
            point = Point3D((self.access_index(0,0), self.access_index(1,0), self.access_index(2,0)))
        else:
            point = Point3D((self.access_index(0,0), self.access_index(1,0), 0))
        return point    

class Point3D:
    def __init__(self, position):
          self.x = position[0]
          self.y = position[1]
          self.z = position[2]

    """ Converts a point to a matrix """
    def point3d_to_matrix(self):
        matrix = Matrix(3, 1)
        matrix.set_index(0, 0, self.x)
        matrix.set_index(1, 0, self.y)
        matrix.set_index(2, 0, self.z)
        return matrix

class Rotation3D(Point3D):
    def __init__(self, position):
        Point3D.__init__(self, position)
    
class Wireframe:
    def __init__(self, position):
        self.points = Matrix(0, 0)
        self.lines = []
        self.position = Point3D(position)
        self.centre = Point3D(position)

    def add_points(self, points):
        ones_column = Matrix(len(points), 1, 1)
        ones_added = x_math.h_stack(points, ones_column)
        self.points = ones_added
        #for point in points:
        #    self.points.append(Point3D(point))
        
    def add_lines(self, lines):
        self.lines += lines
        #for (start, end) in lines:
        #    self.lines.append(Line(self.points[start], self.points[end]))

    def show_points(self):
        for i, (x, y, z) in enumerate(self.points):
            print('{}: ({}, {}, {})'.format(i, x, y, z))

    def show_lines(self):
        for i, (node_1, node_2) in enumerate(self.lines):
            print('{}: {} to {}'.format(i, node_1, node_2))
    
    def translate(self, translation):
        for point in self.points:
            for axis_no, axis in enumerate(['x', 'y', 'z']):
                point[axis_no] += getattr(translation, axis)

    def scale(self, scale_factor, anchor = None): # Anchor is a point object which stores the point to scale from
        """ Scales the object from an arbetrary point """
        if anchor == None:
            # If no anchor is provided, scale from objects centre
            anchor = self.find_centre()
        for point in self.points:
            point[0] = anchor.x + scale_factor * (point[0] - anchor.x)
            point[1] = anchor.y + scale_factor * (point[1] - anchor.y)
            point[2] *= scale_factor

    def find_centre(self):
        x = sum([point[0] for point in self.points]) / len(self.points)
        y = sum([point[1] for point in self.points]) / len(self.points)
        z = sum([point[2] for point in self.points]) / len(self.points)
        return Point3D((x, y, z))

    def _rotate_z(self, anchor, z_rotation):        
        for point in self.points:
            x = point[0] - anchor.x
            y = point[1] - anchor.y
            hypot = math.hypot(y, x)
            new_z_rotation  = math.atan2(y, x) + z_rotation
            point[0] = anchor.x + hypot * math.cos(new_z_rotation)
            point[1] = anchor.y + hypot * math.sin(new_z_rotation)

    def _rotate_x(self, anchor, x_rotation):        
        for point in self.points:
            y = point[1] - anchor.y
            z = point[2] - anchor.z
            hypot = math.hypot(y, z)
            new_x_rotation  = math.atan2(y, z) + x_rotation
            point[2] = anchor.z + hypot * math.cos(new_x_rotation)
            point[1] = anchor.y + hypot * math.sin(new_x_rotation)

    def _rotate_y(self, anchor, y_rotation):        
        for point in self.points:
            x = point[0] - anchor.x
            z = point[2] - anchor.z
            hypot = math.hypot(x, z)
            new_y_rotation  = math.atan2(x, z) + y_rotation
            point[2] = anchor.z + hypot * math.cos(new_y_rotation)
            point[0] = anchor.x + hypot * math.sin(new_y_rotation)

    def rotate(self, anchor, rotation):
        self._rotate_x(anchor, rotation.x)
        self._rotate_y(anchor, rotation.y)
        self._rotate_z(anchor, rotation.z)