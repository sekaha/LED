"""
TODO:
[ ] - scale and other functios need to work with ndarrays
[ ] - make super for canvas and Sprite, since they share many functions
[x] - refactor font
[ ] - make usage of sprite v.s. canvas consistent or at least document stuff, like with rotate and scale
[ ] - finish documentation
    [ ] - add hyperlinks to functions mentioned in doc
[x] - native surface and image rotation with rotsprite algorithm(taisetsu)
[ ] - debug messages? <<50% done>>
[x] - hypercube dimension length and rotation independent of draw
    [x] - get triangular number
[x] - transparent color? like an erase function
[x] - make set_size update window size
    [x] - auto adjust window width and height
    [ ] - condense init into functions if possible
[x] - make pipable
    [x] - make default font download? 
[x] - add logo
    [x]  - add window name
[x] - create_hypercube
[x] - create_sprite
[x] - canvas get_width and get_height
[x] - refactor sprites
[x] - put internal hidden functions inside a class, like LED.draw => def draw(): game_object.draw()
    [x] - furthermore, better OOP would be nice, esp for canvas and sprite objects
[x] - fix all canvas references, like colorize
[x] - single underscore _method()
[x] - sprite get frame count
[x] - fix origin system
[x] - bug with canvas set after canvas draw
[ ] - canvas floats instead of just 255
[ ] draw_polygon (filled)
[ ] - put numpy somewhere else besides global ffs
[ ] - get rgba
    [x] - get_red get_blue etc for ndarray image processing of surfaces
    [ ] - get_hsv for that too
    [x] - make black and white cavases display natively from the r g b
[x] - make colorize work with just arrays, cast to surface, etc
[ ] - rotate 3D and also perspective and also 3 tuple point support, enable_perspective()
[ ] - json for default settings that can be changed for the system
[ ] - draw_polygon and draw_triangle, draw bézier? triangle fan
[ ] - redo pixel sending now that I know numpy
[ ] - make set_canvas stack based TBH???
[ ] - make text a canvas subclass... create_text()
[ ] - color key
[ ] - convert canvas model to NP arrays, sprite model too
    [ ] - .refresh
    [ ] - add slice support in canvas, use in LEDoom
    [ ] - perhaps switch draw_pixel => array set, if it's faster, 255 alpha, etc
    [ ] - make pixel array, so methods like color_hsv() work inside of it by default, so you can parallelize pixel stuff
        [ ] - also colorize() and rotate() need to take numpy arrays and auto convert them
    [ ] - make color_hsv et all numpy compatible
    [ ] - make merge_palette work across np array
[ ] - check convert_alpha needed for scale rotate colorize etc
    [ ] - perhaps rotate sprite needs to rotate an entire sprite and return it, that may have
          some design considerations though
[ ] - support unicode input for key_pressed et al
[ ] - set_alpha breaks blend
[ ] - get hue, saturation, and value from rgb color
[ ] - hexadecimal color is broken for colorize()
[ ] - make rgb (255,256,255) safe, e.g. numbs above 255
[x] - mouse_x,y,keyboardinputdesu
    [ ] - joystick_connected check
    [x] - joystick input
    [ ] - joystick xbox and ps4 check?
    [x] - joystick device environments
    [ ] - joystick get_count
    [ ] - stream line console-like keyboard input
[ ] - use assert instead of print
[ ] - maybe we ought to change over SDL2 instead of pygame
[ ] - math package, draw_grid, draw_arrow, point class? bézier curve
    [ ] - vector rotate, 3d maths stuff
[ ] - fix bug where LED.set_size doesn't work well after set_orientation()
[x] - window scale settings
[ ] - rotate screen
[ ] - limit mouse x and y to screen?
[ ] - hexcode color support
    [ ] - colorize doesn't work with 0x
    [ ] - merge palette and merge_color needs to work with this too
[ ] - convert_hsv()
	[ ] - convert rgb()
[ ] - make full stack website
[ ] - use numeric python for rotating the grid?
[ ] - scale
[ ] - fix LED logo
[ ] - not even sure this is possible, but remove/limit sprite shaking when rotating
[ ] - get hue, etc
[ ] - add scaling, fix origin for scaling
	[ ] - is center origin backwards? -- yes :0
	[ ] - fix origins and rotations, including not resetting them after colorize rotation 		      etc
[ ] - draw circle and square outline
[ ]  - get canvas ----- canvas stack
[ ] - make LED sim optional, send _pixels only instead
[x] - add smaller minimal font
[x] - update get_delta to care about _frame_ rather than last call
[x] - enable/disable display
[ ] - center_origin() should return the object unless . is used
[ ] - default debug window??? enable_debug
[ ] - switch to shader code? this may be good for performance on 3D graphics
    this would require shader code => buffer surface => numpy array
    realistically I would still need numpy
    [ ] - so batch processing? for pixels etc
[ ] - specify transparency via  vec4???
[ ] - set mouse x
[ ] - reset blend mode? ON GOD
[ ] - get key pressed any???? and such
[x] - has sin and cos leaked?
we're done with this _finally!_
"""

import struct
import socket
import numpy as np
import pygame
from pygame._sdl2.video import Window
import os
import time
import math
from PIL import Image

pygame.init()

# COLORS

