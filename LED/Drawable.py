from abc import ABC, abstractmethod
from RenderContext import _RenderContext


class _Drawable(ABC):
    def __init__(
        self, context: _RenderContext, origin_x: float = 0, origin_y: float = 0
    ):
        self.origin_x = origin_x
        self.origin_y = origin_y
        self.width = 0
        self.height = 0

    @abstractmethod
    def set_origin_x(self, x: float) -> None:
        pass

    @abstractmethod
    def set_origin_y(self, y: float) -> None:
        pass

    def set_origin(self, x: float, y: float) -> None:
        self.set_origin_x(x)
        self.set_origin_y(y)

    def get_origin_x(self) -> float:
        return self.origin_x

    def get_origin_y(self) -> float:
        return self.origin_y

    def get_width(self) -> int:
        return self.width

    def get_height(self) -> int:
        return self.height

    def draw(self):
        pass
