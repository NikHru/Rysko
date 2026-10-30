from tool_manager import DrawingTool, FinalizedShapes, ToolStatusMessageType, get_tool_icon_src, CanvasCoords
from canvas_shapes import VectorLine, VectorShape
from flet import Offset

class Tool(DrawingTool):
    name = "Free Line"
    icon_src = get_tool_icon_src(__file__)
    preview_shape : VectorLine
    uniform_tooltip = "Continue Line"
    def click(self, canvas_coords : CanvasCoords) -> None | tuple[VectorShape, ...]:
        if self.previewing:
            self.previewing = False
            if self.repeat and self.preview_shape is not None:
                self.repeat_start_coords = CanvasCoords(Offset(
                    self.preview_shape.origin_x+self.preview_shape.length_x,
                    self.preview_shape.origin_y+self.preview_shape.length_y
                ))
            return None
        self.previewing = True
        line = VectorLine(
            origin_x=canvas_coords.pos.x,
            origin_y=canvas_coords.pos.y,
            length_x=0,
            length_y=0
        )
        self.preview_shape = line
        return (line,)
    def finalize(self) -> FinalizedShapes:
        if self.preview_shape.length_x == 0 and self.preview_shape.length_y == 0:
            return FinalizedShapes(message="length is equal to zero", message_type=ToolStatusMessageType.ERROR)
        return FinalizedShapes([self.preview_shape])
    def move(self, canvas_coords : CanvasCoords) -> tuple[VectorShape, ...] | None:
        if self.previewing:
            self.preview_shape.length_x = canvas_coords.pos.x - self.preview_shape.origin_x
            self.preview_shape.length_y = canvas_coords.pos.y - self.preview_shape.origin_y
            return (self.preview_shape,)
        return None
    def set_uniform(self, uniform : bool) -> tuple[VectorShape, ...] | None:
        self.repeat = uniform
        return None