import sdl2
import sdl2.ext
from OPCClient import _OPCClient
from Canvas import Canvas
import numpy as np
import os


class _LEDEngine:
    def __init__(self):
        self._CLIENT = _OPCClient()
        self._networked = False

        # GRID HARDWARE SETTINGS
        self._width = 60
        self._height = 80
        self._screen_x_flip = False
        self._screen_y_flip = False
        self._WINDOW_SCALE = 11

        # 1 horizontal, 0 vertical with the current grid set up
        self._orientation = 0
        self._brightness = 1

        # Game state variables
        self._game_speed = 120
        self._elapsed_frames = 0
        self._previous_ticks = sdl2.SDL_GetTicks()

        # Internal Drawing Variables
        self._GAME_SCREEN = Canvas(self._width, self._height)

        self._internal_canvas = self._GAME_SCREEN
        self._canvas_stack = [self._internal_canvas]
        self._alpha = 255
        self._background_color = (0, 0, 0)

        # SDL Components
        self._window = sdl2.SDL_CreateWindow(
            b"LED Simulator",
            sdl2.SDL_WINDOWPOS_CENTERED,
            sdl2.SDL_WINDOWPOS_CENTERED,
            self._width * self._WINDOW_SCALE,
            self._height * self._WINDOW_SCALE,
            sdl2.SDL_WINDOW_RESIZABLE,
        )

        self._renderer = sdl2.SDL_CreateRenderer(
            self._window, -1, sdl2.SDL_RENDERER_ACCELERATED
        )

        self._scaled_surface = sdl2.SDL_CreateRGBSurface(
            0,
            self.get_width_adjusted() * self._WINDOW_SCALE,
            self.get_height_adjusted() * self._WINDOW_SCALE,
            32,
            0,
            0,
            0,
            0,
        )

        self._texture = sdl2.SDL_CreateTextureFromSurface(
            self._renderer, self._scaled_surface
        )

        # Set the window icon
        icon_path = (os.path.dirname(os.path.abspath(__file__)) + "/icon.png").encode(
            "utf-8"
        )
        icon_surface = sdl2.ext.image.load_img(icon_path)

        if icon_surface:
            sdl2.SDL_SetWindowIcon(self._window, icon_surface)
            sdl2.SDL_FreeSurface(icon_surface)
        else:
            print("Failed to load icon:", sdl2.SDL_GetError())

    def get_width(self) -> int:
        return self._width

    def get_height(self) -> int:
        return self._height

    def get_width_adjusted(self) -> int:
        if self._orientation % 2 == 0:
            return self._width
        else:
            return self._height

    def get_height_adjusted(self) -> int:
        if self._orientation % 2 == 0:
            return self._height
        else:
            return self._width

    def _clean(self):
        print("Flushed black. Cleaning up resources...")
        sdl2.SDL_DestroyRenderer(self._renderer)
        sdl2.SDL_DestroyWindow(self._window)
        sdl2.SDL_Quit()
        exit(0)

    def _update_environment(self):
        event = sdl2.SDL_Event()

        for event in sdl2.ext.get_events():
            if event.type == sdl2.SDL_QUIT:
                self._clean()

    def _tick(self):
        elapsed_time = sdl2.SDL_GetTicks() - self._previous_ticks
        target_time = 1000 // self._game_speed
        wait_time = target_time - elapsed_time

        # print(wait_time)
        if wait_time > 0:
            sdl2.SDL_Delay(wait_time)

        self._previous_ticks = sdl2.SDL_GetTicks()

    def _update_window_title(self):
        sdl2.SDL_SetWindowTitle(
            self._window,
            f"LED Simulator - FPS: {1000/(sdl2.SDL_GetTicks()-self._previous_ticks):.2f}".encode(
                "utf-8"
            ),
        )

        self._elapsed_frames += 1

    def draw(self):
        self._update_window_title()
        self._tick()

        # Animate animated sprites
        self._update_environment()

        # Draw the simulation screen
        sdl2.SDL_BlitScaled(self._GAME_SCREEN.surface, None, self._scaled_surface, None)

        # Lock the scaled surface to get the pixel data
        sdl2.SDL_LockSurface(self._scaled_surface)
        pixels = self._scaled_surface.contents.pixels
        pitch = self._scaled_surface.contents.pitch

        # update screen
        sdl2.SDL_UpdateTexture(self._texture, None, pixels, pitch)
        sdl2.SDL_UnlockSurface(self._scaled_surface)
        sdl2.SDL_RenderCopy(self._renderer, self._texture, None, None)
        sdl2.SDL_RenderPresent(self._renderer)

        # If self._networked then send self._pixels to the grid with our desired self._orientation
        if self._networked:
            self._pixels = (
                sdl2.surfarray.pixels3d(self._GAME_SCREEN.surface) * self._brightness
            ).astype(np.uint8)

            self._pixels = np.rot90(self._pixels, self._orientation - 1)

            # Sending the pixels to the client to put on the grid
            self._CLIENT.send_pixels(0, self._pixels.flatten())