# normal
RED = (255, 0, 0)
ORANGE = (255, 127, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
FUCHSIA = (255, 0, 255)
PURPLE = (127, 0, 255)
BROWN = (192, 128, 96)

WHITE = (255, 255, 255)
SILVER = (196, 196, 196)
GREY = (127, 127, 127)
BLACK = (0, 0, 0)

TRANSPARENT = pygame.SRCALPHA

########################################################################
############### INTERNAL CLASSES USED BY THE GAME ENGINE ###############
########################################################################

############### SPRITE ###############

# used in sprite updates
_animated_sprites = []


def _update_sprites():
    for sprite in _animated_sprites:
        sprite.frame = (sprite.frame + (sprite.frame_rate / _game_speed)) % len(
            sprite.frames
        )


class Sprite:
    # sprite collects and points to canvases
    def __init__(self, filename="", origin_x=0, origin_y=0):
        # image index and image speed
        self.frames = []
        self.frame = 0
        self.frame_rate = 0
        self.frame_offset = 0
        self.origin_x = origin_x
        self.origin_y = origin_y
        self.angle = 0
        self.img_scale = 1
        self.width = 0
        self.height = 0

        if filename != "":
            try:
                image = pygame.image.load(filename)
                self.origin_x, self.origin_y = origin_x, origin_y
                image = image.convert_alpha()

                self.frames.append(Canvas(0, 0, origin_x, origin_y, image))
                self.width = self.frames[0].get_width()
                self.height = self.frames[0].get_height()
            except pygame.error as e:
                print(f"Unable to load {filename}")
                raise SystemExit(e)

    def __getitem__(self, key):
        if isinstance(key, tuple):
            return self.get_current_frame()[key]
        else:
            return self.frames[key % len(self.frames)]

    def __setitem__(self, key, canvas):
        self.frames[key % len(self.frames)] = canvas

    def __eq__(self, other):
        return (self.get_rgb() == other.get_rgb()).all()

    def set_frame(self, frame):
        self.frame = frame

    def get_ndarray(self):
        return self.get_current_frame().get_ndarray()

    def get_frame(self):
        return math.floor(self.frame + self.frame_offset) % len(self.frames)

    def get_current_frame(self):
        return self.frames[self.get_frame()]

    def append(self, canvas):
        if (type(canvas) == Sprite) or (type(canvas) == Canvas) or (type(canvas)):
            self.frames.append(canvas)
        else:
            raise TypeError(f"cannot append non-canvas object of type {type(canvas)}")

    def center_origin(self):
        self.origin_x = self.width / 2
        self.origin_y = self.height / 2

        for frame in self.frames:
            frame.set_origin(self.origin_x, self.origin_y)

    def set_origin(self, x, y):
        self.origin_x = x
        self.origin_y = y

        for frame in self.frames:
            frame.set_origin(self.origin_x, self.origin_y)

    def set_origin_x(self, x):
        self.origin_x = x

        for frame in self.frames:
            frame.set_origin(self.origin_x, self.origin_y)

    def set_origin_y(self, y):
        self.origin_y = y

        for frame in self.frames:
            frame.set_origin(self.origin_x, self.origin_y)

    def get_origin_x(self):
        return self.origin_x

    def get_origin_y(self):
        return self.origin_y

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def rotate(self, angle):
        self.angle = angle
        self.get_current_frame().rotate(angle)

    def get_angle(self):
        return self.angle

    def scale(self, scale):
        self.img_scale = img_scale

    def get_scale(self):
        return self.img_scale

    def set_frame_rate(self, frame_rate):
        if frame_rate == 0:
            # if the frame rate is now zero, don't update this sprite
            if _animated_sprites.count(self) > 0:
                _animated_sprites.remove(self)

        # if the frame rate is now more than 0 and the sprite isn't already set to be updated
        # put it in the update list
        elif _animated_sprites.count(self) < 1:
            _animated_sprites.append(self)
        self.frame_rate = frame_rate

    def get_frame_rate(self):
        return self.frame_rate

    def get_frame_count(self):
        return len(self.frames)

    def get_rgb(self):
        return pygame.surfarray.array3d(self.get_current_frame().surface)

    def get_rgba(self):
        return np.dstack((self.get_rgb(), self.get_alpha()))

    def get_red(self):
        return np.dsplit(self.get_rgb(), 3)[0]

    def get_green(self):
        return np.dsplit(self.get_rgb(), 3)[1]

    def get_blue(self):
        return np.dsplit(self.get_rgb(), 3)[2]

    def get_alpha(self):
        return pygame.surfarray.array_alpha(self.get_frame().surface)

    def trim(self, x, y, w, h):
        canvas = self.get_current_frame().surface

        # Loads image from x, y, x+offset, y+offset.
        rect = pygame.Rect((x, y, w, h))
        image = pygame.Surface(rect.size).convert_alpha()
        image.blit(canvas, (0, 0), rect)
        return Canvas(0, 0, 0, 0, image)


############### CANVAS ###############

# pygame.surfarray.pixels3d


class Canvas:
    def __init__(self, width, height, origin_x=0, origin_y=0, surface=None):
        self.origin_x = origin_x
        self.origin_y = origin_y
        self.angle = 0
        self.cnv_scale = 1

        self.scaled8x = None

        # need image data to be set
        if surface == None:
            # self.surface = pygame.surfarray.pixels2dnp.full((width, height), pygame.SRCALPHA)
            self.surface = pygame.Surface((width, height), pygame.SRCALPHA)
        else:
            self.surface = surface
        self.width = self.surface.get_width()
        self.height = self.surface.get_height()
        # self.surface_array = pygame.surfarray.pixels3d(self.surface)

    def export(self, file_name):
        image = Image.fromarray(np.uint8(self.get_ndarray()))
        image.save(file_name)

    def refresh(self, color=TRANSPARENT):
        self.surface.fill(color)

    def center_origin(self):
        self.origin_x = self.width / 2
        self.origin_y = self.height / 2

    def set_origin(self, x, y):
        self.origin_x = x
        self.origin_y = y

    def __setitem__(self, coords, col):
        x_key, y_key = math.floor(coords[0]), math.floor(coords[1])
        return self.surface.set_at((x_key % self.width, y_key % self.height), col)

    def __getitem__(self, coords):
        x_key, y_key = math.floor(coords[0]), math.floor(coords[1])
        col = self.surface.get_at((x_key % self.width, y_key % self.height))
        return (col.r, col.g, col.b, col.a)

    def compare(self, other):
        return (self.get_rgb() == other.get_rgb()).all()

    def set_origin_x(self, x):
        self.origin_x = x

    def set_origin_y(self, y):
        self.origin_y = y

    def get_origin_x(self):
        return self.origin_x

    def get_origin_y(self):
        return self.origin_y

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def get_ndarray(self):
        return pygame.surfarray.array3d(self.surface)

    def get_rgb(self):
        return pygame.surfarray.array3d(self.surface)

    def get_rgba(self):
        return np.dstack((self.get_rgb(), self.get_alpha()))

    def get_red(self):
        return np.dsplit(self.get_rgb(), 3)[0]

    def get_green(self):
        return np.dsplit(self.get_rgb(), 3)[1]

    def get_blue(self):
        return np.dsplit(self.get_rgb(), 3)[2]

    def get_alpha(self):
        return pygame.surfarray.array_alpha(self.surface)

    def rotate(self, angle):
        self.angle = angle

    def get_angle(self):
        return self.angle

    # def scale(self, scale):
    #    self.cnv_scale = cnv_scale

    def get_scale(self):
        return self.cnv_scale

    def get_updated_canvas(self):
        return self
        # iterations = 3
        # limititng calculation times for 90 degrees, since we don't need to do rotsprite then
        # if (self.angle % 90 == 0):
        #    rotated_image = pygame.transform.rotate(self.surface, -self.angle)
        #    scaled_image = pygame.transform.scale(rotated_image,(self.get_width()*self.get_scale(),self.get_height()*self.get_scale()))
        #    new_canvas = Canvas(0, 0, self.origin_x*self.get_scale(),
        #                            self.origin_y*self.get_scale(), scaled_image)
        # else:
        #    # scale the image up 8x, this gives us a better resolution to rotate with
        #    new_scale = 2**iterations
        #    scaled_canvas = self.surface

        #    if self.scaled8x == None:
        #        print("made new one")
        #        for i in range(iterations):
        #            scaled_canvas = pygame.transform.scale2x(scaled_canvas)
        #        self.scaled8x = scaled_canvas

        #    rotated_image = pygame.transform.rotate(self.scaled8x, -self.angle)

        #    # create a new image to draw the rotated and scaled sprite to
        #    new_image = pygame.Surface(
        #        (rotated_image.get_width(), rotated_image.get_height()), pygame.SRCALPHA)
        #    new_image.blit(rotated_image, (0, 0))

        #    # scale the image back down using a nearest neighbor algorithm
        #    new_width  = rotated_image.get_width()/new_scale*self.get_scale()
        #    new_height = rotated_image.get_height()/new_scale*self.get_scale()
        #    new_canvas = Canvas(0, 0, self.origin_x*self.get_scale(), self.origin_y*self.get_scale(),
        #                            pygame.transform.scale(new_image, (new_width, new_height)))

        ## offset the pivot from center
        # image_rect = self.surface.get_rect(topleft=(-self.origin_x*self.get_scale(), -self.origin_y*self.get_scale()))
        # offset = (-image_rect.center[0], -image_rect.center[1])

        ## determine rotation from center using a rotation matrix
        ## more here: https://en.wikipedia.org/wiki/Rotation_matrix
        # rad = math.radians(self.angle)
        # x, y, c, s = offset[0], offset[1], math.cos(rad), math.sin(rad)
        # rot_x, rot_y = c*x - s*y, s*x + c*y

        ## maintain an origin for drawing correctly
        # rot_image_center = (-rot_x,-rot_y)
        # new_rect = new_canvas.surface.get_rect(center=rot_image_center)
        # new_canvas.set_origin(-new_rect.topleft[0], -new_rect.topleft[1])

        # return new_canvas

    def trim(self, x, y, w, h):
        surface = self.surface

        # Loads image from x, y, x+offset, y+offset.
        rect = pygame.Rect((x, y, w, h))
        image = pygame.Surface(rect.size, pygame.SRCALPHA)
        image.blit(surface, (0, 0), rect)

        return Canvas(0, 0, 0, 0, image)


############### FAST OPC ###############

# SENDS PACKETS TO THE GRID


class _FastOPC(object):
    """High-performance Open Pixel Control client, using Numeric Python.
    By default, assumes the OPC server is running on localhost. This may be
    overridden with the OPC_SERVER environment variable, or the 'server'
    keyword argument.
    """

    def __init__(self, server=None):
        self.server = server or os.getenv("OPC_SERVER") or "127.0.0.1:7890"
        self.host, port = self.server.split(":")
        self.port = int(port)
        self.socket = None

    def send(self, packet):
        """Send a low-level packet to the OPC server, connecting if necessary
        and handling disconnects. Returns True on success.
        """
        if self.socket is None:
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.host, self.port))
                self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
            except socket.error:
                self.socket = None

        if self.socket is not None:
            try:
                self.socket.send(packet)
                return True
            except socket.error:
                self.socket = None

        # Limit CPU usage when polling for a server
        time.sleep(0.1)

        return False

    def send_pixels(self, channel, *sources):
        """Send a list of 8-bit colors to the indicated channel.
        (OPC command 0x00). This command accepts a list of pixel sources,
        which are concatenated and sent. Pixel sources may be:
            - Strings or buffer objects containing pre-formatted 8-bit RGB
              pixel data
            - NumPy arrays or sequences containing 8-bit RGB pixel data.
              If values are out of range, the array is modified.
        """
        rgbvals = []
        numvals = 0

        for source in sources:
            if isinstance(source, list):
                source = [x for rgb in source for x in rgb]  # flatten the list
            elif isinstance(source, np.ndarray):
                source = source.tolist()  # convert (assumed flat) NumPy array to a list

            def clamp(x):
                return max(min(255, int(x)), 0)

            source = [clamp(x) for x in source]

            rgbvals.extend(source)
            numvals += len(source)

        # returns a bytes object
        header = struct.pack(">BBH", channel, 0, numvals)
        message = header + bytes(rgbvals)
        self.send(message)


