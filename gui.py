import tkinter, os, time, pygame
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from ctypes import windll

import data_handling

class GUI():
    def __init__(self, engine_client, width, height):

        self.engine_client = engine_client
        
        self.gui_width, self.gui_height = width, height

        self.top_bar_width, self.top_bar_height = self.gui_width, 25
        self.control_width, self.control_height = 250, self.gui_height - self.top_bar_height
        self.fps_graph_width = 400
        self.details_width, self.details_height = self.gui_width - self.control_width - self.fps_graph_width, 200
        self.viewer_width, self.viewer_height = self.gui_width - self.control_width, self.gui_height - self.details_height - self.top_bar_height
        self.fps_graph_height = self.details_height

        self.viewer_centre = (self.viewer_width / 2, self.viewer_height / 2, 0, 0)

        self.root = tkinter.Tk()
        self.root.withdraw()
        self.root.resizable(False, False)
        self.window = FloatingWindow(self.root)
        self.window.geometry("{}x{}+{}+{}".format(self.gui_width, self.gui_height, 200, 200))
        self.window.overrideredirect(True)
        self.window.title('FL3D Engine')
        self.window.iconbitmap('ICON.ico')

        self.gui_header_padding = 10
        self.gui_separator_padding = 50
        self.separator_dimensions = (100, 1)
        self.gui_label_padding = (25, 70)
        self.gui_slider_padding = (140, 1)
        self.gui_slider_offset = 25
        self.gui_button_padding = self.gui_label_padding[0] + 4, self.gui_label_padding[1] + self.gui_slider_offset * 5.5
        self.gui_long_slider_offset = self.gui_label_padding[0] + 4, self.gui_label_padding[1] + self.gui_slider_offset * 11.5
        self.gui_long_slider_padding = 25 
        self.gui_button_offset = 40
        self.gui_exit_button_size = (30, 30)
        self.gui_max_label_padding = 15
        self.gui_min_label_padding = 15
        self.gui_one_line_label_padding = 16
        self.gui_one_line_value_padding = 32

        self.gui_bg_colour = '#171717'
        self.gui_highlight_bg_colour = '#2b2b2b'
        self.gui_hover_bg_colour = '#3b3b3b'
        self.gui_fg_colour = '#9021ff'
        self.gui_highlight_fg_colour = '#962cd4'
        self.gui_hover_fg_colour = '#b44df0'
        self.gui_window_title_colour = '#ababab'
        self.gui_header_colour = '#ffffff'
        self.gui_translation_lines_colour_x = (233, 118, 16)
        self.gui_translation_lines_colour_y = (144, 33, 255)

        self.graph_colour = '#ffffff'
        self.max_min_graph_colour = '#474747'
        self.avg_graph_colour = '#9021ff'

        self.graph_line_width = 1.5
        self.max_min_line_width = 0.75
        self.avg_line_width = 0.75

        self.gui_header_font = ('Montserrat SemiBold', '16')
        self.gui_label_font = ('Montserrat Regular', '10')
        self.gui_button_font = ('Montserrat Medium', '10')
        self.gui_window_title_font = ('Montserrat Medium', '10')

        self.top_bar = tkinter.Frame(self.window, bg = self.gui_bg_colour, width = self.top_bar_width, height = self.top_bar_height)
        self.top_bar.pack(side = 'top')
        self.control = tkinter.Frame(self.window, bg = self.gui_bg_colour, width = self.control_width, height = self.control_height)
        self.control.pack(side = 'right')
        self.viewer = tkinter.Frame(self.window, width = self.viewer_width, height = self.viewer_height)
        self.viewer.pack(side = 'top')
        self.details = tkinter.Frame(self.window, bg = self.gui_bg_colour, width = self.details_width, height = self.details_height)
        self.details.pack(side = 'right')
        self.fps_graph = tkinter.Frame(self.window, width = self.fps_graph_width, height = self.fps_graph_height)
        self.fps_graph.pack(side = 'left')
        self.maximise_window = True

        self.top_bar.bind("<Map>", self.engine_client.maximise_window) # Used to properly maximise and minimise the window

        self.fps_viewer = plt.Figure(figsize=(4,2), dpi=100)
        self.fps_plot = self.fps_viewer.add_subplot(111)
        self.fps_viewer.subplots_adjust(bottom = 0.1, top = 0.9, right = 1.05, left= 0)
        self.fps_viewer.set_facecolor(self.gui_bg_colour)
        self.fps_plot.set_facecolor(self.gui_bg_colour)
        self.fps_plot.axis('off')

        chart_type = FigureCanvasTkAgg(self.fps_viewer, self.fps_graph)
        chart_type.get_tk_widget().pack()

        os.environ['SDL_VIDEODRIVER'] = 'windib'
        os.environ['SDL_WINDOWID'] = str(self.viewer.winfo_id()) # Used to embed pygame window in tkinter

        self.GWL_EXSTYLE=-20
        self.WS_EX_APPWINDOW=0x00040000
        self.WS_EX_TOOLWINDOW=0x00000080 # Used to show icon in task bar when in default window mode

        self.window.create_grip(self.top_bar)
        self.construct_gui()

    def set_appwindow(self):
        hwnd = windll.user32.GetParent(self.window.winfo_id())
        style = windll.user32.GetWindowLongW(hwnd, self.GWL_EXSTYLE)
        style = style & ~self.WS_EX_TOOLWINDOW
        style = style | self.WS_EX_APPWINDOW
        res = windll.user32.SetWindowLongW(hwnd, self.GWL_EXSTYLE, style)
        self.window.withdraw()
        self.window.after(10, lambda: self.window.deiconify())

    def construct_gui(self):
        self.construct_top_bar()
        self.construct_control_panel()
        self.construct_details_panel()
        self.construct_fps_graph_labels()

    def destruct_gui(self):
        self.root.quit()
        plt.close()

    def hover_enter_exit_buttom(self, event):
        self.exit_button['bg'] = self.gui_hover_bg_colour

    def hover_leave_exit_buttom(self, event):
        self.exit_button['bg'] = self.gui_bg_colour

    def hover_enter_close_buttom(self, event):
        self.close_button['bg'] = self.gui_hover_bg_colour

    def hover_leave_close_buttom(self, event):
        self.close_button['bg'] = self.gui_bg_colour

    def hover_enter_import_buttom(self, event):
        self.import_objects_button['bg'] = self.gui_hover_fg_colour

    def hover_leave_import_buttom(self, event):
        self.import_objects_button['bg'] = self.gui_fg_colour

    def hover_enter_clear_buttom(self, event):
        self.clear_worldspace_button['bg'] = self.gui_hover_fg_colour

    def hover_leave_clear_buttom(self, event):
        self.clear_worldspace_button['bg'] = self.gui_fg_colour

    def construct_top_bar(self):

        self.gui_top_bar_button_padding = 10

        self.exit_img = ImageTk.PhotoImage(file = 'EXIT.png')
        self.exit_button = tkinter.Button(self.top_bar, text = "Exit", width = self.gui_exit_button_size[0], height = self.gui_exit_button_size[1], command = self.engine_client.close_window, borderwidth=0, bd = -2, bg = self.gui_bg_colour, activebackground=self.gui_highlight_bg_colour)
        self.exit_button.config(image = self.exit_img)
        self.exit_button.place(x = self.gui_width - self.gui_exit_button_size[0], y = -3, anchor = 'nw')

        self.close_img = ImageTk.PhotoImage(file = 'CLOSE.png')
        self.close_button = tkinter.Button(self.top_bar, text = "Close", width = self.gui_exit_button_size[0], height = self.gui_exit_button_size[1], command = self.engine_client.minimise_window, borderwidth=0, bd = -2, bg = self.gui_bg_colour, activebackground=self.gui_highlight_bg_colour)
        self.close_button.config(image = self.close_img)
        self.close_button.place(x = self.gui_width - self.gui_exit_button_size[0] * 2 - self.gui_top_bar_button_padding, y = -3, anchor = 'nw')

        self.window_title = tkinter.Label(self.top_bar, text='FL3D Rendering Engine', bg=self.gui_bg_colour, fg=self.gui_window_title_colour, font=self.gui_window_title_font)
        self.window_title.place(x = self.gui_width / 2, y = 0, anchor = 'n')
        self.window.create_grip(self.window_title)

        self.exit_button.bind('<Enter>', self.hover_enter_exit_buttom)
        self.exit_button.bind('<Leave>', self.hover_leave_exit_buttom)
        self.close_button.bind('<Enter>', self.hover_enter_close_buttom)
        self.close_button.bind('<Leave>', self.hover_leave_close_buttom)

    def construct_control_panel(self):

        controls_header = tkinter.Label(self.control, text='ENGINE SETTINGS', bg=self.gui_bg_colour, fg=self.gui_header_colour, font=self.gui_header_font)
        controls_header.place(x = self.control_width / 2, y = self.gui_header_padding, anchor = 'n')

        separator_canvas = tkinter.Canvas(self.control, width = self.separator_dimensions[0], height = self.separator_dimensions[1], bg = self.gui_bg_colour, bd = 0, highlightthickness=0)
        separator_canvas.place(x = (self.control_width - self.separator_dimensions[0]) / 2, y = self.gui_separator_padding)
        separator = separator_canvas.create_line(0, 0, self.separator_dimensions[0], 0, fill = self.gui_fg_colour)

        self.construct_binary_sliders()
        self.construct_buttons()
        self.construct_linear_sliders()

    def construct_details_panel(self):
        pass

    def construct_fps_graph_labels(self):
        self.max_fps_label = tkinter.Label(self.details, text='Max FPS: {}'.format(0), bg=self.gui_bg_colour, fg=self.gui_window_title_colour, font=self.gui_label_font)
        self.max_fps_label.place(x = 0, y = self.gui_max_label_padding, anchor = 'nw')
        self.min_fps_label = tkinter.Label(self.details, text='Min FPS: {}'.format(0), bg=self.gui_bg_colour, fg=self.gui_window_title_colour, font=self.gui_label_font)
        self.min_fps_label.place(x = 0, y = self.details_height - self.gui_min_label_padding, anchor = 'sw')
        self.avg_fps_label = tkinter.Label(self.details, text='Mean FPS: {}'.format(0), bg=self.gui_bg_colour, fg=self.gui_window_title_colour, font=self.gui_label_font)
        self.avg_fps_label.place(x = 0, y = self.details_height / 2, anchor = 'w')

    def construct_binary_sliders(self):
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

        display_hud_label = tkinter.Label(self.control, text='Display HUD', bg=self.gui_bg_colour, fg=self.gui_window_title_colour, font=self.gui_label_font)
        display_hud_label.place(x = self.gui_label_padding[0], y = self.gui_label_padding[1] + self.gui_slider_offset * 5, anchor = 'w')
        display_hud_slider = tkinter.Scale(self.control, orient=tkinter.HORIZONTAL, length=50, width=15, sliderlength=15, from_=0, to=1, bg=self.gui_fg_colour, bd=0, borderwidth=0, activebackground=self.gui_highlight_fg_colour, highlightthickness=0, sliderrelief="flat", showvalue=0, troughcolor="#333333", command = self.update_display_hud)
        display_hud_slider.set(1)
        display_hud_slider.place(x=self.gui_label_padding[0] + self.gui_slider_padding[0], y = self.gui_label_padding[1] + self.gui_slider_padding[1] + self.gui_slider_offset * 5, anchor = 'w')

        display_logo_label = tkinter.Label(self.control, text='Display Logo', bg=self.gui_bg_colour, fg=self.gui_window_title_colour, font=self.gui_label_font)
        display_logo_label.place(x = self.gui_label_padding[0], y = self.gui_label_padding[1] + self.gui_slider_offset * 6, anchor = 'w')
        display_logo_slider = tkinter.Scale(self.control, orient=tkinter.HORIZONTAL, length=50, width=15, sliderlength=15, from_=0, to=1, bg=self.gui_fg_colour, bd=0, borderwidth=0, activebackground=self.gui_highlight_fg_colour, highlightthickness=0, sliderrelief="flat", showvalue=0, troughcolor="#333333", command = self.update_display_logo)
        display_logo_slider.set(1)
        display_logo_slider.place(x=self.gui_label_padding[0] + self.gui_slider_padding[0], y = self.gui_label_padding[1] + self.gui_slider_padding[1] + self.gui_slider_offset * 6, anchor = 'w')

    def construct_buttons(self):
        self.save_objects_button = tkinter.Button(self.control, text="Save Objects", fg="white", bg= self.gui_fg_colour, borderwidth=0, height = 1, width = 15, activebackground=self.gui_highlight_fg_colour, activeforeground="white", command= self.save_objects, font=self.gui_button_font)
        self.save_objects_button.place(x= self.control_width / 2, y = self.gui_button_padding[1] + self.gui_button_offset * 1, anchor = 'n')

        self.import_objects_button = tkinter.Button(self.control, text="Import Objects", fg="white", bg= self.gui_fg_colour, borderwidth=0, height = 1, width = 15, activebackground=self.gui_highlight_fg_colour, activeforeground="white", command= self.import_objects, font=self.gui_button_font)
        self.import_objects_button.place(x= self.control_width / 2, y = self.gui_button_padding[1] + self.gui_button_offset * 2, anchor = 'n')

        self.clear_worldspace_button = tkinter.Button(self.control, text="Clear Worldspace", fg="white", bg= self.gui_fg_colour, borderwidth=0, height = 1, width = 15, activebackground=self.gui_highlight_fg_colour, activeforeground="white", command= self.clear_worldspace, font=self.gui_button_font)
        self.clear_worldspace_button.place(x= self.control_width / 2, y = self.gui_button_padding[1] + self.gui_button_offset * 3, anchor = 'n')

        self.import_objects_button.bind('<Enter>', self.hover_enter_import_buttom)
        self.import_objects_button.bind('<Leave>', self.hover_leave_import_buttom)
        self.clear_worldspace_button.bind('<Enter>', self.hover_enter_clear_buttom)
        self.clear_worldspace_button.bind('<Leave>', self.hover_leave_clear_buttom)

    def construct_linear_sliders(self):
        rotation_factor_label = tkinter.Label(self.control, text='Rotation Factor', bg=self.gui_bg_colour, fg=self.gui_window_title_colour, font=self.gui_label_font)
        rotation_factor_label.place(x = self.gui_label_padding[0], y = self.gui_label_padding[1] + self.gui_slider_offset * 13 - self.gui_one_line_label_padding, anchor = 'w')
        self.rotation_factor_slider = tkinter.Scale(self.control, orient=tkinter.HORIZONTAL, length=185, width=10, sliderlength=10, from_= 1, to= 100, bg=self.gui_fg_colour, bd=0, borderwidth=0, activebackground=self.gui_highlight_fg_colour, highlightthickness=0, sliderrelief="flat", showvalue=0, troughcolor="#333333", command = self.update_rotation_factor)
        self.rotation_factor_slider.set(self.engine_client.rotation_factor * 100)
        self.rotation_factor_slider.place(x=self.gui_long_slider_offset[0], y = self.gui_label_padding[1] + self.gui_slider_padding[1] + self.gui_slider_offset * 13, anchor = 'w')
        self.rotation_factor_value = tkinter.Label(self.control, text='{0:.2f}'.format(self.rotation_factor_slider.get()), bg=self.gui_bg_colour, fg=self.gui_window_title_colour, font=self.gui_label_font)
        self.rotation_factor_value.place(x = self.control_width - self.gui_one_line_value_padding, y = self.gui_label_padding[1] + self.gui_slider_offset * 13 - self.gui_one_line_label_padding, anchor = 'e')

        scaling_factor_label = tkinter.Label(self.control, text='Scaling Factor', bg=self.gui_bg_colour, fg=self.gui_window_title_colour, font=self.gui_label_font)
        scaling_factor_label.place(x = self.gui_label_padding[0], y = self.gui_label_padding[1] + self.gui_slider_offset * 14.5 - self.gui_one_line_label_padding, anchor = 'w')
        self.scaling_factor_slider = tkinter.Scale(self.control, orient=tkinter.HORIZONTAL, length=185, width=10, sliderlength=10, from_= 101, to= 150, bg=self.gui_fg_colour, bd=0, borderwidth=0, activebackground=self.gui_highlight_fg_colour, highlightthickness=0, sliderrelief="flat", showvalue=0, troughcolor="#333333", command = self.update_scaling_factor)
        self.scaling_factor_slider.set(self.engine_client.scaling_factor * 100)
        self.scaling_factor_slider.place(x=self.gui_long_slider_offset[0], y = self.gui_label_padding[1] + self.gui_slider_padding[1] + self.gui_slider_offset * 14.5, anchor = 'w')
        self.scaling_factor_value = tkinter.Label(self.control, text='{0:.2f}'.format(self.scaling_factor_slider.get()), bg=self.gui_bg_colour, fg=self.gui_window_title_colour, font=self.gui_label_font)
        self.scaling_factor_value.place(x = self.control_width - self.gui_one_line_value_padding, y = self.gui_label_padding[1] + self.gui_slider_offset * 14.5 - self.gui_one_line_label_padding, anchor = 'e')

        translation_factor_label = tkinter.Label(self.control, text='Translation Factor', bg=self.gui_bg_colour, fg=self.gui_window_title_colour, font=self.gui_label_font)
        translation_factor_label.place(x = self.gui_label_padding[0], y = self.gui_label_padding[1] + self.gui_slider_offset * 16 - self.gui_one_line_label_padding, anchor = 'w')
        self.translation_factor_slider = tkinter.Scale(self.control, orient=tkinter.HORIZONTAL, length=185, width=10, sliderlength=10, from_= 1, to= 100, bg=self.gui_fg_colour, bd=0, borderwidth=0, activebackground=self.gui_highlight_fg_colour, highlightthickness=0, sliderrelief="flat", showvalue=0, troughcolor="#333333", command = self.update_translation_factor)
        self.translation_factor_slider.set(self.engine_client.translation_factor)
        self.translation_factor_slider.place(x=self.gui_long_slider_offset[0], y = self.gui_label_padding[1] + self.gui_slider_padding[1] + self.gui_slider_offset * 16, anchor = 'w')
        self.translation_factor_value = tkinter.Label(self.control, text='{0:.2f}'.format(self.translation_factor_slider.get()), bg=self.gui_bg_colour, fg=self.gui_window_title_colour, font=self.gui_label_font)
        self.translation_factor_value.place(x = self.control_width - self.gui_one_line_value_padding, y = self.gui_label_padding[1] + self.gui_slider_offset * 16 - self.gui_one_line_label_padding, anchor = 'e')

        movement_factor_label = tkinter.Label(self.control, text='Movement Factor', bg=self.gui_bg_colour, fg=self.gui_window_title_colour, font=self.gui_label_font)
        movement_factor_label.place(x = self.gui_label_padding[0], y = self.gui_label_padding[1] + self.gui_slider_offset * 17.5 - self.gui_one_line_label_padding, anchor = 'w')
        self.movement_factor_slider = tkinter.Scale(self.control, orient=tkinter.HORIZONTAL, length=185, width=10, sliderlength=10, from_= 1, to= 200, bg=self.gui_fg_colour, bd=0, borderwidth=0, activebackground=self.gui_highlight_fg_colour, highlightthickness=0, sliderrelief="flat", showvalue=0, troughcolor="#333333", command = self.update_movement_factor)
        self.movement_factor_slider.set(self.engine_client.movement_factor)
        self.movement_factor_slider.place(x=self.gui_long_slider_offset[0], y = self.gui_label_padding[1] + self.gui_slider_padding[1] + self.gui_slider_offset * 17.5, anchor = 'w')
        self.movement_factor_value = tkinter.Label(self.control, text='{0:.2f}'.format(self.movement_factor_slider.get()), bg=self.gui_bg_colour, fg=self.gui_window_title_colour, font=self.gui_label_font)
        self.movement_factor_value.place(x = self.control_width - self.gui_one_line_value_padding, y = self.gui_label_padding[1] + self.gui_slider_offset * 17.5 - self.gui_one_line_label_padding, anchor = 'e')

        max_frame_rate_label = tkinter.Label(self.control, text='Max Frame Rate', bg=self.gui_bg_colour, fg=self.gui_window_title_colour, font=self.gui_label_font)
        max_frame_rate_label.place(x = self.gui_label_padding[0], y = self.gui_label_padding[1] + self.gui_slider_offset * 19 - self.gui_one_line_label_padding, anchor = 'w')
        self.max_frame_rate_slider = tkinter.Scale(self.control, orient=tkinter.HORIZONTAL, length=185, width=10, sliderlength=10, from_= 1, to= 1000, bg=self.gui_fg_colour, bd=0, borderwidth=0, activebackground=self.gui_highlight_fg_colour, highlightthickness=0, sliderrelief="flat", showvalue=0, troughcolor="#333333", command = self.update_max_frame_rate)
        self.max_frame_rate_slider.set(self.engine_client.max_frame_rate)
        self.max_frame_rate_slider.place(x=self.gui_long_slider_offset[0], y = self.gui_label_padding[1] + self.gui_slider_padding[1] + self.gui_slider_offset * 19, anchor = 'w')
        self.max_frame_rate_value = tkinter.Label(self.control, text='{0:.2f}'.format(self.max_frame_rate_slider.get()), bg=self.gui_bg_colour, fg=self.gui_window_title_colour, font=self.gui_label_font)
        self.max_frame_rate_value.place(x = self.control_width - self.gui_one_line_value_padding, y = self.gui_label_padding[1] + self.gui_slider_offset * 19 - self.gui_one_line_label_padding, anchor = 'e')

        max_render_distance_label = tkinter.Label(self.control, text='Max Render Distance', bg=self.gui_bg_colour, fg=self.gui_window_title_colour, font=self.gui_label_font)
        max_render_distance_label.place(x = self.gui_label_padding[0], y = self.gui_label_padding[1] + self.gui_slider_offset * 20.5 - self.gui_one_line_label_padding, anchor = 'w')
        self.max_render_distance_slider = tkinter.Scale(self.control, orient=tkinter.HORIZONTAL, length=185, width=10, sliderlength=10, from_= 0, to= 25, bg=self.gui_fg_colour, bd=0, borderwidth=0, activebackground=self.gui_highlight_fg_colour, highlightthickness=0, sliderrelief="flat", showvalue=0, troughcolor="#333333", command = self.update_max_render_distance)
        self.max_render_distance_slider.set(self.engine_client.max_render_distance * 100)
        self.max_render_distance_slider.place(x=self.gui_long_slider_offset[0], y = self.gui_label_padding[1] + self.gui_slider_padding[1] + self.gui_slider_offset * 20.5, anchor = 'w')
        self.max_render_distance_value = tkinter.Label(self.control, text='{0:.2f}'.format(self.max_render_distance_slider.get()), bg=self.gui_bg_colour, fg=self.gui_window_title_colour, font=self.gui_label_font)
        self.max_render_distance_value.place(x = self.control_width - self.gui_one_line_value_padding, y = self.gui_label_padding[1] + self.gui_slider_offset * 20.5 - self.gui_one_line_label_padding, anchor = 'e')

        min_render_distance_label = tkinter.Label(self.control, text='Min Render Distance', bg=self.gui_bg_colour, fg=self.gui_window_title_colour, font=self.gui_label_font)
        min_render_distance_label.place(x = self.gui_label_padding[0], y = self.gui_label_padding[1] + self.gui_slider_offset * 22 - self.gui_one_line_label_padding, anchor = 'w')
        self.min_render_distance_slider = tkinter.Scale(self.control, orient=tkinter.HORIZONTAL, length=185, width=10, sliderlength=10, from_= 100, to= 1, bg=self.gui_fg_colour, bd=0, borderwidth=0, activebackground=self.gui_highlight_fg_colour, highlightthickness=0, sliderrelief="flat", showvalue=0, troughcolor="#333333", command = self.update_min_render_distance)
        self.min_render_distance_slider.set(data_handling.div_non_zero(1, (self.engine_client.min_render_distance * 1000)))
        self.min_render_distance_slider.place(x=self.gui_long_slider_offset[0], y = self.gui_label_padding[1] + self.gui_slider_padding[1] + self.gui_slider_offset * 22, anchor = 'w')
        self.min_render_distance_value = tkinter.Label(self.control, text='{0:.2f}'.format(self.min_render_distance_slider.get()), bg=self.gui_bg_colour, fg=self.gui_window_title_colour, font=self.gui_label_font)
        self.min_render_distance_value.place(x = self.control_width - self.gui_one_line_value_padding, y = self.gui_label_padding[1] + self.gui_slider_offset * 22 - self.gui_one_line_label_padding, anchor = 'e')

        lighting_factor_label = tkinter.Label(self.control, text='Lighting Factor', bg=self.gui_bg_colour, fg=self.gui_window_title_colour, font=self.gui_label_font)
        lighting_factor_label.place(x = self.gui_label_padding[0], y = self.gui_label_padding[1] + self.gui_slider_offset * 23.5 - self.gui_one_line_label_padding, anchor = 'w')
        self.lighting_factor_slider = tkinter.Scale(self.control, orient=tkinter.HORIZONTAL, length=185, width=10, sliderlength=10, from_= 0, to= 250, bg=self.gui_fg_colour, bd=0, borderwidth=0, activebackground=self.gui_highlight_fg_colour, highlightthickness=0, sliderrelief="flat", showvalue=0, troughcolor="#333333", command = self.update_lighting_factor)
        self.lighting_factor_slider.set(self.engine_client.lighting_factor * 100)
        self.lighting_factor_slider.place(x=self.gui_long_slider_offset[0], y = self.gui_label_padding[1] + self.gui_slider_padding[1] + self.gui_slider_offset * 23.5, anchor = 'w')
        self.lighting_factor_value = tkinter.Label(self.control, text='{0:.2f}'.format(self.lighting_factor_slider.get()), bg=self.gui_bg_colour, fg=self.gui_window_title_colour, font=self.gui_label_font)
        self.lighting_factor_value.place(x = self.control_width - self.gui_one_line_value_padding, y = self.gui_label_padding[1] + self.gui_slider_offset * 23.5 - self.gui_one_line_label_padding, anchor = 'e')

        point_radius_label = tkinter.Label(self.control, text='Point Radius', bg=self.gui_bg_colour, fg=self.gui_window_title_colour, font=self.gui_label_font)
        point_radius_label.place(x = self.gui_label_padding[0], y = self.gui_label_padding[1] + self.gui_slider_offset * 25 - self.gui_one_line_label_padding, anchor = 'w')
        self.point_radius_slider = tkinter.Scale(self.control, orient=tkinter.HORIZONTAL, length=185, width=10, sliderlength=10, from_= 1, to= 10, bg=self.gui_fg_colour, bd=0, borderwidth=0, activebackground=self.gui_highlight_fg_colour, highlightthickness=0, sliderrelief="flat", showvalue=0, troughcolor="#333333", command = self.update_point_radius)
        self.point_radius_slider.set(self.engine_client.point_radius)
        self.point_radius_slider.place(x=self.gui_long_slider_offset[0], y = self.gui_label_padding[1] + self.gui_slider_padding[1] + self.gui_slider_offset * 25, anchor = 'w')
        self.point_radius_value = tkinter.Label(self.control, text='{0:.2f}'.format(self.point_radius_slider.get()), bg=self.gui_bg_colour, fg=self.gui_window_title_colour, font=self.gui_label_font)
        self.point_radius_value.place(x = self.control_width - self.gui_one_line_value_padding, y = self.gui_label_padding[1] + self.gui_slider_offset * 25 - self.gui_one_line_label_padding, anchor = 'e')

    def animate_fps_graph(self):
        fps_animation = animation.FuncAnimation(self.fps_viewer, self.update_fps_graph, interval = self.engine_client.fps_graph_interval)
        return fps_animation

    def update_fps_graph(self, x):
        fps = self.engine_client.clock.get_fps()
        if fps > 0:
            self.engine_client.time_array.append(time.time() - self.engine_client.start_time)
            self.engine_client.fps_array.append(fps)
        if len(self.engine_client.fps_array) > self.engine_client.fps_array_max_length:
            self.engine_client.fps_array = self.engine_client.fps_array[1:]
            self.engine_client.time_array = self.engine_client.time_array[1:]
        if len(self.engine_client.fps_array) > 0:
            min_fps = min(self.engine_client.fps_array)
            max_fps = max(self.engine_client.fps_array)
            avg_fps = sum(self.engine_client.fps_array) / len(self.engine_client.fps_array)
            self.fps_plot.cla()
            # Time array is changed so that only the first and last points are plotted to improve efficiency
            self.fps_plot.plot(self.engine_client.time_array, self.engine_client.fps_array, color = self.graph_colour, linewidth = self.graph_line_width / 2)
            self.fps_plot.plot((self.engine_client.time_array[0], self.engine_client.time_array[-1]), (min_fps, min_fps), color = self.max_min_graph_colour, linewidth = self.max_min_line_width)
            self.fps_plot.plot((self.engine_client.time_array[0], self.engine_client.time_array[-1]), (max_fps, max_fps), color = self.max_min_graph_colour, linewidth = self.max_min_line_width)
            self.fps_plot.plot((self.engine_client.time_array[0], self.engine_client.time_array[-1]), (avg_fps, avg_fps), color = self.avg_graph_colour, linewidth = self.avg_line_width)
            self.max_fps_label.config(text='Max FPS: {}'.format(round(max_fps,2)))
            self.min_fps_label.config(text='Min FPS: {}'.format(round(min_fps,2)))
            self.avg_fps_label.config(text='Mean FPS: {}'.format(round(avg_fps,2)))
            self.avg_fps_label.place(y = int(self.gui_max_label_padding + 12 + (data_handling.div_non_zero(max_fps - avg_fps, (max_fps - min_fps) * 1.30) * 190)))
            self.fps_plot.axis('off')

    def update_display_surfaces(self, value):
        if value == '1':
            self.engine_client.display_surfaces = True 
        elif value == '0':
            self.engine_client.display_surfaces = False

    def update_display_lines(self, value):
        if value == '1':
            self.engine_client.display_lines = True 
        elif value == '0':
            self.engine_client.display_lines = False
    
    def update_display_points(self, value):
        if value == '1':
            self.engine_client.display_points = True 
        elif value == '0':
            self.engine_client.display_points = False

    def update_debug_mode(self, value):
        if value == '1':
            self.engine_client.debug_mode = True 
        elif value == '0':
            self.engine_client.debug_mode = False

    def update_hidden_lines(self, value):
        if value == '1':
            self.engine_client.hidden_lines = True 
        elif value == '0':
            self.engine_client.hidden_lines = False
    
    def update_display_hud(self, value):
        if value == '1':
            self.engine_client.display_hud = True
        elif value == '0':
            self.engine_client.display_hud = False

    def update_display_logo(self, value):
        if value == '1':
            self.engine_client.display_logo = True
        elif value == '0':
            self.engine_client.display_logo = False
    
    def save_objects(self):
        self.engine_client.db_manager.save_objects(self.engine_client.engine.objects)

    def import_objects(self):
        self.engine_client.db_manager.import_objects(self.engine_client.engine)

    def clear_worldspace(self):
        self.engine_client.engine.clear_all_objects()

    def update_rotation_factor(self, value):
        self.engine_client.rotation_factor = int(value) / 100
        self.rotation_factor_value.config(text = '{0:.2f}'.format(self.engine_client.rotation_factor))

    def update_scaling_factor(self, value):
        self.engine_client.scaling_factor = int(value) / 100
        self.scaling_factor_value.config(text = '{0:.2f}'.format(self.engine_client.scaling_factor))

    def update_translation_factor(self, value):
        self.engine_client.translation_factor = int(value)
        self.translation_factor_value.config(text = '{0:.2f}'.format(self.engine_client.translation_factor))

    def update_movement_factor(self, value):
        self.engine_client.movement_factor = int(value)
        self.movement_factor_value.config(text = '{0:.2f}'.format(self.engine_client.movement_factor))
        pygame.key.set_repeat(1, self.engine_client.movement_factor)

    def update_max_frame_rate(self, value):
        self.engine_client.max_frame_rate = int(value)
        self.max_frame_rate_value.config(text = '{0:.2f}'.format(self.engine_client.max_frame_rate))

    def update_max_render_distance(self, value):
        self.engine_client.max_render_distance = int(value) / 100
        self.max_render_distance_value.config(text = '{0:.2f}'.format(self.engine_client.max_render_distance * 100))

    def update_min_render_distance(self, value):
        self.engine_client.min_render_distance = data_handling.div_non_zero(1, (int(value) * 1000))
        self.min_render_distance_value.config(text = '{0:.2f}'.format(self.engine_client.min_render_distance * 1000))

    def update_lighting_factor(self, value):
        self.engine_client.lighting_factor = int(value) / 100
        self.lighting_factor_value.config(text = '{0:.2f}'.format(self.engine_client.lighting_factor))

    def update_point_radius(self, value):
        self.engine_client.point_radius = int(value)
        self.point_radius_value.config(text = '{0:.2f}'.format(self.engine_client.point_radius))

