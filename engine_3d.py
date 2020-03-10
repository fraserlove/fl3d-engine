import matrix_math

class Engine3D:
    def __init__(self, projection_type = 'orthographic', projection_anchor = (0, 0, 0, 0)):
        self.objects = {}
        self.translation_lines = None

        self.rendered_translation_lines = []
        self.rendered_points = [[]]

        self.projection_type = projection_type
        self.projection_anchor = projection_anchor
    
    def add_object(self, object_3d):
        self.objects[object_3d.name] = object_3d
        object_3d.project(self.projection_type, self.projection_anchor)

    def set_translation_lines(self, translation_lines):
        self.translation_lines = translation_lines
        translation_lines.projected = translation_lines.points

    def translate(self, dx, dy, dz, entities = None):
        if entities == None:
            for object_3d in self.objects.values():
                object_3d.translate((dx, dy, dz))
                object_3d.project(self.projection_type, self.projection_anchor)
        else:
            for object_3d in entities:
                self.objects[object_3d].translate((dx, dy, dz))
                self.objects[object_3d].project(self.projection_type, self.projection_anchor)
        if self.translation_lines != None:
            self.translation_lines.translate((dx, dy, dz))
            self.translation_lines.projected = self.translation_lines.points

    def scale(self, kx, ky, kz, anchor = None, entities = None):
        if anchor == None:
            anchor = self.entities_centre()

        if entities == None:
            for object_3d in self.objects.values():
                object_3d.scale((kx, ky, kz), anchor)
                object_3d.project(self.projection_type, self.projection_anchor)
        else:
            for object_3d in entities:
                self.objects[object_3d].scale((kx, ky, kz), anchor)
                self.objects[object_3d].project(self.projection_type, self.projection_anchor)
        if self.translation_lines != None:
            self.translation_lines.scale((kx, ky, kz), anchor)
            self.translation_lines.projected = self.translation_lines.points

    def rotate(self, rx, ry, rz, anchor = None, entities = None):
        if anchor == None:
            anchor = self.entities_centre()

        if entities == None:
            for object_3d in self.objects.values():
                object_3d.rotate((rx, ry, rz), anchor)
                object_3d.project(self.projection_type, self.projection_anchor)
        else:
            anchor = self.entities_centre(entities)
            for object_3d in entities:
                self.objects[object_3d].rotate((rx, ry, rz), anchor)
                self.objects[object_3d].project(self.projection_type, self.projection_anchor)
        if self.translation_lines != None:
            self.translation_lines.rotate((rx, ry, rz), anchor)
            self.translation_lines.projected = self.translation_lines.points
    
    def entities_centre(self, entities = None):
        centre = (0, 0, 0, 0)
        if entities == None:
            entities = self.objects.keys()

        total_x, total_y, total_z, no_points = 0, 0, 0, 0
        for object_3d in entities:
            total_x += self.objects[object_3d].sum_x()
            total_y += self.objects[object_3d].sum_y()
            total_z += self.objects[object_3d].sum_z()
            no_points += self.objects[object_3d].no_points()
        if no_points > 0:
           centre = (total_x / no_points, total_y / no_points, total_z / no_points, 0)
        return centre

    def order_objects(self):
        for i in range(len(self.objects)):
            current = self.objects[list(self.objects.keys())[i]]
            index = i
            while index > 0 and self.objects[list(self.objects.keys())[index-1]].find_centre()[2] > current.find_centre()[2]:
                self.objects[list(self.objects.keys())[index]] = self.objects[list(self.objects.keys())[index - 1]]
                index -= 1
            self.objects[list(self.objects.keys())[index]] = current
        return self.objects

    def clear_all_objects(self):
        self.objects = {}

    def clear_rendered_points(self):
        self.rendered_points = []

    def clear_translation_lines(self):
        self.translation_lines = None
    
    def get_translation_lines(self):
        return self.translation_lines
