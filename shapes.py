import math
from structures import Object3D, Matrix
import data_handling

class Cube(Object3D):
    """ Cubes are constructed from the bottom left corner out to a defined size """
    def __init__(self, name, position, size, colour = 'grey'):
        Object3D.__init__(self, name, colour)
        cx, cy, cz = position
        self.add_points(Matrix([[x,y,z] for x in (cx, cx + size) for y in (cy, cy + size) for z in (cz, cz + size)]))
        self.add_lines([(n,n+4) for n in range(0,4)]+[(n,n+1) for n in range(0,8,2)]+[(n,n+2) for n in (0,1,4,5)])
        self.add_surfaces([(0,2,6,4), (1,3,7,5), (0,1,3,2), (5,4,6,7), (0,1,5,4), (3,2,6,7)])

class Quad(Object3D):
    """ Quads are constructed from the bottom left corner out to a defined size """
    def __init__(self, name, position, size_x, size_y, size_z, colour = 'grey'):
        Object3D.__init__(self, name, colour)
        cx, cy, cz = position
        self.add_points(Matrix([[x,y,z] for x in (cx, cx + size_x) for y in (cy, cy + size_y) for z in (cz, cz + size_z)]))
        self.add_lines([(n,n+4) for n in range(0,4)]+[(n,n+1) for n in range(0,8,2)]+[(n,n+2) for n in (0,1,4,5)])
        self.add_surfaces([(0,2,6,4), (1,3,7,5), (0,1,3,2), (5,4,6,7), (0,1,5,4), (3,2,6,7)])

class Plane(Object3D):
    """ Planes are constructed from the bottom left corner out to a defined size """
    def __init__(self, name, position, size_x, size_y, colour = 'grey'):
        Object3D.__init__(self, name, colour)
        cx, cy, cz = position
        self.add_points(Matrix([[x,y,0] for x in (cx, cx + size_x) for y in (cy, cy + size_y)]))
        self.add_lines([(0,1), (1,3), (2,3), (0,2)])
        self.add_surfaces([(0,1,3,2)])

class Polygon(Object3D):
    def __init__(self, name, position, no_points, size, colour = 'grey'):
        Object3D.__init__(self, name, colour)
        cx, cy, cz = position
        points = []
        for i in range(1,no_points + 1):
            x = (math.cos(2*math.pi / no_points * i) * size / no_points) + cx
            y = (math.sin(2*math.pi / no_points * i) * size / no_points) + cy
            cx, cy = x, y
            points.append([x,y,0])
        self.add_points(Matrix(points))
        self.add_lines([(n, (n + 1) % no_points) for n in range(0,no_points)])
        surfaces = []
        for i in range(0, no_points):
            surfaces.append(i)
        self.add_surfaces([surfaces])

class Sphere(Object3D):
    def __init__(self, name, position, radius, no_points, colour = 'grey'):
        Object3D.__init__(self, name, colour)
        cx, cy, cz = position
        points, lines, surfaces = [], [], []
        k = -1
        for i in range(no_points):
            lat = data_handling.map(i, 0, no_points, 0, math.pi)
            c = 0
            for j in range(no_points):
                lon = data_handling.map(j, 0, no_points, 0, 2 * math.pi)
                x = radius * math.sin(lon) * math.cos(lat) + cx
                y = radius * math.sin(lon) * math.sin(lat) + cy
                z = radius * math.cos(lon) + cz
                points.append([x,y,z])
                lines.append((j+k,j+k+1))
                if i+c+no_points < no_points ** 2:
                    lines.append((i+c, i+c+no_points))
                else:
                    if i+c+no_points == 0:
                        lines.append((i+c, 0))
                    else:
                        lines.append((i+c, no_points ** 2 % (i+c)))
                if i+c+no_points < no_points ** 2:
                    surfaces.append((i+c, i+1+c, (i+no_points+1+c) % no_points ** 2, i+no_points+c))
                else:
                    surfaces.append((i+c, (i+1+c) % no_points ** 2, no_points ** 2 % (i+c+1), no_points ** 2 % (i+c)))
                c += no_points
            k += no_points
        self.add_points(Matrix(points))
        self.add_lines(lines)
        self.add_surfaces(surfaces)

class GUILines(Object3D):
    def __init__(self, position, length, colour = 'grey'):
        Object3D.__init__(self, name = 'GUI_Line', colour = colour)
        self.add_points(Matrix([[position[0], position[1], position[2]], [position[0] + length, position[1], position[2]],
                                [position[0], position[1] + length, position[2]]]))
        self.add_lines([(0,1), (0,2)])