class FloatingWindow(tkinter.Toplevel):
    def __init__(self, *args, **kwargs):
        tkinter.Toplevel.__init__(self, *args, **kwargs)

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

class CoordinateInput:
    def __init__(self, x, y, z):
        self.input_boxes = []
        self.input_box_y_padding = 20
        self.input_box_text = [str(x), str(y), str(z)]

        for i in range(3):
            self.input_boxes.append(InputBox(x, y + self.input_box_y_padding * i, text = self.input_box_text[i]))

    def access_input_boxes(self):
        return self.input_boxes

    def accepting_input(self):
        user_input = False
        for input_box in self.input_boxes:
            if input_box.active == True:
                user_input = True
        return user_input

class InputBox:
    def __init__(self, x, y, text=''):
        self.width, self.height = 30, 15
        self.text_box_padding = (10, 10)
        self.rect = pygame.Rect(x + self.text_box_padding[0], y + self.text_box_padding[1], self.width, self.height)
        self.text_box_active_colour = (144, 33, 255)
        self.text_box_inactive_colour = (255, 255, 255)
        self.text_box_text_colour = (255, 255, 255)
        self.input_speed = 10
        self.accepted_characters = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.', ',', ' ')
        self.text_box_font = pygame.font.Font('fonts/Montserrat-Medium.ttf', 10)

        self.color = self.text_box_inactive_colour
        self.text = text
        self.txt_surface = self.text_box_font.render(text, True, self.color)
        self.active = False

    def handle_event(self, event, movement_factor):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                #self.active = not self.active
                self.active = True
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = self.text_box_active_colour if self.active else self.text_box_inactive_colour

        if event.type == pygame.KEYDOWN:
            if self.active:
                pygame.key.set_repeat(1, self.input_speed)
                if event.key == pygame.K_RETURN:
                    print(self.text)
                    self.text = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    if event.unicode in self.accepted_characters:
                        self.text += event.unicode
                # Re-render the text.
                self.txt_surface = self.text_box_font.render(self.text, True, self.text_box_text_colour)
                pygame.key.set_repeat(1, movement_factor)

    def draw(self, screen):
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x + 1, self.rect.y + 1))
        # Blit the rect.
        pygame.draw.rect(screen, self.color, self.rect, 1)

    def resize(self):
        # Resize the box if the text is too long.
        width = max(self.width, self.txt_surface.get_width()+10)
        self.rect.w = width