############## HYPERCUBE ##############


class _Hypercube:
    def __init__(self, dimensions):
        if dimensions > 10:
            raise Exception("hypercube may not exceed 10 dimensions")
            # why you may ask? well it's slow haha

        class Point:
            def __init__(self):
                self.coords = []
                self.transforms = []

        class Edge:
            def __init__(self):
                self.endpoints = ()  # (a,b)

        class Plane:
            def __init__(self):
                self.axes = ()
                self.rotation = 0

        # Creating the points #
        self.dimensions = dimensions
        self.points = []
        points_num = math.floor(2**dimensions)

        def get_axis_coord(x):
            return 1 if (math.floor(x / (2**axis)) % 2 == 1) else -1

        # adding every point needed for the hypercube and setting its position
        for point in range(points_num):
            temp_point = Point()
            self.points.append(temp_point)

            # assigns -1 or 1 for x y z w etc, each corner, depending on the axis
            for axis in range(dimensions):
                temp_point.coords.append(get_axis_coord(point))
                temp_point.transforms.append(0)

        # Creating the edges
        self.edges = []
        end = 0

        # Go through all points and compare to find perpendicular shapes
        for vertex_a_num in range(len(self.points)):
            for vertex_b_num in range(end):
                similar_coords = 0
                vertex_a = self.points[vertex_a_num]
                vertex_b = self.points[vertex_b_num]

                # Find points with dimensions-1 number of similar cords, connect edges
                for axis in range(dimensions):
                    if vertex_a.coords[axis] == vertex_b.coords[axis]:
                        similar_coords += 1
                    if similar_coords == dimensions - 1:
                        temp_edge = Edge()
                        temp_edge.endpoints = (vertex_a, vertex_b)
                        self.edges.append(temp_edge)
            end += 1

        # Creating planes of rotation, 2d = 1, 3d = 3, 4d = 6, triangle number (n+n^2)/2
        self.planes = []
        end = 0

        # Assign a rotation to every plane parallel to two axes and through the origin, 2d x-y, 3d xy xz yz, etc
        for axis_a in range(dimensions):
            for axis_b in range(end):
                temp_plane = Plane()
                temp_plane.axes = (axis_a, axis_b)
                self.planes.append(temp_plane)
            end += 1

    def __str__(self):
        return "rotations: " + ", ".join([str(plane.rotation) for plane in self.planes])

    def __setitem__(self, index, rot):
        self.planes[index].rotation = rot

    def __getitem__(self, index):
        return self.planes[index].rotation

    def set_rotation(self, rotations):
        for pos, rotation in enumerate(rotations):
            self.planes[pos].rotation = rotation

    def get_rotation(self):
        return [plane.rotation for plane in self.planes]

    def get_dimensions(self):
        return self.dimensions


###############################################
############### THE GAME ENGINE ###############
###############################################


############## DEFAULT VARIABLES ##############

# Window Settings
pygame.display.set_icon(
    pygame.image.load(os.path.dirname(os.path.abspath(__file__)) + "/icon.png")
)
pygame.display.set_caption(f"LED Simulator")

# SERVER
_CLIENT = _FastOPC()
_networked = False

# GRID HARDWARE SETTINGS
_WIDTH = 60
_HEIGHT = 80
_NUMLEDS = _WIDTH * _HEIGHT
_pixels = [(0, 0, 0)] * _NUMLEDS
screen_x_flip = False
screen_y_flip = False

# _orientation
_orientation = 0  # 1 horizontal, 0 vertical with the current grid set up
_brightness = 1

# INTERNAL DRAWING VARIABLES
_GAME_SCREEN = Canvas(0, 0, 0, 0, pygame.Surface((_WIDTH, _HEIGHT)))
_BLEND_SCREEN = Canvas(0, 0, 0, 0, pygame.Surface((_WIDTH, _HEIGHT), pygame.SRCALPHA))
_internal_canvas = _GAME_SCREEN
_current_canvas = _GAME_SCREEN
_canvas_stack = [_internal_canvas]
_alpha = 255
_background_color = (0, 0, 0)

# blend modes
BM_NORMAL = 0
BM_ADD = pygame.BLEND_ADD
BM_SUBTRACT = pygame.BLEND_SUB
BM_MAX = pygame.BLEND_MAX
_blend_mode = BM_NORMAL

# text variables
FNT_NORMAL = (os.path.dirname(os.path.abspath(__file__)) + "/Kaku.ttf", 16)
FNT_SMALL = (os.path.dirname(os.path.abspath(__file__)) + "/m3x6.ttf", 8)
FNT_LARGE = (os.path.dirname(os.path.abspath(__file__)) + "/CozetteVector.ttf", 8)

_default_font = FNT_NORMAL
_h_text_alignment = 0
_v_text_alignment = 0

_LEFT = 0
_CENTER_HORIZONTAL = 1
_RIGHT = 2
_TOP = 0
_CENTER_VERTICAL = 1
_BOTTOM = 2

# FPS
_game_speed = 120
_true_game_speed = 120
_prev_time = time.time()
_cur_time = 0
_clock = pygame.time.Clock()

# WINDOW GUI
_WINDOW_SCALE = 12  # FACTOR TO _WINDOW_SCALE FOR GUI
_WINDOW_WIDTH = _WIDTH * _WINDOW_SCALE
_WINDOW_HEIGHT = _HEIGHT * _WINDOW_SCALE
_SCREEN = pygame.display.set_mode((_WINDOW_WIDTH, _WINDOW_HEIGHT))  # None #

# Keyboard and mouse input
_key_held = pygame.key.get_pressed()
_key_pressed = []
_key_released = []
_key_input = []
_mouse_pressed = []
_mouse_released = []
_mouse_x = 0
_mouse_y = 0

# joystick input
_joysticks = {}
_joystick_pressed = []
_joystick_released = []
_joystick_dpad = None
_joystick_dpad_pressed = []
_joystick_dpad_released = []
_deadzone = 0.2
_joystick_environment = 0

# button constants
JS_FACE0 = 0
JS_FACE1 = 1
JS_FACE2 = 2
JS_FACE3 = 3
JS_L1 = 4
JS_R1 = 5
JS_L2 = 6
JS_R2 = 7
JS_SELECT = 8
JS_START = 9
JS_LSTICK = 11
JS_RSTICK = 12
JS_PADU = 13
JS_PADD = 14
JS_PADL = 15
JS_PADR = 16

############### GRID SETTINGS ###############

# NETWORKING AND GRID SETUP


def grid_config(address, width, height, _orientation, _brightness):
    set_server(address)
    set_width(width)
    set_height(height)
    set_orientation(_orientation)
    set_brightness(_brightness)


def set_server(address):
    global _CLIENT
    _CLIENT = _FastOPC(address)


def disable_networking():
    global _networked
    _networked = False


def enable_networking():
    global _networked
    _networked = True


# ORIENTATION
def set_orientation(new_orientation):
    global _orientation
    global _current_canvas
    global _GAME_SCREEN
    global _internal_canvas
    global _BLEND_SCREEN
    global _SCREEN

    _orientation = new_orientation % 4
    _update_window()
    # _NUMLEDS = _WIDTH * _HEIGHT
    # _pixels = [(0, 0, 0)] * _NUMLEDS


def get_orientation():
    return _orientation


# BRIGHTNESS


def set_brightness(new_brightness):
    global _brightness
    _brightness = new_brightness


def get_brightness():
    global _brightness
    return _brightness


# GRID SIZE CONTROLS


# Normal size controls
def set_width(new_width):
    global _WIDTH
    _WIDTH = int(new_width)
    _update_window()


def get_width():
    global _WIDTH
    return _WIDTH


