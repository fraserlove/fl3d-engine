import pygame, sys, os, tkinter
from PIL import Image, ImageTk

from engine_3d import Engine3D
from shapes import Cube, Quad, Plane, Polygon, Sphere
from database_manager import DatabaseManager
import data_handling

""" For rotation of all objects use self.viewer_centre to spin all objects """
""" For individual rotation of one ore multiple objects use objects = [] in engine.rotate() with array of object lables """
""" For combined spin over multiple objects use objects = [] in engine.rotate() with array of object lables """

""" Add UI with options, add optional grid to screen """
""" Add ablity to click on points and enter new values """
""" Clean up lighting wrt moving objects to top of screen increasing contrast """
""" Login system """
""" Add ability to change object rotation and direction using clicking on objects """
""" Add ability to change object rotation anchor point """
""" Add ability to add objects from GUI, (click and drag) and set values """

class Camera():
    def __init__(self, translation_factor, scaling_factor, rotation_factor):
        self.controls = {
            pygame.K_LEFT: (lambda self, engine, db_manager: self.engine.translate(-translation_factor, 0, 0)),
            pygame.K_RIGHT: (lambda self, engine, db_manager: self.engine.translate(translation_factor, 0, 0)),
            pygame.K_DOWN: (lambda self, engine, db_manager: self.engine.translate(0, translation_factor, 0)),
            pygame.K_UP: (lambda self, engine, db_manager: self.engine.translate(0, -translation_factor, 0)),
            pygame.K_EQUALS: (lambda self, engine, db_manager: self.engine.scale(scaling_factor, scaling_factor, scaling_factor, self.viewer_centre)),
            pygame.K_MINUS: (lambda self, engine, db_manager: self.engine.scale(2 - scaling_factor, 2 - scaling_factor, 2 - scaling_factor, self.viewer_centre)),
            pygame.K_q: (lambda self, engine, db_manager: self.engine.rotate(rotation_factor, 0, 0)),
            pygame.K_w: (lambda self, engine, db_manager: self.engine.rotate(-rotation_factor, 0, 0)),
            pygame.K_a: (lambda self, engine, db_manager: self.engine.rotate(0, rotation_factor, 0)),
            pygame.K_s: (lambda self, engine, db_manager: self.engine.rotate(0, -rotation_factor, 0)),
            pygame.K_z: (lambda self, engine, db_manager: self.engine.rotate(0, 0, rotation_factor)),
            pygame.K_x: (lambda self, engine, db_manager: self.engine.rotate(0, 0, -rotation_factor)),
            pygame.K_SPACE: (lambda self, engine, db_manager: self.db_manager.save_objects(self.engine.objects)),
            }

