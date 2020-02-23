class Engine3D:
    def __init__(self):
        self.entities = {}
    
    def add_object(self, name, entity):
        self.entities[name] = entity

    def translate_all(self, translation):
        for entity in self.entities.values():
            entity.translate(translation)

    def scale_all(self, scale_factor, anchor = None):
        for entity in self.entities.values():
            entity.scale(scale_factor, anchor)

    def rotate_all(self, rotation):
        for entity in self.entities.values():
            entity.centre = entity.find_centre()
            entity.rotate(entity.centre, rotation)