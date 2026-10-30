from tool_manager import DrawingTool, FinalizedShapes, ToolStatusMessageType, get_tool_icon_src, CanvasCoords
from canvas_shapes import VectorLine, VectorRect, VectorShape, VectorMarker
from utils import get_number_sign

class Tool(DrawingTool):
    name = "Midpoint Rect"
    icon_src = get_tool_icon_src(__file__)
    preview_shape : VectorRect
    midpoint : VectorMarker
    width : float | None = None
    uniform : bool = False
    _last_hover_canvas_coords : CanvasCoords
    def click(self, canvas_coords : CanvasCoords) -> None | tuple[VectorShape, ...]:
        if not self.previewing:
            self.previewing = True
            self.preview_shape  = VectorRect(
                origin_x=canvas_coords.pos.x,
                origin_y=canvas_coords.pos.y,
                width=0,
                height=0
            )
            self.midpoint = VectorMarker(
                canvas_coords.pos.x, canvas_coords.pos.y
            )
            self._last_hover_canvas_coords = canvas_coords
            return (self.preview_shape, self.midpoint)
        elif self.width is None:
            self.uniform_tooltip = "Square"
            self.width = self.preview_shape.width
            return None
        self.previewing = False
        return None
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
            if self.width is None:
                self.preview_shape.width = (canvas_coords.pos.x - self.midpoint.origin_x)*2
            else:
                if self.uniform:
                    self.preview_shape.height = self.width
                else:
                    self.preview_shape.height = (canvas_coords.pos.y - self.midpoint.origin_y)*2
            self.preview_shape.origin_x = self.midpoint.origin_x - self.preview_shape.width/2
            self.preview_shape.origin_y = self.midpoint.origin_y - self.preview_shape.height/2
            self._last_hover_canvas_coords = canvas_coords
            return (self.preview_shape,)
        return None
    def set_uniform(self, uniform: bool) -> tuple[VectorShape, ...] | None:
        self.uniform = uniform
        if self.previewing:
            return self.move(self._last_hover_canvas_coords)
        return None