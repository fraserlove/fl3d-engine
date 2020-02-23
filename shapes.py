from structures import Wireframe, Matrix

class Cube(Wireframe):
    def __init__(self, position, size):
        Wireframe.__init__(self, position)
        self.add_points(Matrix([[x,y,z] for x in (position[0], position[0] + size) for y in (position[1], position[1] + size) for z in (position[2], position[2] + size)]))
        self.add_lines([(n,n+4) for n in range(0,4)]+[(n,n+1) for n in range(0,8,2)]+[(n,n+2) for n in (0,1,4,5)])