def set_height(new_height):
    global _HEIGHT
    _HEIGHT = int(new_height)
    _update_window()


def get_height():
    global _HEIGHT
    return _HEIGHT


# Adjusted sizes


def set_width_adjusted(new_width):
    if _orientation % 2 == 0:
        global _WIDTH
        _WIDTH = int(new_width)
    else:
        global _HEIGHT
        _HEIGHT = int(new_width)
    _update_window()


def get_width_adjusted():
    if _orientation % 2 == 0:
        global _WIDTH
        return _WIDTH
    else:
        global _HEIGHT
        return _HEIGHT


def set_height_adjusted(new_height):
    if _orientation % 2 == 0:
        global _HEIGHT
        _HEIGHT = int(new_height)
    else:
        global _WIDTH
        _WIDTH = int(new_height)
    _update_window()


def get_height_adjusted():
    if _orientation % 2 == 0:
        global _HEIGHT
        return _HEIGHT
    else:
        global _WIDTH
        return _WIDTH


def flip_screen_x():
    global screen_x_flip
    screen_x_flip = 1 - screen_x_flip


def flip_screen_y():
    global screen_y_flip
    screen_y_flip = 1 - screen_y_flip


def set_size(new_width, new_height):
    set_width(new_width)
    set_height(new_height)


def set_size_adjusted(new_width, new_height):
    set_width_adjusted(new_width)
    set_height_adjusted(new_height)


def get_size():
    return (get_width(), get_height())


def get_size_adjusted():
    return (get_width_adjusted(), get_height_adjusted())


# FPS


def set_fps(fps):
    global _game_speed
    _game_speed = math.floor(fps)


def get_fps():
    global _game_speed
    return _game_speed


def _tick():
    global _game_speed
    _clock.tick(_game_speed)


def reset_clock():
    global _prev_time

    _prev_time = time.time()


def get_delta(fps=None):
    if fps == None:
        fps = _game_speed

    target_speed = 1 / fps
    return _true_game_speed / target_speed


def _update_delta():
    global _true_game_speed
    global _prev_time
    global _cur_time

    # returns current time in ms
    _cur_time = time.time()
    _true_game_speed = _cur_time - _prev_time
    _prev_time = _cur_time


############### DRAWING FUNCTIONS ###############
def draw_line(x1, y1, x2, y2, color):
    pygame.draw.line(_internal_canvas.surface, color, (x1, y1), (x2, y2), 1)
    _update_blend_canvas()


def draw_line_width(x1, y1, x2, y2, color, thickness):
    pygame.draw.line(
        _internal_canvas.surface, color, (x1, y1), (x2, y2), math.floor(thickness)
    )
    _update_blend_canvas()


def draw_rectangle(x, y, w, h, color):
    pygame.draw.rect(_internal_canvas.surface, (color), pygame.Rect(x, y, w, h))
    _update_blend_canvas()


def draw_rectangle_outline(x, y, w, h, color, thickness=1):
    pygame.draw.rect(
        _internal_canvas.surface,
        (color),
        pygame.Rect(x, y, w, h),
        math.floor(thickness),
    )
    _update_blend_canvas()


def draw_circle(x, y, r, color):
    r = abs(r)
    if r <= 1:
        draw_pixel(x, y, color)
    else:
        pygame.draw.circle(_internal_canvas.surface, color, (x, y), r)
        _update_blend_canvas()


def draw_circle_outline(x, y, r, color, thickness=1):
    r = abs(r)
    pygame.draw.circle(
        _internal_canvas.surface, color, (x, y), r, math.floor(thickness)
    )
    _update_blend_canvas()


def draw_pixel(x, y, color):
    # pygame has an overflow error with values that are "too far off the grid" but it seems very arbitrary so using modulo is the cheap fix
    if _alpha == 255:
        _internal_canvas.surface.set_at(
            (
                math.floor(x % (_internal_canvas.get_width() * 2)),
                math.floor(y) % (_internal_canvas.get_height() * 2),
            ),
            color,
        )
    else:
        _internal_canvas.surface.set_at(
            (
                math.floor(x % (_internal_canvas.get_width() * 2)),
                math.floor(y) % (_internal_canvas.get_height() * 2),
            ),
            color,
        )
        _update_blend_canvas()


# draws a mesh given points of the format (float, float) in a triangle strip
def draw_triangle_strip(points, color):
    # points BCDEF => triangles BCD,CED,DEF
    # points FEDCBA => triangles FED,ECD,DCB,CAB
    if len(points) < 3:
        if len(points) > 0:
            draw_line(points[0][0], points[0][1], points[-1][0], points[-1][1], color)
    else:
        for i in range(len(points) - 2):
            p1 = points[i]
            p2 = points[i + 1]
            p3 = points[i + 2]
            draw_line(p1[0], p1[1], p2[0], p2[1], color)
            draw_line(p2[0], p2[1], p3[0], p3[1], color)
            draw_line(p1[0], p1[1], p3[0], p3[1], color)


def set_background_color(color):
    global _background_color
    _background_color = color


def get_background_color():
    return _background_color


def create_hypercube(dimensions):
    return _Hypercube(dimensions)


def draw_hypercube(x, y, hypercube, scale, color, rotations=None):
    try:
        # Rotate it
        if rotations != None:
            for pos, rotation in enumerate(rotations):
                hypercube.planes[pos].rotation = rotation

        # Getting the values of every points in the hypercube
        for vertex in hypercube.points:
            # Scale these values
            for axis in range(hypercube.dimensions):
                vertex.transforms[axis] = vertex.coords[axis] * scale

            # Apply rotations using plane rotation matraxi math
            for plane in hypercube.planes:
                axis_a = plane.axes[0]
                axis_b = plane.axes[1]
                coord_a_prev = vertex.transforms[axis_a]
                coord_b_prev = vertex.transforms[axis_b]

                # tbh this math is really hard... idk how to explain it lol, but it basically rotates the coords in a circle
                # as any points would be, or rather an ellipse to account for scaling :)
                rot = math.radians(plane.rotation)
                vertex.transforms[axis_a] = (
                    math.cos(rot) * coord_a_prev - math.sin(rot) * coord_b_prev
                )
                vertex.transforms[axis_b] = (
                    math.sin(rot) * coord_a_prev + math.cos(rot) * coord_b_prev
                )

            # Translate positions of the vertices
            vertex.transforms[0] += x
            vertex.transforms[1] += y

        for edge in hypercube.edges:
            point_a = edge.endpoints[0]
            point_b = edge.endpoints[1]
            draw_line(
                point_a.transforms[0],
                point_a.transforms[1],
                point_b.transforms[0],
                point_b.transforms[1],
                color,
            )

    except:
        if hypercube.dimensions < 2:
            raise Exception("fewer than 2 dimensions for the hypercube")
        else:
            # if this is raised, use fewer rotations in your list
            raise Exception("plane index out of bounds")


def refresh(color=None):
    if color != None:
        _current_canvas.surface.fill(color)
    else:
        if _current_canvas == _GAME_SCREEN:
            _current_canvas.surface.fill(_background_color)
        else:
            _current_canvas.surface.fill(TRANSPARENT)


def color_oklab(L, a, b):
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b

    l, m, s = (l_**3, m_**3, s_**3)

    r, g, b = (
        4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
        -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
        -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s,
    )

    return tuple(round(max(0, min(1.0, c)) * 255) for c in (r, g, b))


def oklch_to_oklab(L, c, h):
    return [L, c * math.cos(h), c * math.sin(h)]


def color_oklch(L, c, h):
    return color_oklab(*oklch_to_oklab(L, c, h))


def color_hsv(h, s, v):
    # redesigned to work with 255 instead of 1.0, for consistency
    h = h % 256
    s = s % 256
    v = v % 256
    c = v * (s / 255)
    hue_interval = 255 / 6
    x = c * (1 - abs((h / hue_interval) % 2 - 1))
    m = v - c
    c, m, x = int(c), int(m), int(x)

    if h < hue_interval:
        return (c + m, x + m, m)
    elif h < hue_interval * 2:
        return (x + m, c + m, m)
    elif h < hue_interval * 3:
        return (m, c + m, x + m)
    elif h < hue_interval * 4:
        return (m, x + m, c + m)
    elif h < hue_interval * 5:
        return (x + m, m, c + m)
    else:
        return (c + m, m, x + m)