class DisplayManager():
    def __init__(self, width, height):
        self.control_width = 250
        self.control_height = height
        self.details_width = width - self.control_width
        self.details_height = 150
        self.viewer_width = width - self.control_width
        self.viewer_height = height - self.details_height
        self.viewer_centre = (self.viewer_width / 2, self.viewer_height / 2, 0, 0)

        self.gui_bg_colour = '#1e1e1e'

        self.root = tkinter.Tk()
        self.root.title('FL3D Engine')
        self.control = tkinter.Frame(self.root, bg = self.gui_bg_colour, width = self.control_width, height = self.control_height)
        self.control.pack(side = 'right')
        self.viewer = tkinter.Frame(self.root, width = self.viewer_width, height = self.viewer_height)
        self.viewer.pack(side = 'top')
        self.details = tkinter.Frame(self.root, bg = self.gui_bg_colour, width = self.details_width, height = self.details_height)
        self.details.pack(side = 'bottom')

        os.environ['SDL_WINDOWID'] = str(self.viewer.winfo_id())
        os.environ['SDL_VIDEODRIVER'] = 'windib'

        self.display_surfaces = True
        self.display_points = False
        self.display_lines = False
        self.debug_mode = False
        self.hidden_lines = False # Display lines within overlapping objects
        self.per_surface_alpha = False # Display alpha over a surface or object basis
        self.load_objects = False
        self.create_objects = True

        self.line_colour = (255, 255, 255)
        self.point_colour = (255, 255, 255)
        self.bg_colour = (40, 40, 40)
        self.fps_colour = (255, 255, 255)
        self.surface_alpha = 255
        self.point_radius = 2
        self.lighting_factor = 1.25 # Controls the contrast of colour in objects, higher means more contrast
        self.rotation_factor = 0.1
        self.translation_factor = 25
        self.scaling_factor = 1.1
        self.movement_factor = 25
        self.max_frame_rate = 1000
        self.max_render_distance = 1
        self.min_render_distance = 10000

        pygame.init()
        self.screen = pygame.display.set_mode((self.viewer_width, self.viewer_height))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font('fonts/Montserrat-SemiBold.ttf', 16)
        pygame.key.set_repeat(1, self.movement_factor)
        self.logo = pygame.image.load('FL3D_small.png')
        self.logo_size = (197, 70)

        self.camera = Camera(self.translation_factor, self.scaling_factor, self.rotation_factor)
        self.engine = Engine3D('orthographic', self.viewer_centre)
        self.db_manager = DatabaseManager('ObjectData.db')

        self.db_manager.create_database()
        self.construct_session()
        
    def construct_session(self):
        if self.create_objects:
            self.instantiate_entities()

        if self.load_objects:
            self.db_manager.load_objects(self.engine)
        
        self.construct_gui() 
        self.run()

    def instantiate_entities(self):
        self.engine.add_object(Quad('quad1', (300, 200, 10), 10, 100, 200, 'blue'))

    def save_world(self):
        self.db_manager.save_objects(self.engine.objects)

    def debug_display(self, object_3d):
        pygame.draw.circle(self.screen, (255, 0, 0), (int(object_3d.points.access_index(0, 0)), int(object_3d.points.access_index(0, 1))), 5, 0)
        pygame.draw.circle(self.screen, (0, 255, 0), (int(object_3d.find_centre()[0]), int(object_3d.find_centre()[1])), self.point_radius, 0)
        pygame.draw.circle(self.screen, (0, 0, 255), (int(self.engine.entities_centre(self.engine.objects)[0]), int(self.engine.entities_centre(self.engine.objects)[1])), self.point_radius, 0)
    
    def construct_gui(self):

        divider_dimensions = (100, 1)

        controls_header = tkinter.Label(self.control, text='ENGINE SETTINGS', bg=self.gui_bg_colour, fg='white', font=('Montserrat SemiBold', '16'))
        controls_header.place(x = self.control_width / 2, y = 10, anchor = 'n')

        canvas = tkinter.Canvas(self.control, width = divider_dimensions[0], height = divider_dimensions[1], bg = self.gui_bg_colour, bd = 0, highlightthickness=0)
        canvas.place(x = (self.control_width - divider_dimensions[0]) / 2, y = 50)
        line = canvas.create_line(0, 0, divider_dimensions[0], 0, fill = '#af00e8')

        self.root.update()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    self.db_manager.close_database()
                elif event.type == pygame.KEYDOWN:
                    if event.key in self.camera.controls:
                        self.camera.controls[event.key](self, self.engine, self.db_manager)

            self.render_objects()
            pygame.display.flip()
            self.clock.tick(self.max_frame_rate)
    
    def render_objects(self):
        self.screen.fill(self.bg_colour)
        layer = pygame.Surface((self.viewer_width, self.viewer_height))
        layer.set_alpha(self.surface_alpha)
        layer.fill(self.bg_colour)
        self.engine.order_objects().values()
        for object_3d in self.engine.order_objects().values():
            if object_3d.check_render_distance(self.max_render_distance, self.min_render_distance):
                if object_3d.is_visible(self.viewer_width, self.viewer_height):
                    if self.display_surfaces:
                        for surface in object_3d.order_surfaces():
                            surface_points = object_3d.find_points(surface)
                            pygame.draw.polygon(layer, object_3d.map_colour(surface, self.lighting_factor), surface_points)
                            if self.per_surface_alpha:
                                self.screen.blit(layer, (0,0))
                    if not self.per_surface_alpha:
                        self.screen.blit(layer, (0,0))

                    if self.hidden_lines == False:
                        if self.display_lines:
                            for point_1, point_2 in object_3d.lines:
                                pygame.draw.aaline(self.screen, self.line_colour, object_3d.projected.access_row(point_1)[:2], object_3d.projected.access_row(point_2)[:2], 1)

                        if self.display_points:
                            for point in object_3d.projected:
                                pygame.draw.circle(self.screen, self.point_colour, (int(point[0]), int(point[1])), self.point_radius, 0)

                else:
                    self.render_relative_lines(object_3d)

        for object_3d in self.engine.objects.values():
            if object_3d.check_render_distance(self.max_render_distance, self.min_render_distance):
                if object_3d.is_visible(self.viewer_width, self.viewer_height):
                    if self.hidden_lines:
                        if self.display_lines:
                            for point_1, point_2 in object_3d.lines:
                                pygame.draw.aaline(self.screen, self.line_colour, object_3d.projected.access_row(point_1)[:2], object_3d.projected.access_row(point_2)[:2], 1)

                        if self.display_points:
                            for point in object_3d.projected:
                                pygame.draw.circle(self.screen, self.point_colour, (int(point[0]), int(point[1])), self.point_radius, 0)
                
                else:
                    self.render_relative_lines(object_3d)

        if self.debug_mode:
            self.debug_display(object_3d)

        fps = self.font.render('FPS: '+ str(int(self.clock.get_fps())), True, self.fps_colour)
        self.screen.blit(fps, (10, 10))
        self.screen.blit(self.logo, (self.viewer_width - 197, self.viewer_height - 70))

    def render_relative_lines(self, object_3d):
       for direction in object_3d.viewer_relativity(self.viewer_width, self.viewer_height):
            if direction == 'W':
                pygame.draw.line(self.screen, (118, 18, 219), (0,0), (0,self.viewer_height), 5)
            if direction == 'E':
                pygame.draw.line(self.screen, (118, 18, 219), (self.viewer_width,0), (self.viewer_width,self.viewer_height), 5)
            if direction == 'N':
                pygame.draw.line(self.screen, (118, 18, 219), (0,0), (self.viewer_width,0), 5)
            if direction == 'S':
                pygame.draw.line(self.screen, (118, 18, 219), (0,self.viewer_height), (self.viewer_width,self.viewer_height), 5)


display = DisplayManager(1600, 900)