import pygame, sys, os, tkinter, time, threading
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk

from engine_3d import Engine3D
from shapes import Cube, Quad, Plane, Polygon, Sphere
from database_manager import DatabaseManager
import data_handling

""" For rotation of all objects use self.viewer_centre to spin all objects """
""" For individual rotation of one ore multiple objects use objects = [] in engine.rotate() with array of object lables """
""" For combined spin over multiple objects use objects = [] in engine.rotate() with array of object lables """

""" Add fps graph """
""" Add UI with options, add optional grid to screen """
""" Add ablity to click on points and enter new values """
""" Clean up lighting wrt moving objects to top of screen increasing contrast """
""" Login system """
""" Add ability to change object rotation and direction using clicking on objects """
""" Add ability to change object rotation anchor point """
""" Add ability to add objects from GUI, (click and drag) and set values """
""" Include ability to save user settings """

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

        self.window_top_width = width
        self.window_top_height = 25
        self.control_width = 250
        self.control_height = height - self.window_top_height
        self.fps_graph_width = 400
        self.details_width = width - self.control_width - self.fps_graph_width
        self.details_height = 200
        self.viewer_width = width - self.control_width
        self.viewer_height = height - self.details_height - self.window_top_height
        self.viewer_centre = (self.viewer_width / 2, self.viewer_height / 2, 0, 0)
        self.fps_graph_height = self.details_height
        self.window_dimensions = (width, height)

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

        self.display_surfaces = True
        self.display_points = False
        self.display_lines = False
        self.debug_mode = False
        self.hidden_lines = False #  Display lines within overlapping objects
        self.display_fps = True
        self.display_logo = True
        self.import_objects = False 
        self.create_objects = True 

        self.camera = Camera(self.translation_factor, self.scaling_factor, self.rotation_factor)
        self.engine = Engine3D('orthographic', self.viewer_centre)
        self.db_manager = DatabaseManager('ObjectData.db')

        self.gui_bg_colour = '#1e1e1e'
        self.gui_highlight_bg_colour = '#282828'
        self.gui_fg_colour = '#af00e8'
        self.gui_highlight_fg_colour = '#b44df0'
        self.gui_window_title_colour = '#ababab'
        self.gui_header_colour = '#ffffff'
        self.gui_header_font = ('Montserrat SemiBold', '16')
        self.gui_label_font = ('Montserrat Regular', '10')
        self.gui_button_font = ('Montserrat Medium', '10')
        self.gui_window_title_font = ('Montserrat Medium', '10')

        self.gui_header_padding = 10
        self.gui_separator_padding = 50
        self.separator_dimensions = (100, 1)
        self.gui_label_padding = (25, 70)
        self.gui_slider_padding = (140, 1)
        self.gui_slider_offset = 25
        self.gui_button_padding = self.gui_label_padding[0] + 4, self.gui_label_padding[1] + self.gui_slider_offset * 5.5
        self.gui_button_offset = 40
        self.gui_exit_button_size = (30, 30)

        self.root = tkinter.Tk()

        self.root.attributes('-alpha', 0.0)
        self.root.iconify()
        self.root.resizable(False, False)
        self.window = FloatingWindow(self.root)
        self.window.geometry("{}x{}+{}+{}".format(self.window_dimensions[0], self.window_dimensions[1], 200, 200))
        self.window.overrideredirect(1)
        self.window.title('FL3D Engine')

        self.window_top = tkinter.Frame(self.window, bg = self.gui_bg_colour, width = self.window_top_width, height = self.window_top_height)
        self.window_top.pack(side = 'top')
        self.control = tkinter.Frame(self.window, bg = self.gui_bg_colour, width = self.control_width, height = self.control_height)
        self.control.pack(side = 'right')
        self.viewer = tkinter.Frame(self.window, width = self.viewer_width, height = self.viewer_height)
        self.viewer.pack(side = 'top')
        self.details = tkinter.Frame(self.window, bg = self.gui_bg_colour, width = self.details_width, height = self.details_height)
        self.details.pack(side = 'right')
        self.fps_graph = tkinter.Frame(self.window, width = self.fps_graph_width, height = self.fps_graph_height)
        self.fps_graph.pack(side = 'left')

        self.window.create_grip(self.window_top)

        os.environ['SDL_VIDEODRIVER'] = 'windib'
        os.environ['SDL_WINDOWID'] = str(self.viewer.winfo_id()) # Used to embed pygame window in tkinter

        self.fps_array = []
        self.time_array = []
        self.fps_array_max_length = 300
        self.fps_graph_interval = 100
        self.start_time = time.time()

        self.graph_colour = self.gui_fg_colour
        self.axis_colour = '#ffffff'
        self.graph_line_width = 1
        self.fps_viewer = plt.Figure(figsize=(4,2), dpi=100)
        self.fps_plot = self.fps_viewer.add_subplot(111)
        self.fps_viewer.set_facecolor(self.gui_bg_colour)
        self.fps_plot.set_facecolor(self.gui_bg_colour)
        self.fps_plot.spines['left'].set_color(self.axis_colour)
        self.fps_plot.spines['right'].set_color(self.axis_colour)
        self.fps_plot.spines['top'].set_color(self.axis_colour)
        self.fps_plot.spines['bottom'].set_color(self.axis_colour)
        self.fps_plot.spines['right'].set_visible(False)
        self.fps_plot.spines['top'].set_visible(False)
        self.fps_plot.tick_params(axis='y', colors=self.axis_colour)
        self.fps_plot.tick_params(axis='x', colors=self.axis_colour)
        self.fps_plot.set_title('Frames Per Second')

        chart_type = FigureCanvasTkAgg(self.fps_viewer, self.fps_graph)
        chart_type.get_tk_widget().pack()

        pygame.init()
        self.viewer = pygame.display.set_mode((self.viewer_width, self.viewer_height))
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

        self.construct_gui() 

        ani = animation.FuncAnimation(self.fps_viewer, self.update_fps_graph, interval = self.fps_graph_interval)
        self.root.update_idletasks()

        if __name__ == '__main__':
            self.running = True
            self.run()

    def instantiate_entities(self):
        self.engine.add_object(Quad('quad1', (300, 200, 10), 10, 100, 200, 'blue'))
        self.engine.add_object(Quad('quad2', (300, 250, 60), 10, 100, 200, 'red'))

    def save_world(self):
        self.db_manager.save_objects(self.engine.objects)

    def debug_display(self, object_3d):
        pygame.draw.circle(self.viewer, (255, 0, 0), (int(object_3d.points.access_index(0, 0)), int(object_3d.points.access_index(0, 1))), self.point_radius, 0)
        pygame.draw.circle(self.viewer, (0, 255, 0), (int(object_3d.find_centre()[0]), int(object_3d.find_centre()[1])), self.point_radius, 0)
        pygame.draw.circle(self.viewer, (0, 0, 255), (int(self.engine.entities_centre(self.engine.objects)[0]), int(self.engine.entities_centre(self.engine.objects)[1])), self.point_radius, 0)

    def update_display_surfaces(self, value):
        if value == '1':
            self.display_surfaces = True 
        elif value == '0':
            self.display_surfaces = False

    def update_display_lines(self, value):
        if value == '1':
            self.display_lines = True 
        elif value == '0':
            self.display_lines = False
    
    def update_display_points(self, value):
        if value == '1':
            self.display_points = True 
        elif value == '0':
            self.display_points = False

    def update_debug_mode(self, value):
        if value == '1':
            self.debug_mode = True 
        elif value == '0':
            self.debug_mode = False

    def update_hidden_lines(self, value):
        if value == '1':
            self.hidden_lines = True 
        elif value == '0':
            self.hidden_lines = False
    
    def update_display_fps(self, value):
        if value == '1':
            self.display_fps = True
        elif value == '0':
            self.display_fps = False

    def update_display_logo(self, value):
        if value == '1':
            self.display_logo = True
        elif value == '0':
            self.display_logo = False

    def update_import_objects(self):
        self.db_manager.import_objects(self.engine)

    def update_clear_worldspace(self):
        self.engine.clear_all_objects()
            
    def construct_gui(self):
        self.exit_img = tkinter.PhotoImage(file = 'EXIT.png')
        exit_button = tkinter.Button(self.window_top, text = "Exit", width = self.gui_exit_button_size[0], height = self.gui_exit_button_size[1], command = self.close_window, borderwidth=0, bd = -2, bg = self.gui_bg_colour, activebackground=self.gui_highlight_bg_colour)
        exit_button.config(image = self.exit_img)
        exit_button.place(x = self.window_dimensions[0] - self.gui_exit_button_size[0], y = -3, anchor = 'nw')

        window_title = tkinter.Label(self.window_top, text='FL3D Rendering Engine', bg=self.gui_bg_colour, fg=self.gui_window_title_colour, font=self.gui_window_title_font)
        window_title.place(x = self.window_dimensions[0] / 2, y = 0, anchor = 'n')
        self.window.create_grip(window_title)

        controls_header = tkinter.Label(self.control, text='ENGINE SETTINGS', bg=self.gui_bg_colour, fg=self.gui_header_colour, font=self.gui_header_font)
        controls_header.place(x = self.control_width / 2, y = self.gui_header_padding, anchor = 'n')

        separator_canvas = tkinter.Canvas(self.control, width = self.separator_dimensions[0], height = self.separator_dimensions[1], bg = self.gui_bg_colour, bd = 0, highlightthickness=0)
        separator_canvas.place(x = (self.control_width - self.separator_dimensions[0]) / 2, y = self.gui_separator_padding)
        separator = separator_canvas.create_line(0, 0, self.separator_dimensions[0], 0, fill = self.gui_fg_colour)

        display_surfaces_label = tkinter.Label(self.control, text='Display Surfaces', bg=self.gui_bg_colour, fg=self.gui_window_title_colour, font=self.gui_label_font)
        display_surfaces_label.place(x = self.gui_label_padding[0], y = self.gui_label_padding[1], anchor = 'w')
        display_surfaces_slider = tkinter.Scale(self.control, orient=tkinter.HORIZONTAL, length=50, width=15, sliderlength=15, from_=0, to=1, bg=self.gui_fg_colour, bd=0, borderwidth=0, activebackground=self.gui_highlight_fg_colour, highlightthickness=0, sliderrelief="flat", showvalue=0, troughcolor="#333333", command = self.update_display_surfaces)
        display_surfaces_slider.set(1)
        display_surfaces_slider.place(x=self.gui_label_padding[0] + self.gui_slider_padding[0], y = self.gui_label_padding[1] + self.gui_slider_padding[1], anchor = 'w')

        display_lines_label = tkinter.Label(self.control, text='Display Lines', bg=self.gui_bg_colour, fg=self.gui_window_title_colour, font=self.gui_label_font)
        display_lines_label.place(x = self.gui_label_padding[0], y = self.gui_label_padding[1] + self.gui_slider_offset, anchor = 'w')
        display_lines_slider = tkinter.Scale(self.control, orient=tkinter.HORIZONTAL, length=50, width=15, sliderlength=15, from_=0, to=1, bg=self.gui_fg_colour, bd=0, borderwidth=0, activebackground=self.gui_highlight_fg_colour, highlightthickness=0, sliderrelief="flat", showvalue=0, troughcolor="#333333", command = self.update_display_lines)
        display_lines_slider.set(1)
        display_lines_slider.place(x=self.gui_label_padding[0] + self.gui_slider_padding[0], y = self.gui_label_padding[1] + self.gui_slider_padding[1] + self.gui_slider_offset, anchor = 'w')

        display_points_label = tkinter.Label(self.control, text='Display Points', bg=self.gui_bg_colour, fg=self.gui_window_title_colour, font=self.gui_label_font)
        display_points_label.place(x = self.gui_label_padding[0], y = self.gui_label_padding[1] + self.gui_slider_offset * 2, anchor = 'w')
        display_points_slider = tkinter.Scale(self.control, orient=tkinter.HORIZONTAL, length=50, width=15, sliderlength=15, from_=0, to=1, bg=self.gui_fg_colour, bd=0, borderwidth=0, activebackground=self.gui_highlight_fg_colour, highlightthickness=0, sliderrelief="flat", showvalue=0, troughcolor="#333333", command = self.update_display_points)
        display_points_slider.set(1)
        display_points_slider.place(x=self.gui_label_padding[0] + self.gui_slider_padding[0], y = self.gui_label_padding[1] + self.gui_slider_padding[1] + self.gui_slider_offset * 2, anchor = 'w')

        debug_mode_label = tkinter.Label(self.control, text='Debug Mode', bg=self.gui_bg_colour, fg=self.gui_window_title_colour, font=self.gui_label_font)
        debug_mode_label.place(x = self.gui_label_padding[0], y = self.gui_label_padding[1] + self.gui_slider_offset * 3, anchor = 'w')
        debug_mode_slider = tkinter.Scale(self.control, orient=tkinter.HORIZONTAL, length=50, width=15, sliderlength=15, from_=0, to=1, bg=self.gui_fg_colour, bd=0, borderwidth=0, activebackground=self.gui_highlight_fg_colour, highlightthickness=0, sliderrelief="flat", showvalue=0, troughcolor="#333333", command = self.update_debug_mode)
        debug_mode_slider.set(1)
        debug_mode_slider.place(x=self.gui_label_padding[0] + self.gui_slider_padding[0], y = self.gui_label_padding[1] + self.gui_slider_padding[1] + self.gui_slider_offset * 3, anchor = 'w')

        hidden_lines_label = tkinter.Label(self.control, text='Show Hidden Lines', bg=self.gui_bg_colour, fg=self.gui_window_title_colour, font=self.gui_label_font)
        hidden_lines_label.place(x = self.gui_label_padding[0], y = self.gui_label_padding[1] + self.gui_slider_offset * 4, anchor = 'w')
        hidden_lines_slider = tkinter.Scale(self.control, orient=tkinter.HORIZONTAL, length=50, width=15, sliderlength=15, from_=0, to=1, bg=self.gui_fg_colour, bd=0, borderwidth=0, activebackground=self.gui_highlight_fg_colour, highlightthickness=0, sliderrelief="flat", showvalue=0, troughcolor="#333333", command = self.update_hidden_lines)
        hidden_lines_slider.set(1)
        hidden_lines_slider.place(x=self.gui_label_padding[0] + self.gui_slider_padding[0], y = self.gui_label_padding[1] + self.gui_slider_padding[1] + self.gui_slider_offset * 4, anchor = 'w')

        display_fps_label = tkinter.Label(self.control, text='Display FPS', bg=self.gui_bg_colour, fg=self.gui_window_title_colour, font=self.gui_label_font)
        display_fps_label.place(x = self.gui_label_padding[0], y = self.gui_label_padding[1] + self.gui_slider_offset * 5, anchor = 'w')
        display_fps_slider = tkinter.Scale(self.control, orient=tkinter.HORIZONTAL, length=50, width=15, sliderlength=15, from_=0, to=1, bg=self.gui_fg_colour, bd=0, borderwidth=0, activebackground=self.gui_highlight_fg_colour, highlightthickness=0, sliderrelief="flat", showvalue=0, troughcolor="#333333", command = self.update_display_fps)
        display_fps_slider.set(1)
        display_fps_slider.place(x=self.gui_label_padding[0] + self.gui_slider_padding[0], y = self.gui_label_padding[1] + self.gui_slider_padding[1] + self.gui_slider_offset * 5, anchor = 'w')

        display_logo_label = tkinter.Label(self.control, text='Display Logo', bg=self.gui_bg_colour, fg=self.gui_window_title_colour, font=self.gui_label_font)
        display_logo_label.place(x = self.gui_label_padding[0], y = self.gui_label_padding[1] + self.gui_slider_offset * 6, anchor = 'w')
        display_logo_slider = tkinter.Scale(self.control, orient=tkinter.HORIZONTAL, length=50, width=15, sliderlength=15, from_=0, to=1, bg=self.gui_fg_colour, bd=0, borderwidth=0, activebackground=self.gui_highlight_fg_colour, highlightthickness=0, sliderrelief="flat", showvalue=0, troughcolor="#333333", command = self.update_display_logo)
        display_logo_slider.set(1)
        display_logo_slider.place(x=self.gui_label_padding[0] + self.gui_slider_padding[0], y = self.gui_label_padding[1] + self.gui_slider_padding[1] + self.gui_slider_offset * 6, anchor = 'w')

        import_objects_button = tkinter.Button(self.control, text="Import Objects", fg="white", bg= self.gui_fg_colour, borderwidth=0, height = 1, width = 15, activebackground=self.gui_highlight_fg_colour, activeforeground="white", command= self.update_import_objects, font=self.gui_button_font)
        import_objects_button.place(x= self.control_width / 2, y = self.gui_button_padding[1] + self.gui_button_offset * 1, anchor = 'n')

        clear_worldspace_button = tkinter.Button(self.control, text="Clear Worldspace", fg="white", bg= self.gui_fg_colour, borderwidth=0, height = 1, width = 15, activebackground=self.gui_highlight_fg_colour, activeforeground="white", command= self.update_clear_worldspace, font=self.gui_button_font)
        clear_worldspace_button.place(x= self.control_width / 2, y = self.gui_button_padding[1] + self.gui_button_offset * 2, anchor = 'n')
    
    def close_window(self):
        self.root.quit()
        self.running_fps = False
        self.running = False
        self.db_manager.close_database()
        pygame.quit()
        plt.close()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key in self.camera.controls: 
                        self.camera.controls[event.key](self, self.engine, self.db_manager)

            self.render_objects()
            pygame.display.flip()
            self.clock.tick(self.max_frame_rate)
            if self.running:
                self.root.update()

    def update_fps_graph(self, x):
        self.time_array.append(time.time() - self.start_time)
        self.fps_array.append(self.clock.get_fps())
        if len(self.fps_array) > self.fps_array_max_length:
            self.fps_array = self.fps_array[1:]
            self.time_array = self.time_array[1:]
        self.fps_plot.cla()
        self.fps_plot.plot(self.time_array, self.fps_array, color = self.graph_colour, linewidth = self.graph_line_width)
    
    def render_objects(self):
        self.viewer.fill(self.bg_colour)
        self.engine.order_objects().values()
        for object_3d in self.engine.order_objects().values():
            if object_3d.check_render_distance(self.max_render_distance, self.min_render_distance):
                if object_3d.is_visible(self.viewer_width, self.viewer_height):
                    if self.display_surfaces:
                        for surface in object_3d.order_surfaces():
                            surface_points = object_3d.find_points(surface)
                            pygame.draw.polygon(self.viewer, object_3d.map_colour(surface, self.lighting_factor), surface_points)

                    if self.hidden_lines == False:
                        if self.display_lines:
                            for point_1, point_2 in object_3d.lines:
                                pygame.draw.aaline(self.viewer, self.line_colour, object_3d.projected.access_row(point_1)[:2], object_3d.projected.access_row(point_2)[:2], 1)

                        if self.display_points:
                            for point in object_3d.projected:
                                pygame.draw.circle(self.viewer, self.point_colour, (int(point[0]), int(point[1])), self.point_radius, 0)
                else:
                    self.render_relative_lines(object_3d)

        for object_3d in self.engine.objects.values():
            if object_3d.check_render_distance(self.max_render_distance, self.min_render_distance):
                if object_3d.is_visible(self.viewer_width, self.viewer_height):
                    if self.hidden_lines:
                        if self.display_lines:
                            for point_1, point_2 in object_3d.lines:
                                pygame.draw.aaline(self.viewer, self.line_colour, object_3d.projected.access_row(point_1)[:2], object_3d.projected.access_row(point_2)[:2], 1)

                        if self.display_points:
                            for point in object_3d.projected:
                                pygame.draw.circle(self.viewer, self.point_colour, (int(point[0]), int(point[1])), self.point_radius, 0)
                else:
                    self.render_relative_lines(object_3d)

            if self.debug_mode:
                self.debug_display(object_3d)

        if self.display_fps:
            fps = self.font.render('FPS: '+ str(int(self.clock.get_fps())), True, self.fps_colour)
            self.viewer.blit(fps, (10, 10))
        
        if self.display_logo:
            self.viewer.blit(self.logo, (self.viewer_width - self.logo_size[0], self.viewer_height - self.logo_size[1]))

    def render_relative_lines(self, object_3d):
       for direction in object_3d.viewer_relativity(self.viewer_width, self.viewer_height):
            if direction == 'W':
                pygame.draw.line(self.viewer, (118, 18, 219), (0,0), (0,self.viewer_height), 5)
            if direction == 'E':
                pygame.draw.line(self.viewer, (118, 18, 219), (self.viewer_width,0), (self.viewer_width,self.viewer_height), 5)
            if direction == 'N':
                pygame.draw.line(self.viewer, (118, 18, 219), (0,0), (self.viewer_width,0), 5)
            if direction == 'S':
                pygame.draw.line(self.viewer, (118, 18, 219), (0,self.viewer_height), (self.viewer_width,self.viewer_height), 5)

class FloatingWindow(tkinter.Toplevel):
    def __init__(self, *args, **kwargs):
        tkinter.Toplevel.__init__(self, *args, **kwargs)
        self.overrideredirect(True)

    def create_grip(self, frame):
        frame.bind("<ButtonPress-1>", self.start_motion)
        frame.bind("<ButtonRelease-1>", self.end_motion)
        frame.bind("<B1-Motion>", self.in_motion)

    def start_motion(self, event):
        self.x = event.x
        self.y = event.y

    def end_motion(self, event):
        self.x = None
        self.y = None

    def in_motion(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry("+{}+{}".format(x, y))

display = DisplayManager(1600, 900)