def merge_color(color1, color2, amount):
    amount = 1 if amount == 1 else amount % 1

    return tuple([(color1[x] + (color2[x] - color1[x]) * amount) for x in [0, 1, 2]])


def merge_palette(colors, amount):
    palette_size = len(colors)
    assert palette_size > 1, "Palettes must have two or more colors"

    amount = 1 if amount == 1 else amount % 1
    index = math.floor(min(palette_size - 2, ((palette_size - 1) * amount)))
    ratio = 1 / (len(colors) - 1)
    new_am = (amount - (index * ratio)) / ratio
    return merge_color(colors[index], colors[index + 1], new_am)


############### IMAGES ###############

# draws an image taking an image path


def draw_image(x, y, file, w=0, h=0, color=None, angle=0, alpha=255):
    if not isinstance(file, str):
        raise TypeError(
            f"image must take a file path, not {type(file)}, use draw_sprite or draw_canvas for their respective data types"
        )
    sprite = pygame.image.load(file)

    origin_x, origin_y = 0, 0

    if color != None:
        sprite = colorize(sprite, color).surface

    if w != 0:
        sprite = pygame.transform.scale(sprite, (w, h))

    if alpha != 255:
        sprite.set_alpha(alpha)

    if angle != 0:
        rotated = rotate(sprite, angle)
        origin_x, origin_y = rotated.get_origin_x(), rotated.get_origin_y()
        sprite = rotated.surface

    _internal_canvas.surface.blit(sprite, (x - origin_x, y - origin_y))
    _update_blend_canvas()


# create sprite
def create_sprite(file_name, origin_x=0, origin_y=0):
    return Sprite(file_name, origin_x, origin_y)


# splits a spritesheet into a list of individual images
def create_sprite_sheet(
    canvas,
    width,
    height,
    origin_x=0,
    origin_y=0,
    num_rows=None,
    num_cols=None,
    frames=0,
    x_margin=0,
    y_margin=0,
    x_padding=0,
    y_padding=0,
):
    frame = 0
    sprite_rects = []

    if isinstance(canvas, str):
        sheet = Sprite(canvas)[0]
    elif isinstance(canvas, Sprite):
        if len(canvas.frames) > 1:
            raise Exception("sprite is already a sprite sheet")
        else:
            sheet = canvas.frames[0]
    elif isinstance(canvas, Canvas):
        sheet = canvas
    else:
        raise TypeError(f"cannot create a sprite sheet from type {type(canvas)}")

    if num_rows == None:
        num_rows = sheet.get_height() // height

    if num_cols == None:
        num_cols = sheet.get_width() // width

    for row_num in range(num_rows):
        for col_num in range(num_cols):
            # Position of sprite rect is margin + one sprite size
            # and one padding size for each row. Same for y.
            if frames == 0 or frame < frames:
                x = x_margin + col_num * (width + x_padding)
                y = y_margin + row_num * (height + y_padding)
                sprite_rect = (x, y, width, height)
                sprite_rects.append(sprite_rect)
                frame += 1
            else:
                break

    sheet.surface.convert_alpha()
    new_sprite = Sprite()
    new_sprite.frames = [
        sheet.trim(rect[0], rect[1], rect[2], rect[3]) for rect in sprite_rects
    ]
    new_sprite.width = width
    new_sprite.height = height
    new_sprite.set_origin(origin_x, origin_y)

    return new_sprite


# draws a sprite taking an image
def draw_sprite(x, y, sprite):

    # if _alpha != 255:
    #    new_sprite.set_alpha(_alpha)

    if isinstance(sprite, Sprite):
        draw_canvas(x, y, sprite.get_current_frame())
    elif isinstance(sprite, Canvas):
        draw_canvas(x, y, sprite)
    else:
        raise TypeError(f"Cannot draw a sprite of type {type(sprite)}")

    # _internal_canvas.surface.blit(
    #    new_sprite, (x - sprite.origin_x, y - sprite.origin_y))
    # _update_blend_canvas()


############# TEXT :) #############

# draw text, uses the default font and size unless otherwise specified


def draw_text(x, y, str, color, size=None):
    global _h_text_alignment
    global _v_text_alignment
    pygame.font.init()  # you have to call this at the start

    if size == None:
        size = _default_font[1]
    myfont = pygame.font.Font(_default_font[0], size)
    textcanvas = myfont.render(str, False, color)
    text_rect = textcanvas.get_rect()

    # Adjusting for horizontal alignment
    if _h_text_alignment == _LEFT:
        text_rect.left = x
    elif _h_text_alignment == _CENTER_HORIZONTAL:
        text_rect.centerx = x
    elif _h_text_alignment == _RIGHT:
        text_rect.right = x

    # Adjusting for vertical alignment
    if _v_text_alignment == _TOP:
        text_rect.top = y
    elif _v_text_alignment == _CENTER_VERTICAL:
        text_rect.centery = y
    elif _v_text_alignment == _BOTTOM:
        text_rect.bottom = y

    _internal_canvas.surface.blit(textcanvas, text_rect)
    _update_blend_canvas()


def set_font(font, size=16):
    global _default_font
    _default_font = (font, size)


def reset_font():
    global _default_font
    _default_font = FNT_NORMAL


# Sets the text's horizontal alignment, default left
def align_text_left():
    global _h_text_alignment
    _h_text_alignment = _LEFT


def align_text_right():
    global _h_text_alignment
    _h_text_alignment = _RIGHT


def align_text_top():
    global _v_text_alignment
    _v_text_alignment = _TOP


def align_text_bottom():
    global _v_text_alignment
    _v_text_alignment = _BOTTOM


def center_text_horizontal():
    global _h_text_alignment
    _h_text_alignment = _CENTER_HORIZONTAL


def center_text_vertical():
    global _v_text_alignment
    _v_text_alignment = _CENTER_VERTICAL


def center_text():
    center_text_horizontal()
    center_text_vertical()


def reset_text():
    align_text_left()
    align_text_top()


############# Canvases and blendmodes #############


# intialize a transparent canvas based on width and height
def create_canvas(width, height):
    return Canvas(width, height)


# convert arrays to canvases
def convert_to_canvas(array):
    if isinstance(array, list):
        array = np.array(array)

    if isinstance(array, np.ndarray):
        # typical RGB canvas
        if canvas.shape[-1] == 3:
            pygame.surfarray.make_surface(array)

        # RGBA
        elif canvas.shape[-1] == 4:
            pygame.image.frombuffer(
                np.rot90(array, -1).flatten(), array.shape[:2], "RGBA"
            )

        # 2D Greyscale
        elif len(canvas.shape) == 2:
            black_and_white = np.repeat(canvas[:, :, np.newaxis], 3, 2)
            pygame.surfarray.make_surface(black_and_white)
        # 3D Greyscale
        elif canvas.shape[-1] == 1:
            black_and_white = np.repeat(canvas, 3, 2)
            pygame.surfarray.make_surface(black_and_white)
    else:
        raise TypeError(f"Cannot create canvases from type {type(array)}")


def get_canvas():
    return _current_canvas


def set_canvas(canvas):
    global _current_canvas, _internal_canvas, _canvas_stack
    _current_canvas = canvas

    if _internal_canvas != _BLEND_SCREEN:
        _internal_canvas = canvas
    _canvas_stack = [_internal_canvas]


def reset_canvas():
    global _current_canvas, _internal_canvas, _GAME_SCREEN, _canvas_stack
    _current_canvas = _GAME_SCREEN
    if _internal_canvas != _BLEND_SCREEN:
        _internal_canvas = _GAME_SCREEN
    _canvas_stack = [_internal_canvas]


def push_canvas(canvas):
    global _current_canvas, _internal_canvas
    _canvas_stack.append(canvas)
    _current_canvas = canvas

    if _internal_canvas != _BLEND_SCREEN:
        _internal_canvas = canvas


def pop_canvas():
    global _current_canvas, _internal_canvas
    _canvas_stack.pop()

    _current_canvas = _canvas_stack[-1]

    if _internal_canvas != _BLEND_SCREEN:
        _internal_canvas = _canvas_stack[-1]


