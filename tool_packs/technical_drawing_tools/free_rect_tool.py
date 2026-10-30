from tool_manager import DrawingTool, FinalizedShapes, ToolStatusMessageType, get_tool_icon_src, CanvasCoords
from canvas_shapes import VectorLine, VectorRect, VectorShape
from utils import get_number_sign

class Tool(DrawingTool):
    name = "Free Rect"
    icon_src = get_tool_icon_src(__file__)
    preview_shape : VectorRect
    uniform : bool = False
    uniform_tooltip = "Square"
    _last_hover_canvas_coords : CanvasCoords
    def click(self, canvas_coords : CanvasCoords) -> None | tuple[VectorShape, ...]:
        if self.previewing:
            self.previewing = False
            return None
        self.previewing = True
        rect = VectorRect(
            origin_x=canvas_coords.pos.x,
            origin_y=canvas_coords.pos.y,
            width=0,
            height=0
        )
        self.preview_shape = rect
        self._last_hover_canvas_coords = canvas_coords
        return (rect,)
    def finalize(self) -> FinalizedShapes:
        if self.preview_shape.width == 0 or self.preview_shape.height == 0:
            return FinalizedShapes(message="width or height equal to 0", message_type=ToolStatusMessageType.ERROR)
        return FinalizedShapes([
            VectorLine(origin_x=self.preview_shape.origin_x, origin_y=self.preview_shape.origin_y,
                       length_x=self.preview_shape.width, length_y=0),
            VectorLine(origin_x=self.preview_shape.origin_x, origin_y=self.preview_shape.origin_y,
                       length_x=0, length_y=self.preview_shape.height),
            VectorLine(origin_x=self.preview_shape.origin_x+self.preview_shape.width, origin_y=self.preview_shape.origin_y,
                       length_x=0, length_y=self.preview_shape.height),
            VectorLine(origin_x=self.preview_shape.origin_x, origin_y=self.preview_shape.origin_y+self.preview_shape.height,
                       length_x=self.preview_shape.width, length_y=0)
        ])
    def move(self, canvas_coords : CanvasCoords) -> tuple[VectorShape, ...] | None:
        if self.previewing:
            self.preview_shape.width = canvas_coords.pos.x - self.preview_shape.origin_x
            self.preview_shape.height = canvas_coords.pos.y - self.preview_shape.origin_y
            self._last_hover_canvas_coords = canvas_coords
            if self.uniform:
                small_side = min(abs(self.preview_shape.width), abs(self.preview_shape.height))
                self.preview_shape.width = small_side * get_number_sign(self.preview_shape.width)
                self.preview_shape.height = small_side * get_number_sign(self.preview_shape.height)
            return (self.preview_shape,)
        return None
    def set_uniform(self, uniform: bool) -> tuple[VectorShape, ...] | None:
        self.uniform = uniform
        if self.previewing:
            return self.move(self._last_hover_canvas_coords)
        return None