import numpy as np
import math
import sdl2
import sdl2.ext
from Drawable import _Drawable
from PIL import Image
from RenderContext import _RenderContext
from constants import *
from OpenGL import GL


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

        # Make read and write PBO?

    def center_origin(self) -> None:
        self.origin_x = self.width / 2
        self.origin_y = self.height / 2

    def set_origin_x(self, x):
        self.origin_x = x

    def set_origin_y(self, y):
        self.origin_y = y

    def _create_fbo(self, width, height):
        fbo = GL.glGenFramebuffers(1)
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, fbo)

        texture = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, texture)
        GL.glTexImage2D(
            GL.GL_TEXTURE_2D,
            0,
            GL.GL_RGBA,
            width,
            height,
            0,
            GL.GL_RGBA,
            GL.GL_UNSIGNED_BYTE,
            None,
        )
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glFramebufferTexture2D(
            GL.GL_FRAMEBUFFER, GL.GL_COLOR_ATTACHMENT0, GL.GL_TEXTURE_2D, texture, 0
        )

        if GL.glCheckFramebufferStatus(GL.GL_FRAMEBUFFER) != GL.GL_FRAMEBUFFER_COMPLETE:
            raise RuntimeError("Framebuffer is not complete")

        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)
        return fbo, texture

    def _create_pbo(self):
        pbo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_PIXEL_PACK_BUFFER, pbo)
        GL.glBufferData(
            GL.GL_PIXEL_PACK_BUFFER,
            self.width * self.height * 4,
            None,
            GL.GL_STREAM_READ,
        )
        GL.glBindBuffer(GL.GL_PIXEL_PACK_BUFFER, 0)

        return pbo

    def _bind(self):
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self.fbo)
        GL.glViewport(0, 0, self.width, self.height)

    def _unbind(self):
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)

    def _get_texture(self):
        return self.texture

    def _read_pixels(self):
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self.fbo)
        GL.glBindBuffer(GL.GL_PIXEL_PACK_BUFFER, self.pbo)
        GL.glReadPixels(
            0, 0, self.width, self.height, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, None
        )

        data = GL.glMapBuffer(GL.GL_PIXEL_PACK_BUFFER, GL.GL_READ_ONLY)
        pixel_data = sdl2.SDL_CreateRGBSurfaceFrom(
            data, self.width, self.height, 32, self.width * 4, 0, 0, 0, 0
        )

        GL.glUnmapBuffer(GL.GL_PIXEL_PACK_BUFFER)
        GL.glBindBuffer(GL.GL_PIXEL_PACK_BUFFER, 0)

        return pixel_data

    def _cleanup(self):
        GL.glDeleteFramebuffers(1, [self.fbo])
        GL.glDeleteTextures(1, [self.texture])
        GL.glDeleteBuffers(1, [self.pbo])
