from CanvasManager import _CanvasManager
import sdl2, sdl2.ext
from OpenGL import GL


class _RenderContext:
    def __init__(self):
        self.width = 0
        self.height = 0
        self.blend_mode = 0
        self.alpha = 0
        self.current_canvas = None
        self._WINDOW_SCALE = 11
        self._game_speed = 120
        self._background_color = (0, 0, 0)

        # Initialize SDL with OpenGL context
        sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)
        sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_CONTEXT_MAJOR_VERSION, 3)
        sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_CONTEXT_MINOR_VERSION, 3)
        sdl2.SDL_GL_SetAttribute(
            sdl2.SDL_GL_CONTEXT_PROFILE_MASK, sdl2.SDL_GL_CONTEXT_PROFILE_CORE
        )

        self._window = sdl2.SDL_CreateWindow(
            b"LED Simulator",
            sdl2.SDL_WINDOWPOS_CENTERED,
            sdl2.SDL_WINDOWPOS_CENTERED,
            self._width * self._WINDOW_SCALE,
            self._height * self._WINDOW_SCALE,
            sdl2.SDL_WINDOW_OPENGL | sdl2.SDL_WINDOW_RESIZABLE,
        )

        # Render with explicit OpenGL backend
        self._gl_context = sdl2.SDL_GL_CreateContext(self.window)
        self._renderer = sdl2.SDL_CreateRenderer(
            self.window,
            -1,
            sdl2.SDL_RENDERER_ACCELERATED | sdl2.SDL_RENDERER_PRESENTVSYNC,
        )

    def _clean(self):
        print("Flushed black. Cleaning up resources...")
        sdl2.SDL_GL_DeleteContext(self._gl_context)
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
