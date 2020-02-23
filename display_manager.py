import pygame, sys
from engine_3d import Engine3D
from structures import Point3D, Rotation3D
from shapes import Cube

class DisplayManager():
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.centre = Point3D((width / 2, height / 2, 0))
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption('3D Graphics Engine')

        self.display_points = True
        self.display_lines = True

        self.line_colour = (255, 255, 255)
        self.node_colour = (255, 255, 255)
        self.bg_colour = (30, 30, 30)
        self.point_radius = 2

        self.controls = {
        pygame.K_LEFT: (lambda self, engine: self.engine.translate_all(Point3D((-10, 0, 0)))),
        pygame.K_RIGHT: (lambda self, engine: self.engine.translate_all(Point3D((10, 0, 0)))),
        pygame.K_DOWN: (lambda self, engine: self.engine.translate_all(Point3D((0, 10, 0)))),
        pygame.K_UP: (lambda self, engine: self.engine.translate_all(Point3D((0, -10, 0)))),
        pygame.K_EQUALS: (lambda self, engine: self.engine.scale_all(1.25 , self.centre)),
        pygame.K_MINUS: (lambda self, engine: self.engine.scale_all(0.75, self.centre)),
        pygame.K_q: (lambda self, engine: self.engine.rotate_all(Rotation3D((0.1, 0, 0)))),
        pygame.K_w: (lambda self, engine: self.engine.rotate_all(Rotation3D((-0.1, 0, 0)))),
        pygame.K_a: (lambda self, engine: self.engine.rotate_all(Rotation3D((0, 0.1, 0)))),
        pygame.K_s: (lambda self, engine: self.engine.rotate_all(Rotation3D((0, -0.1, 0)))),
        pygame.K_z: (lambda self, engine: self.engine.rotate_all(Rotation3D((0, 0, 0.1)))),
        pygame.K_x: (lambda self, engine: self.engine.rotate_all(Rotation3D((0, 0, -0.1)))),
        }

        self.engine = Engine3D()

        self.instantiate_entities()

    def instantiate_entities(self):
        self.engine.add_object('cube1', Cube((775, 425, 0), 50))
        self.engine.add_object('cube2', Cube((750, 400, 0), 100))
    
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in self.controls:
                        self.controls[event.key](self, self.engine)
            self.display()
            pygame.display.flip()
    
    def display(self):
        self.screen.fill(self.bg_colour)
        for entity in self.engine.entities.values():
            if self.display_lines:
                for point_1, point_2 in entity.lines:
                    pygame.draw.aaline(self.screen, self.line_colour, entity.points.access_row(point_1)[:2], entity.points.access_row(point_2)[:2], 1)

            if self.display_points:
                for point in entity.points:
                    pygame.draw.circle(self.screen, self.line_colour, (int(point[0]), int(point[1])), self.point_radius, 0)

display = DisplayManager(1600, 900)

display.run()