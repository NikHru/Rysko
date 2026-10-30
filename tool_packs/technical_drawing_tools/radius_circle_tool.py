from tool_manager import DrawingTool, FinalizedShapes, ToolStatusMessageType, get_tool_icon_src, CanvasCoords
from canvas_shapes import VectorCircle, VectorMarker, VectorShape
from utils import get_tri_hypotenuse

class Tool(DrawingTool):
    name = "Radius Circle"
    icon_src = get_tool_icon_src(__file__)
    preview_shape : VectorCircle
    def click(self, canvas_coords : CanvasCoords) -> None | tuple[VectorShape, ...]:
        if self.previewing:
            self.previewing = False
            return None
        self.previewing = True
        circle = VectorCircle(
            origin_x=canvas_coords.pos.x,
            origin_y=canvas_coords.pos.y,
            radius=0
        )
        center_marker = VectorMarker(circle.origin_x, circle.origin_y, 8)
        self.preview_shape = circle
        return (center_marker, circle)
    def finalize(self):
        if self.preview_shape.radius == 0:
            return FinalizedShapes(message="radius equal to 0", message_type=ToolStatusMessageType.ERROR)
        return FinalizedShapes([self.preview_shape])
    def move(self, canvas_coords : CanvasCoords) -> tuple[VectorShape, ...] | None:
        if self.previewing:
            x_diff = abs(canvas_coords.pos.x - self.preview_shape.origin_x)
            y_diff = abs(canvas_coords.pos.y - self.preview_shape.origin_y)
            self.preview_shape.radius = get_tri_hypotenuse(x_diff, y_diff)
            return (self.preview_shape,)
        return None
