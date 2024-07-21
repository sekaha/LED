import numpy as np
import math
import sdl2
import sdl2.ext
from Drawable import _Drawable
from PIL import Image
from RenderContext import _RenderContext
from constants import *


# Stuff to do (in order):
# Make it so canvases work as a render target
# Lock them when used as an array by the user, seamlessly ofc
# Then add ndarray conversion
# Export as image
class _Canvas(_Drawable):
    def __init__(
        self,
        context: _RenderContext,
        width: int,
        height: int,
        origin_x: float = 0,
        origin_y: float = 0,
    ):
        super().__init__(context, origin_x, origin_y)
        self.angle = 0
        self.cnv_scale = 1
        self.scaled8x = None

        # SDL_TEXTUREACCESS_STREAMING allows both being used as a render target and being locked
        self.texture = sdl2.SDL_CreateTexture(
            context._renderer,
            sdl2.SDL_PIXELFORMAT_RGBA8888,
            sdl2.SDL_TEXTUREACCESS_STREAMING,
            width,
            height,
        )
        # texture = sdl2.SDL_CreateTextureFromSurface(renderer, image_surface)

        self.width = width
        self.height = height

    def center_origin(self) -> None:
        self.origin_x = self.width / 2
        self.origin_y = self.height / 2

    def set_origin_x(self, x):
        self.origin_x = x

    def set_origin_y(self, y):
        self.origin_y = y
