import numpy as np
import math
import sdl2
import sdl2.ext
from Drawable import Drawable
from PIL import Image
from constants import *


class Canvas(Drawable):
    def __init__(
        self,
        width: int,
        height: int,
        origin_x: float = 0,
        origin_y: float = 0,
        surface=None,
    ):
        super().__init__(origin_x, origin_y)
        self.angle = 0
        self.cnv_scale = 1
        self.scaled8x = None

        self.surface = surface or sdl2.SDL_CreateRGBSurface(
            sdl2.SDL_SWSURFACE,
            width,
            height,
            32,
            0xFF000000,
            0x00FF0000,
            0x0000FF00,
            0x000000FF,
        )

        self.

        self.width = self.surface.contents.w
        self.height = self.surface.contents.h

    def export(self, file_name: str) -> None:
        image = Image.fromarray(np.uint8(self.get_ndarray()))
        image.save(file_name)

    def refresh(self, color=TRANSPARENT) -> None:
        sdl2.SDL_FillRect(
            self.surface, None, sdl2.SDL_MapRGBA(self.surface.contents.format, *color)
        )

    def center_origin(self) -> None:
        self.origin_x = self.width / 2
        self.origin_y = self.height / 2

    def __setitem__(self, coords, col) -> None:
        x_key, y_key = math.floor(coords[0]), math.floor(coords[1])
        sdl2.SDL_SetRenderDrawColor(self.surface, *col)
        sdl2.SDL_RenderDrawPoint(self.surface, x_key % self.width, y_key % self.height)

    def __getitem__(self, coords):
        x_key, y_key = math.floor(coords[0]), math.floor(coords[1])
        pixel = sdl2.ext.PixelView(self.surface)
        col = pixel[x_key % self.width, y_key % self.height]
        return (col.r, col.g, col.b, col.a)

    # def compare(self, other: 'Drawable') -> bool:
    #    return (self.get_ndarray() == other.get_ndarray()).all()

    def set_origin_x(self, x):
        self.origin_x = x

    def set_origin_y(self, y):
        self.origin_y = y

    def get_ndarray(self) -> np.ndarray:
        return sdl2.ext.pixels2array(self.surface)

    def get_rgb(self):
        return sdl2.ext.pixels2array(self.surface)

    def get_rgba(self):
        return np.dstack((self.get_rgb(), self.get_alpha()))

    def get_red(self):
        return np.dsplit(self.get_rgb(), 3)[0]

    def get_green(self):
        return np.dsplit(self.get_rgb(), 3)[1]

    def get_blue(self):
        return np.dsplit(self.get_rgb(), 3)[2]

    def get_alpha(self):
        return sdl2.ext.pixels2array(self.surface, format="A")

    def rotate(self, angle):
        self.angle = angle

    def get_angle(self):
        return self.angle

    def scale(self):
        pass

    def get_scale(self):
        return self.cnv_scale

    def trim(self, x, y, w, h):
        rect = sdl2.SDL_Rect(x, y, w, h)
        image = sdl2.SDL_CreateRGBSurface(
            sdl2.SDL_SWSURFACE, w, h, 32, 0xFF000000, 0x00FF0000, 0x0000FF00, 0x000000FF
        )
        sdl2.SDL_BlitSurface(self.surface, rect, image, None)

        return Canvas(0, 0, 0, 0, image)