def __ndarray_to_canvas(arr):
    # typical RGB canvas
    if arr.shape[-1] == 3:
        return pygame.surfarray.make_surface(arr)

    # RGBA
    elif arr.shape[-1] == 4:
        return pygame.image.frombuffer(
            np.rot90(arr, -1).flatten(), arr.shape[:2], "RGBA"
        )

    # 2D Greyscale
    elif len(arr.shape) == 2:
        return pygame.surfarray.make_surface(np.repeat(arr[:, :, np.newaxis], 3, 2))

    # 3D Greyscale
    elif arr.shape[-1] == 1:
        return pygame.surfarray.make_surface(np.repeat(arr, 3, 2))

    # Invalid input
    else:
        if isinstance(arr, np.ndarray):
            raise ValueError(
                "Cannot handle arrays of shape "
                + str(canvas.shape)
                + ". Array must be grey scale, rgb, or rgba"
            )
        else:
            raise ValueError(f"Input must be a NumPy array. Received: {type(arr)}")


def draw_canvas(x, y, canvas):
    if isinstance(canvas, Sprite):
        canvas = canvas.get_current_frame()
    elif isinstance(canvas, np.ndarray):
        _internal_canvas.surface.blit(__ndarray_to_canvas(canvas), (x, y), area=None)
    else:
        _internal_canvas.surface.blit(
            canvas.surface, (x - canvas.origin_x, y - canvas.origin_y), area=None
        )
    _update_blend_canvas()


def set_blend_mode(mode):
    global _blend_mode
    global _current_canvas
    global _internal_canvas

    if mode != BM_NORMAL or _alpha != 255:
        if _internal_canvas != _BLEND_SCREEN:
            _internal_canvas = _BLEND_SCREEN
    else:
        _update_blend_canvas()
        _internal_canvas = _current_canvas

    _blend_mode = mode


def get_blend_mode():
    return _blend_mode


def reset_blend_mode():
    set_blend_mode(BM_NORMAL)


def colorize(canvas, color):
    origin = (0, 0)

    # allow black and white with just one value
    if isinstance(color, (int, float)):
        color = [color, color, color]

    if isinstance(canvas, Sprite):
        origin = (canvas.get_origin_x(), canvas.get_origin_y())
        current_frame = canvas.get_frame()
        new_sprite = Sprite()
        new_sprite.set_origin(origin[0], origin[1])
        new_sprite.width = canvas.get_width()
        new_sprite.height = canvas.get_height()

        # this feels really cursed, recursion
        for frame in canvas.frames:
            new_sprite.frames.append(colorize(frame, color))
        new_sprite.frame = current_frame
        return new_sprite
    else:
        if isinstance(canvas, Canvas):
            canvas = canvas.get_updated_canvas()
            new_image = canvas.surface.convert_alpha()
            origin = (canvas.get_origin_x(), canvas.get_origin_y())
        elif isinstance(canvas, np.ndarray):
            return colorize(__ndarray_to_canvas(canvas), color)
        elif isinstance(canvas, pygame.Surface):
            new_image = canvas.convert_alpha()
        else:
            raise TypeError(f"Cannot colorize type {type(canvas)}")

        new_image.fill(color, special_flags=pygame.BLEND_RGBA_MULT)

        new_canvas = Canvas(0, 0, 0, 0, new_image.convert_alpha())
        new_canvas.set_origin(origin[0], origin[1])
        return new_canvas


def scale_relative(canvas, rel_width, rel_height=None, smooth=False):
    if rel_height == None:
        rel_height = rel_width

    elif isinstance(canvas, Canvas) or isinstance(canvas, np.ndarray):
        if isinstance(canvas, np.ndarray):
            canvas = Canvas(*canvas.shape, surface=__ndarray_to_canvas(canvas))
        return scale(
            canvas,
            canvas.get_width() * rel_width,
            canvas.get_height() * rel_height,
            smooth,
        )
    else:
        return scale(
            canvas,
            canvas.get_width() * rel_width,
            canvas.get_height() * rel_height,
            smooth,
        )


def scale(canvas, width, height, smooth=False):
    # store a boolean determining if we need to flip it for negative scale values
    flip_x, flip_y = 0, 0
    if abs(width) > 0:
        flip_x = width // abs(width) == -1
    if abs(height) > 0:
        flip_y = height // abs(height) == -1
    width, height = abs(width), abs(height)

    # we need to keep track of the origin to reassign it, scaled correctly
    origin = (0, 0)

    # Sprite scaling, scaling each frame in the sprite
    if isinstance(canvas, Sprite):
        # new sprite that comes out of the scale
        new_sprite = Sprite()

        # rescale origin and assign new width and height
        prev_size = (canvas.get_width(), canvas.get_height())
        origin_scale = (width / prev_size[0], height / prev_size[1])
        origin = (
            canvas.get_origin_x() * origin_scale[0],
            canvas.get_origin_y() * origin_scale[1],
        )
        new_sprite.set_origin(origin[0], origin[1])

        new_sprite.width = width
        new_sprite.height = height

        # keeping track of animation
        current_frame = canvas.get_frame()
        new_sprite.frame = current_frame

        # scale every frame for the sprite
        for frame in canvas.frames:
            # flip frame canvas according to negative width or height
            flipped_frame = pygame.transform.flip(frame.surface, flip_x, flip_y)

            # scale
            if smooth:
                scaled_frame = pygame.transform.smoothscale(
                    flipped_frame, (width, height)
                )
            else:
                scaled_frame = pygame.transform.scale(flipped_frame, (width, height))

            new_frame = Canvas(0, 0, origin[0], origin[1], scaled_frame)

            # add scaled frame to the frames list of the new sprite
            new_sprite.frames.append(new_frame)

        return new_sprite

    # Scaling the canvas
    elif isinstance(canvas, Canvas) or isinstance(canvas, np.ndarray):
        if isinstance(canvas, np.ndarray):
            canvas = Canvas(*canvas.shape, surface=__ndarray_to_canvas(canvas))

        # rescale origin
        prev_size = (canvas.get_width(), canvas.get_height())
        origin_scale = (width / prev_size[0], height / prev_size[0])
        origin = (
            canvas.get_origin_x() * origin_scale[0],
            canvas.get_origin_y() * origin_scale[1],
        )

        # flip according to negative width or height
        flipped_canvas = pygame.transform.flip(canvas.surface, flip_x, flip_y)

        # scaling
        new_image = pygame.transform.scale(flipped_canvas, (width, height))

    # Scaling a pygame surface
    elif isinstance(canvas, pygame.Surface):
        new_image = pygame.transform.scale(canvas.convert_alpha(), (width, height))

    # Error for incorrect input
    else:
        raise TypeError(f"Cannot scale type {type(canvas)}")

    # returning the scaled canvas, if it wasn't a sprite
    new_canvas = Canvas(0, 0, 0, 0, new_image)
    new_canvas.set_origin(origin[0], origin[1])
    return new_canvas


def scale2x(canvas):
    # we need to keep track of the origin to reassign it, scaled correctly
    origin = (canvas.get_origin_x() * 2, canvas.get_origin_y() * 2)

    # Sprite scaling, scaling each frame in the sprite
    if isinstance(canvas, Sprite):
        # new sprite that comes out of the scale
        new_sprite = Sprite()

        # keeping track of animation
        current_frame = canvas.get_frame()
        new_sprite.frame = current_frame

        # scale every frame for the sprite
        for frame in canvas.frames:
            scaled_frame = pygame.transform.scale2x(frame.surface)
            new_frame = Canvas(0, 0, origin[0], origin[1], scaled_frame)

            # add scaled frame to the frames list of the new sprite
            new_sprite.width = frame.get_width() * 2
            new_sprite.height = frame.get_height() * 2
            new_sprite.frames.append(new_frame)

        # rescale origin and assign new width and heighty
        new_sprite.set_origin(origin[0], origin[1])

        return new_sprite

    # Scaling the canvas
    if isinstance(canvas, Canvas):
        new_image = pygame.transform.scale2x(canvas.surface)

    # Scaling a pygame surface
    elif isinstance(canvas, pygame.Surface):
        new_image = pygame.transform.scale2x(canvas.convert_alpha())

    # Error for incorrect input
    else:
        raise TypeError(f"Cannot scale type {type(canvas)}")

    # returning the scaled canvas, if it wasn't a sprite
    new_canvas = Canvas(0, 0, 0, 0, new_image)
    new_canvas.set_origin(origin[0], origin[1])

    return new_canvas


