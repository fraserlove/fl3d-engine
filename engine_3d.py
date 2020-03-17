import time

import matrix_math

class Engine3D:
    def __init__(self, projection_type = 'orthographic', projection_anchor = (0, 0, 0, 0)):
        self.objects = {}
        self.translation_lines = None
        self._performing_operations = False
        self._last_operation_time = time.time()
        self.operation_delay = 0.4 # The minimum time between operations allowed to show the translation lines in seconds

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
        self._performing_operations = True
        self._last_operation_time = time.time()
        if entities == None:
            for object_3d in self.objects.values():
                object_3d.translate((dx, dy, dz))
                object_3d.project(self.projection_type, self.projection_anchor)
        else:
            for object_3d in entities:
                self.objects[object_3d].translate((dx, dy, dz))
                self.objects[object_3d].project(self.projection_type, self.projection_anchor)

    def scale(self, kx, ky, kz, anchor = None, entities = None):
        self._performing_operations = True
        self._last_operation_time = time.time()
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

    def rotate(self, rx, ry, rz, anchor = None, entities = None):
        self._performing_operations = True
        self._last_operation_time = time.time()
        if anchor == None:
            anchor = self.entities_centre()

        if entities == None:
            for object_3d in self.objects.values():
                object_3d.rotate((rx, ry, rz), anchor)
                object_3d.project(self.projection_type, self.projection_anchor)
        else:
            for object_3d in entities:
                self.objects[object_3d].rotate((rx, ry, rz), anchor)
                self.objects[object_3d].project(self.projection_type, self.projection_anchor)
    
    def entities_centre(self, entities = None):
        centre = (0, 0, 0, 0)
        if entities == None:
            entities = self.objects.keys()

        total_x, total_y, total_z, no_points = 0, 0, 0, 0
        for object_3d in entities:
            total_x += self.objects[object_3d].sum_x()
            total_y += self.objects[object_3d].sum_y()
            total_z += self.objects[object_3d].sum_z()
            no_points += self.objects[object_3d].point_count()
        if no_points > 0:
           centre = (total_x / no_points, total_y / no_points, total_z / no_points, 0)
        return centre

    def order_objects(self):
        ordered_objects = self.objects.copy()
        for i in range(len(ordered_objects)):
            current = ordered_objects[list(ordered_objects.keys())[i]]
            index = i
            while index > 0 and ordered_objects[list(ordered_objects.keys())[index-1]].find_centre()[2] > current.find_centre()[2]:
                ordered_objects[list(ordered_objects.keys())[index]] = ordered_objects[list(ordered_objects.keys())[index - 1]]
                index -= 1
            ordered_objects[list(ordered_objects.keys())[index]] = current
        return ordered_objects

    def clear_all_objects(self):
        self.objects = {}
        self.clear_translation_lines()
        self.clear_rendered_points()

    def remove_object(self, object_name, engine_client):
        if engine_client.chosen_point != None:
            if engine_client.chosen_point[2].points.access_row(engine_client.chosen_point[3]) in self.objects[object_name].points.access_matrix():
                self.clear_translation_lines()
                self.clear_rendered_points()
        if engine_client.chosen_rotation_anchor != None:
            if len(self.objects) == 1: # If the object being deleted is the last object then remove the rotation point
                self.clear_translation_lines()
                self.clear_rendered_points()
        del self.objects[object_name]

    def clear_rendered_points(self):
        self.rendered_points = []

    def clear_translation_lines(self):
        self.translation_lines = None
    
    def get_translation_lines(self):
        return self.translation_lines

    def performing_operations(self):
        return self._performing_operations

    def update_operating_status(self, status):
        self._performing_operations = status

    def acceptable_operation_period(self):
        return True if time.time() - self._last_operation_time > self.operation_delay else False