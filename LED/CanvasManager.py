import sdl2
import sdl2.ext
from Canvas import _Canvas
from typing import List, Optional
from RenderContext import _RenderContext


class _CanvasManager:
    def __init__(self, context: _RenderContext) -> None:
        self._context = context
        self._canvas_stack: List[_Canvas] = []
        self._current_canvas: _Canvas = _Canvas(self._context, 0, 0)  # put here xd

    def set_canvas(self, canvas: _Canvas) -> None:
        """Set the current render target to the specified canvas."""
        self._current_canvas = canvas
        sdl2.SDL_SetRenderTarget(self._context._renderer, canvas.texture)

    def get_canvas(self) -> Optional[_Canvas]:
        """Get the current render target."""
        return self._current_canvas

    def reset_canvas(self) -> None:
        """Reset the render target to the default (the window)."""
        self._current_canvas = self._context._GAME_SCREEN
        sdl2.SDL_SetRenderTarget(self._context._renderer, self._current_canvas.texture)

    def push_canvas(self, canvas: _Canvas) -> None:
        """Push the current canvas to the stack and set the new canvas as the render target."""
        if self._current_canvas != self._context._GAME_SCREEN:
            self._canvas_stack.append(self._current_canvas)

        self.set_canvas(canvas)

    def pop_canvas(self) -> Optional[_Canvas]:
        """
        Pop the last canvas from the stack and set it as the render target.
        Resets if stack is empty. Return canvas if successful, otherwise None.
        """
        if self._canvas_stack:
            prev_canvas = self._canvas_stack.pop()
            self.set_canvas(prev_canvas)
            return prev_canvas

        self.reset_canvas()
        return None