# Rotsprite implementation, rotates canvases and sprites
# Read more about it here: https://en.wikipedia.org/wiki/Pixel-art_scaling_algorithms#RotSprite
def rotate(canvas, angle, iterations=3):
    # Get the surface being worked on depending on data type
    if isinstance(canvas, Sprite):
        updated_canvas = canvas.get_current_frame()
    elif isinstance(canvas, Canvas):
        updated_canvas = canvas
    elif isinstance(canvas, pygame.Surface):
        canvas = Canvas(0, 0, 0, 0, canvas)
        canvas.center_origin()
        updated_canvas = canvas
    else:
        raise TypeError(f"cannot rotate non-canvas object of type {type(canvas)}")

    # limititng calculation times for 90 degrees, since we don't need to do rotsprite then
    if angle % 90 == 0:
        rotated_image = pygame.transform.rotate(updated_canvas.surface, -angle)
        new_canvas = Canvas(0, 0, canvas.origin_x, canvas.origin_y, rotated_image)
    else:
        # scale the image up 8x, this gives us a better resolution to rotate with
        new_scale = 2**iterations
        scaled_canvas = updated_canvas.surface

        if updated_canvas.scaled8x == None:
            for i in range(iterations):
                scaled_canvas = pygame.transform.scale2x(scaled_canvas)
            updated_canvas.scaled8x = scaled_canvas

        rotated_image = pygame.transform.rotate(updated_canvas.scaled8x, -angle)

        # create a new image to draw the rotated and scaled sprite to
        new_image = pygame.Surface(
            (rotated_image.get_width(), rotated_image.get_height()), pygame.SRCALPHA
        )
        new_image.blit(rotated_image, (0, 0))

        # scale the image back down using a nearest neighbor algorithm
        new_width = rotated_image.get_width() / new_scale
        new_height = rotated_image.get_height() / new_scale
        new_canvas = Canvas(
            0,
            0,
            canvas.origin_x,
            canvas.origin_y,
            pygame.transform.scale(new_image, (new_width, new_height)),
        )

    # offset the pivot from center
    image_rect = updated_canvas.surface.get_rect(
        topleft=(-canvas.origin_x, -canvas.origin_y)
    )
    offset = (-image_rect.center[0], -image_rect.center[1])

    # determine rotation from center using a rotation matrix
    # more here: https://en.wikipedia.org/wiki/Rotation_matrix
    rad = math.radians(angle)
    x, y, c, s = offset[0], offset[1], math.cos(rad), math.sin(rad)
    rot_x, rot_y = c * x - s * y, s * x + c * y

    # maintain an origin for drawing correctly
    rot_image_center = (-rot_x, -rot_y)
    new_rect = new_canvas.surface.get_rect(center=rot_image_center)
    new_canvas.set_origin(-new_rect.topleft[0], -new_rect.topleft[1])
    return new_canvas


def rotate_fast(canvas, angle):
    # Get the surface being worked on depending on data type
    if isinstance(canvas, Sprite):
        surface = canvas.get_current_frame().surface
    else:
        surface = canvas.surface

    # limititng calculation times for 90 degrees, since we don't need to do rotsprite then

    # create a new image to draw the rotated and scaled sprite to
    new_canvas = Canvas(
        0, 0, canvas.origin_x, canvas.origin_y, pygame.transform.rotate(surface, -angle)
    )

    # offset the pivot from center
    image_rect = surface.get_rect(topleft=(-canvas.origin_x, -canvas.origin_y))
    offset = (-image_rect.center[0], -image_rect.center[1])

    # determine rotation from center using a rotation matrix
    # more here: https://en.wikipedia.org/wiki/Rotation_matrix
    rad = math.radians(angle)
    x, y, c, s = offset[0], offset[1], math.cos(rad), math.sin(rad)
    rot_x, rot_y = c * x - s * y, s * x + c * y

    # maintain an origin for drawing correctly
    rot_image_center = (-rot_x, -rot_y)
    new_rect = new_canvas.surface.get_rect(center=rot_image_center)
    new_canvas.set_origin(-new_rect.topleft[0], -new_rect.topleft[1])
    return new_canvas


def set_alpha(new_alpha):
    global _alpha, _internal_canvas
    _alpha = new_alpha

    # phaps != prev_alpha?
    if new_alpha == 255:
        reset_alpha()
    else:
        _internal_canvas = _BLEND_SCREEN


def get_alpha():
    return _alpha


def reset_alpha():
    global _alpha, _internal_canvas
    _alpha = 255
    _blit_buffer_canvas()
    _internal_canvas = _current_canvas


############### INTERNALS AND WINDOW DRAWING ###############


def _update_blend_canvas():
    global _blend_mode
    global _BLEND_SCREEN
    global _current_canvas
    global _internal_canvas

    if _blend_mode != BM_NORMAL or _alpha != 255:
        _blit_buffer_canvas()
        _internal_canvas = _BLEND_SCREEN
    else:
        _internal_canvas = _current_canvas


def _blit_buffer_canvas():
    global _BLEND_SCREEN
    _BLEND_SCREEN.surface.set_alpha(_alpha)
    _current_canvas.surface.blit(
        _BLEND_SCREEN.surface, (0, 0), special_flags=_blend_mode
    )
    _BLEND_SCREEN = Canvas(
        0,
        0,
        0,
        0,
        pygame.Surface((get_width_adjusted(), get_height_adjusted()), pygame.SRCALPHA),
    )


# update the window after sizing
def _update_window():
    pygame.init()
    global _NUMLEDS
    global _pixels
    global _orientation
    global _current_canvas
    global _GAME_SCREEN
    global _internal_canvas
    global _BLEND_SCREEN
    global _SCREEN

    _GAME_SCREEN = Canvas(
        0, 0, 0, 0, pygame.Surface((get_width_adjusted(), get_height_adjusted()))
    )
    _BLEND_SCREEN = Canvas(
        0,
        0,
        0,
        0,
        pygame.Surface((get_width_adjusted(), get_height_adjusted()), pygame.SRCALPHA),
    )
    _current_canvas = _GAME_SCREEN

    # internal canvas too?
    os.environ["SDL_VIDEO_CENTERED"] = "1"
    _internal_canvas = _GAME_SCREEN
    _WINDOW_WIDTH = get_width_adjusted() * _WINDOW_SCALE
    _WINDOW_HEIGHT = get_height_adjusted() * _WINDOW_SCALE
    _SCREEN = pygame.display.set_mode((_WINDOW_WIDTH, _WINDOW_HEIGHT))

    _NUMLEDS = get_width() * get_height()
    _pixels = [(0, 0, 0)] * _NUMLEDS


def set_window_scale(scale):
    global _WINDOW_SCALE
    _WINDOW_SCALE = scale
    _update_window()


def get_window_scale():
    return _WINDOW_SCALE


def set_window_pos(x, y):
    win = Window.from_display_module()
    win.position = (x, y)


def get_window_pos():
    return Window.from_display_module().position


# Keyboard and mouse input
def _update_inputs():
    global _key_held, _key_pressed, _key_released, _key_input
    global _mouse_pressed, _mouse_released, _joystick_pressed, _joystick_released, _joystick_dpad
    global _joystick_dpad_pressed, _joystick_dpad_released

    # TODO: add bottom released and pressed for the dpad, via differnce basically

    _key_held = pygame.key.get_pressed()
    _key_pressed = []
    _key_released = []
    _key_input = []
    _mouse_pressed = []
    _mouse_released = []
    _joystick_pressed = []
    _joystick_released = []
    _joystick_dpad_pressed = []
    _joystick_dpad_released = []

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # clear the grid to black upon exit
            refresh(BLACK)
            draw()
            quit()

        if event.type == pygame.KEYDOWN:
            _key_pressed.append(event.key)
            # print(event.unicode)

        if event.type == pygame.KEYUP:
            _key_released.append(event.key)

        if event.type == pygame.MOUSEBUTTONDOWN:
            _mouse_pressed.append(event.button)

        if event.type == pygame.MOUSEBUTTONUP:
            _mouse_released.append(event.button)

        if event.type == pygame.JOYBUTTONDOWN:
            _joystick_pressed.append(event.button)

        if event.type == pygame.JOYBUTTONUP:
            _joystick_released.append(event.button)

        # Handle hotplugging
        if event.type == pygame.JOYDEVICEADDED:
            joy = pygame.joystick.Joystick(event.device_index)
            _joysticks[joy.get_instance_id()] = joy
            print(f"Joystick {joy.get_instance_id()} connencted")

        if event.type == pygame.JOYDEVICEREMOVED:
            del _joysticks[event.instance_id]
            print(f"Joystick {event.instance_id} disconnected")

    if len(_joysticks) > _joystick_environment:
        if _joysticks[_joystick_environment].get_numhats() > 0:
            prev_pad = _joystick_dpad
            _joystick_dpad = _joysticks[_joystick_environment].get_hat(0)

            if prev_pad != None:
                # Horizontal dpad check
                if prev_pad[0] != _joystick_dpad[0]:
                    # Get dpad pressed
                    if _joystick_dpad[0] == 1:
                        _joystick_dpad_pressed.append(JS_PADR)

                    if _joystick_dpad[0] == -1:
                        _joystick_dpad_pressed.append(JS_PADL)

                    # Get dpad released
                    if prev_pad[0] == 1:
                        _joystick_dpad_released.append(JS_PADR)

                    if prev_pad[0] == -1:
                        _joystick_dpad_released.append(JS_PADL)

                # Vertical dpad check
                if prev_pad[1] != _joystick_dpad[1]:
                    if _joystick_dpad[1] == 1:
                        _joystick_dpad_pressed.append(JS_PADU)

                    if _joystick_dpad[1] == -1:
                        _joystick_dpad_pressed.append(JS_PADD)

                    if prev_pad[1] == 1:
                        _joystick_dpad_released.append(JS_PADU)

                    if prev_pad[1] == -1:
                        _joystick_dpad_released.append(JS_PADD)

    pygame.event.pump()


