import pygame, sys, os, time, threading
from ctypes import windll
import matplotlib.animation as animation

from engine_3d import Engine3D
from shapes import Cube, Quad, Plane, Polygon, Sphere, GUILines
from database_manager import DatabaseManager
from camera import Camera
from gui import GUI, CoordinateInput
import data_handling

""" For rotation of all objects use self.viewer_centre to spin all objects """
""" For individual rotation of one ore multiple objects use objects = [] in engine.rotate() with array of object lables """
""" For combined spin over multiple objects use objects = [] in engine.rotate() with array of object lables """

""" Add ablity to click on points and enter new values """
""" Clean up lighting wrt moving objects to top of screen increasing contrast """
""" Login system """
""" Add ability to change object rotation and direction using clicking on objects """
""" Add ability to change object rotation anchor point """
""" Add ability to add objects from GUI, (click and drag) and set values """
""" Include ability to save user settings """

class EngineClient():
    def __init__(self, width, height):

        self.line_colour = (255, 255, 255)
        self.point_colour = (255, 255, 255)
        self.bg_colour = (35, 35, 35)
        self.fps_colour = (255, 255, 255)
        self.relative_line_colour = (118, 18, 219)
        self.point_radius = 2
        self.lighting_factor = 1.25 # Controls the contrast of colour in objects, higher means more contrast
        self.rotation_factor = 0.1
        self.translation_factor = 25
        self.scaling_factor = 1.1
        self.movement_factor = 25
        self.max_frame_rate = 1000
        self.max_render_distance = 1
        self.min_render_distance = 1 / 10000

        self.displacement_arrows = 0

        self.display_surfaces = True
        self.display_points = False
        self.display_lines = False
        self.debug_mode = False
        self.hidden_lines = False #  Display lines within overlapping objects
        self.display_hud = True
        self.display_logo = True
        self.import_objects = False 
        self.create_objects = True
        
        self.fps_array, self.time_array = [], []
        self.fps_array_max_length = 500
        self.fps_graph_interval = 500
        self.start_time = time.time()

        self.gui_line_length = 20
        self.gui_line_width = 4

        self.chosen_point = None
        self.clickable_radius = 5 # The radius at which a point can be clicked beyond its shown radius
        self.translating, self.translating_x, self.translating_y = False, False, False
        self.input_boxes = None

        self.camera = Camera(self)
        self.db_manager = DatabaseManager('ObjectData.db')
        self.gui = GUI(self, width, height)
        self.engine = Engine3D('orthographic', self.gui.viewer_centre)

        pygame.init()
        self.viewer = pygame.display.set_mode((self.gui.viewer_width, self.gui.viewer_height))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font('fonts/Montserrat-SemiBold.ttf', 16)
        pygame.key.set_repeat(1, self.movement_factor)
        self.logo = pygame.image.load('FL3D_small.png')
        self.logo_size = (197, 70)

        self.db_manager.create_database()
        self.construct_session()
        
    def construct_session(self):

        if self.create_objects:
            self.instantiate_entities()

        fps_animation = self.gui.animate_fps_graph()

        if __name__ == '__main__':
            self.running = True
            self.run()

    def instantiate_entities(self):
        self.engine.add_object(Quad('quad1', (300, 200, 10), 10, 100, 200, 'blue'))
        self.engine.add_object(Quad('quad2', (300, 250, 60), 10, 100, 200, 'red'))
        self.engine.add_object(Sphere('quad2', (300, 250, 60), 10, 10, 'red'))

    def save_world(self):
        self.db_manager.save_objects(self.engine.objects)

    def debug_display(self, object_3d):
        pygame.draw.circle(self.viewer, (255, 0, 0), (int(object_3d.points.access_index(0, 0)), int(object_3d.points.access_index(0, 1))), self.point_radius, 0)
        pygame.draw.circle(self.viewer, (0, 255, 0), (int(object_3d.find_centre()[0]), int(object_3d.find_centre()[1])), self.point_radius, 0)
        pygame.draw.circle(self.viewer, (0, 0, 255), (int(self.engine.entities_centre(self.engine.objects)[0]), int(self.engine.entities_centre(self.engine.objects)[1])), self.point_radius, 0)
    
    def close_window(self):
        self.gui.destruct_gui()
        self.running_fps = False
        self.running = False
        self.db_manager.close_database()
        pygame.quit()

    def minimise_window(self):
        self.gui.window.update_idletasks()
        self.gui.window.overrideredirect(False)
        self.gui.window.state('iconic')
        self.gui.maximise_window = True

    def maximise_window(self, event):
        self.gui.window.update_idletasks()
        self.gui.window.overrideredirect(True)
        if self.gui.maximise_window:
            self.gui.set_appwindow()
            self.gui.maximise_window = False

    def run(self):
        while self.running:
            pygame.mouse.set_cursor(*pygame.cursors.broken_x)
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key in self.camera.controls: 
                        self.camera.controls[event.key](self, self.engine)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.check_translation_lines(pygame.mouse.get_pos())
                    self.translating = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.translating_x, self.translating_y = False, False
                    self.translating = False
                elif event.type == pygame.MOUSEMOTION:
                    self.check_translation(pygame.mouse.get_pos())
                if self.input_boxes != None:
                    for input_box in self.input_boxes.access_input_boxes():
                        input_box.handle_event(event, self.movement_factor)

            self.render_objects()
            pygame.display.flip()
            self.clock.tick(self.max_frame_rate)
            if self.running:
                self.gui.root.update()

    def check_translation_lines(self, mouse_position):
        for rendered_point in self.engine.rendered_points:
            if self.check_chosen_point_radius(rendered_point[0], mouse_position):
                self.current_translation_point = rendered_point[1]
                self.engine.clear_translation_lines()
                translation_lines = GUILines(rendered_point[1], self.gui_line_length)
                self.engine.set_translation_lines(translation_lines)
                if rendered_point == self.chosen_point:
                    self.engine.clear_translation_lines()
                    self.chosen_point, self.input_boxes = None, None
                else:
                    self.chosen_point = rendered_point
                    self.input_boxes = CoordinateInput(rendered_point[0][0], rendered_point[0][1], rendered_point[0][2])
                break

    def check_chosen_point_radius(self, line, mouse_position):
        click_in_radius = False
        for x_position in range(mouse_position[0] - self.clickable_radius, mouse_position[0] + self.clickable_radius):
            for y_position in range(mouse_position[1] - self.clickable_radius, mouse_position[1] + self.clickable_radius):
                if line.collidepoint((x_position, y_position)):
                    click_in_radius = True
        return click_in_radius
    
    def check_translation(self, mouse_position):
        if len(self.engine.rendered_translation_lines) > 0 and self.translating and self.chosen_point != None:
            if self.check_chosen_point_radius(self.engine.rendered_translation_lines[0], mouse_position) and self.translating_x == False and self.translating_y == False:
                self.translating_x = True
                self.translating_y = False
            if self.check_chosen_point_radius(self.engine.rendered_translation_lines[1], mouse_position) and self.translating_y == False and self.translating_x == False:
                self.translating_y = True
                self.translating_x = False

            if self.translating_x:
                current_row = self.chosen_point[2].points.access_row(self.chosen_point[3])
                new_row = mouse_position[0] - self.gui_line_length / 2, current_row[1], current_row[2], current_row[3]
                self.chosen_point[2].points.set_row(self.chosen_point[3], new_row)
                self.chosen_point[2].project(self.engine.projection_type, self.engine.projection_anchor)
                translation_lines = GUILines(self.chosen_point[2].projected.access_row(self.chosen_point[3]), self.gui_line_length)
                self.engine.set_translation_lines(translation_lines)

            if self.translating_y:
                current_row = self.chosen_point[2].points.access_row(self.chosen_point[3])
                new_row = current_row[0], mouse_position[1] - self.gui_line_length / 2, current_row[2], current_row[3]
                self.chosen_point[2].points.set_row(self.chosen_point[3], new_row)
                self.chosen_point[2].project(self.engine.projection_type, self.engine.projection_anchor)
                translation_lines = GUILines(self.chosen_point[2].projected.access_row(self.chosen_point[3]), self.gui_line_length)
                self.engine.set_translation_lines(translation_lines)

            self.input_boxes = CoordinateInput(self.chosen_point[2].projected.access_row(self.chosen_point[3])[0], self.chosen_point[2].projected.access_row(self.chosen_point[3])[1])

    def text_boxes_accepting_input(self):
        accepting_input = False
        if self.input_boxes != None:
            if self.input_boxes.accepting_input():
                accepting_input = True
        return accepting_input
    
    def render_objects(self):
        self.viewer.fill(self.bg_colour)
        self.engine.clear_rendered_points()
        for object_3d in self.engine.order_objects().values():
            if object_3d.check_render_distance(self.max_render_distance, self.min_render_distance):
                if object_3d.is_visible(self.gui.viewer_width, self.gui.viewer_height):
                    if self.display_surfaces:
                        for surface in object_3d.order_surfaces():
                            surface_points = object_3d.find_points(surface)
                            pygame.draw.polygon(self.viewer, object_3d.map_colour(surface, self.lighting_factor), surface_points)

                    if self.hidden_lines == False:
                        if self.display_lines:
                            for point_1, point_2 in object_3d.lines:
                                pygame.draw.aaline(self.viewer, self.line_colour, object_3d.projected.access_row(point_1)[:2], object_3d.projected.access_row(point_2)[:2])

                        if self.display_points:
                            for i, point in enumerate(object_3d.projected):
                                rendered_point = pygame.draw.circle(self.viewer, self.point_colour, (int(point[0]), int(point[1])), self.point_radius, 0)
                                self.engine.rendered_points.append([rendered_point, point, object_3d, i])
                else:
                    self.render_relative_lines(object_3d)

        for object_3d in self.engine.objects.values():
            if object_3d.check_render_distance(self.max_render_distance, self.min_render_distance):
                if object_3d.is_visible(self.gui.viewer_width, self.gui.viewer_height):
                    if self.hidden_lines:
                        if self.display_lines:
                            for point_1, point_2 in object_3d.lines:
                                pygame.draw.aaline(self.viewer, self.line_colour, object_3d.projected.access_row(point_1)[:2], object_3d.projected.access_row(point_2)[:2])

                        if self.display_points:
                            for i, point in enumerate(object_3d.projected):
                                rendered_point = pygame.draw.circle(self.viewer, self.point_colour, (int(point[0]), int(point[1])), self.point_radius, 0)
                                self.engine.rendered_points.append([rendered_point, point, object_3d, i])
                else:
                    self.render_relative_lines(object_3d)

            if self.debug_mode:
                self.debug_display(object_3d)

        if self.display_hud:
            fps = self.font.render('FPS: '+ str(int(self.clock.get_fps())), True, self.fps_colour)
            self.viewer.blit(fps, (10, 10))
            view = self.font.render('ORTHOGRAPHIC VIEW', True, self.fps_colour)
            self.viewer.blit(view, (self.gui.viewer_width - 200, 10))
        
        if self.display_logo:
            self.viewer.blit(self.logo, (self.gui.viewer_width - self.logo_size[0], self.gui.viewer_height - self.logo_size[1]))

        if self.engine.get_translation_lines() != None:
            if self.engine.get_translation_lines().check_render_distance(self.max_render_distance, self.min_render_distance):
                if self.engine.get_translation_lines().is_visible(self.gui.viewer_width, self.gui.viewer_height):
                    self.render_translation_lines()
                    self.render_input_boxes()

    def render_translation_lines(self):
        translation_lines = self.engine.get_translation_lines()
        x_line = pygame.draw.line(self.viewer, self.gui.gui_translation_lines_colour_x, data_handling.convert_to_int_array(translation_lines.projected.access_row(0)[:2]), data_handling.convert_to_int_array(translation_lines.projected.access_row(1)[:2]), self.gui_line_width)
        y_line = pygame.draw.line(self.viewer, self.gui.gui_translation_lines_colour_y, data_handling.convert_to_int_array(translation_lines.projected.access_row(0)[:2]), data_handling.convert_to_int_array(translation_lines.projected.access_row(2)[:2]), self.gui_line_width)
        rendered_point = pygame.draw.circle(self.viewer, self.point_colour, data_handling.convert_to_int_array(translation_lines.projected.access_row(0)[:2]), self.point_radius, 0)
        self.engine.rendered_translation_lines = [x_line, y_line]

    def render_input_boxes(self):
        for input_box in self.input_boxes.access_input_boxes():
            input_box.resize()
            input_box.draw(self.viewer)

    def render_relative_lines(self, object_3d):
       for direction in object_3d.viewer_relativity(self.gui.viewer_width, self.gui.viewer_height):
            if direction == 'W':
                pygame.draw.line(self.viewer, self.relative_line_colour, (0,0), (0,self.gui.viewer_height), 5)
            if direction == 'E':
                pygame.draw.line(self.viewer, self.relative_line_colour, (self.gui.viewer_width,0), (self.gui.viewer_width,self.gui.viewer_height), 5)
            if direction == 'N':
                pygame.draw.line(self.viewer, self.relative_line_colour, (0,0), (self.gui.viewer_width,0), 5)
            if direction == 'S':
                pygame.draw.line(self.viewer, self.relative_line_colour, (0,self.gui.viewer_height), (self.gui.viewer_width,self.gui.viewer_height), 5)

display = EngineClient(1600, 900)