# keyboard inputs
def _sub_key(key):
    special_to_reg = dict(zip('~!@#$%^&*()_+\{\}|:"<>?', "`1234567890-=[]\\;',./"))
    key = key.lower()

    if key == "page up":
        return ["pageup"]
    if key == "page down":
        return ["pagedown"]
    if key == "lctrl":
        return ["left ctrl"]
    if key == "rctrl":
        return ["right ctrl"]
    if key == "esc":
        return ["escape"]
        return ["`"]
    elif key in special_to_reg:
        return [special_to_reg[key]]
    elif key == "\t":
        return "tab"
    elif key == "enter" or key == "\n":
        return ["return"]
    elif key == "caps" or key == "caps lock":
        return "CapsLock"
    elif key == "alt":
        return ["left alt", "right alt"]
    elif key == "control" or key == "ctrl":
        return ["left ctrl", "right ctrl"]
    elif key == "shift":
        return ["left shift", "right shift"]
    else:
        return [key]


def get_key_pressed(key: str):
    return any([(pygame.key.key_code(sub) in _key_pressed) for sub in _sub_key(key)])


def get_key_released(key: str):
    return any([(pygame.key.key_code(sub) in _key_released) for sub in _sub_key(key)])


def get_key(key: str):
    return any([_key_held[(pygame.key.key_code(sub))] for sub in _sub_key(key)])


# mouse inputs
def get_mouse_left():
    return pygame.mouse.get_pressed()[0]


def get_mouse_middle():
    return pygame.mouse.get_pressed()[1]


def get_mouse_right():
    return pygame.mouse.get_pressed()[2]


# mouse pressed
def get_mouse_pressed_left():
    return _mouse_pressed.count(1) >= 1


def get_mouse_pressed_middle():
    return _mouse_pressed.count(2) >= 1


def get_mouse_pressed_right():
    return _mouse_pressed.count(3) >= 1


# mouse released
def get_mouse_released_left():
    return _mouse_released.count(1) >= 1


def get_mouse_released_middle():
    return _mouse_released.count(2) >= 1


def get_mouse_released_right():
    return _mouse_released.count(3) >= 1


def get_mouse_scroll_up():
    return _mouse_pressed.count(4) >= 1


def get_mouse_scroll_down():
    return _mouse_pressed.count(5) >= 1


def get_mouse_x():
    global _mouse_x, _mouse_y
    _mouse_x, _mouse_y = pygame.mouse.get_pos()
    _mouse_x /= _WINDOW_SCALE
    return _mouse_x


def get_mouse_y():
    global _mouse_x, _mouse_y
    _mouse_x, _mouse_y = pygame.mouse.get_pos()
    _mouse_y /= _WINDOW_SCALE
    return _mouse_y


def set_mouse_x(x):
    pygame.mouse.set_pos(x * _WINDOW_SCALE, get_mouse_y() * _WINDOW_SCALE)


def set_mouse_y(y):
    pygame.mouse.set_pos(get_mouse_x() * _WINDOW_SCALE, y * _WINDOW_SCALE)


def set_mouse_pos(x, y):
    pygame.mouse.set_pos(x * _WINDOW_SCALE, y * _WINDOW_SCALE)


def hide_cursor():
    pygame.mouse.set_visible(False)


def display_cursor():
    pygame.mouse.set_visible(True)


def set_rumble(left_motor, right_motor):
    if len(_joysticks) > _joystick_environment:
        _joysticks[_joystick_environment].rumble(
            left_motor * 0xFFFF, right_motor * 0xFFFF, 0
        )


def set_controller(controller):
    global _joystick_environment
    _joystick_environment = controller


def get_controller():
    return _joystick_environment


def get_controller_count():
    return len(_joysticks)


# joy stick inputs
def get_button(button):
    if button > 16:
        print(f"Button {button} does not exist")
        return False
    elif button >= JS_PADU:
        if _joystick_dpad != None:
            if button == JS_PADU:
                return _joystick_dpad[1] == 1
            elif button == JS_PADD:
                return _joystick_dpad[1] == -1
            elif button == JS_PADL:
                return _joystick_dpad[0] == -1
            elif button == JS_PADR:
                return _joystick_dpad[0] == 1
        else:
            print("Dpad not detected")
            return False
    elif len(_joysticks) > _joystick_environment:
        return _joysticks[_joystick_environment].get_button(button)
    else:
        # print(f"Joystick not connected, button {button} cannot be checked")
        return False


def get_button_pressed(button):
    if button >= JS_PADU:
        return _joystick_dpad_pressed.count(button) > 0
    else:
        return _joystick_pressed.count(button) > 0


def get_button_released(button):
    if button >= JS_PADU:
        return _joystick_dpad_released.count(button) > 0
    else:
        return _joystick_released.count(button) > 0


# joysticks
def set_deadzone(deadzone: float):
    global _deadzone
    _deadzone = deadzone


def get_haxis(joystick):
    axis_val = 0
    if len(_joysticks) > _joystick_environment:
        if joystick == JS_LSTICK:
            axis_val = _joysticks[_joystick_environment].get_axis(0)
        elif joystick == JS_RSTICK:
            axis_val = _joysticks[_joystick_environment].get_axis(3)
        else:
            print("joystick does not exist, can't receive axis")

        # capping to deadzone limit
        if abs(axis_val) < _deadzone:
            axis_val = 0

        return axis_val
    else:
        return 0


def get_vaxis(joystick):
    axis_val = 0

    if len(_joysticks) > _joystick_environment:
        if joystick == JS_LSTICK:
            axis_val = _joysticks[_joystick_environment].get_axis(1)
        elif joystick == JS_RSTICK:
            axis_val = _joysticks[_joystick_environment].get_axis(4)
        else:
            print("joystick does not exist, can't receive axis")

            # capping to deadzone limit
        if abs(axis_val) < _deadzone:
            axis_val = 0
        return axis_val
    else:
        return 0


# drawing the LED grid and window
def _update_environment():
    _update_sprites()
    _update_inputs()
    _update_delta()


def draw():
    global _clock
    _tick()
    pygame.display.set_caption(f"LED Simulator - FPS: {_clock.get_fps():.2f}")
    # animate animated sprites
    _update_environment()

    # This draws and sends differently depending on the _orientation of the screen
    # Drawing Simulation Screen
    _SCREEN.blit(
        pygame.transform.scale(
            _GAME_SCREEN.surface,
            (
                get_width_adjusted() * _WINDOW_SCALE,
                get_height_adjusted() * _WINDOW_SCALE,
            ),
        ),
        (0, 0),
    )
    pygame.display.flip()

    # If _networked then send _pixels to the grid with our desired _orientation
    if _networked:
        _pixels = (
            pygame.surfarray.pixels3d(_GAME_SCREEN.surface) * _brightness
        ).astype(np.uint8)
        _pixels = np.rot90(_pixels, _orientation - 1)

        # sending the pixels to the client to put on the grid
        _CLIENT.send_pixels(0, _pixels.flatten())


# Updates everything on the first frame!
# So you can check keys and all that jazz before you actually call the draw function
_update_environment()
