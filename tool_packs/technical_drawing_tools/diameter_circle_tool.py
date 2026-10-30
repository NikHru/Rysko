from tool_manager import DrawingTool, FinalizedShapes, ToolStatusMessageType, get_tool_icon_src, CanvasCoords
from canvas_shapes import VectorCircle, VectorMarker, VectorShape
from utils import get_tri_hypotenuse

class Tool(DrawingTool):
    name = "Diameter Circle"
    icon_src: str = get_tool_icon_src(__file__)
    preview_shape : VectorCircle
    center_marker : VectorMarker
    origin_x : float = 0
    origin_y : float = 0
    def click(self, canvas_coords : CanvasCoords) -> None | tuple[VectorShape, ...]:
        if self.previewing:
            self.previewing = False
            return None
        self.previewing = True
        self.origin_x = canvas_coords.pos.x
        self.origin_y = canvas_coords.pos.y
        self.preview_shape = VectorCircle(
            origin_x=self.origin_x,
            origin_y=self.origin_y,
            radius=0
        )
        self.center_marker = VectorMarker(
            origin_x=self.origin_x,
            origin_y=self.origin_y
        )
        return (self.preview_shape, self.center_marker)
    def finalize(self):
        if self.preview_shape.radius == 0:
            return FinalizedShapes(message="radius equal to 0", message_type=ToolStatusMessageType.ERROR)
        return FinalizedShapes([self.preview_shape])
    def move(self, canvas_coords : CanvasCoords) -> tuple[VectorShape, ...] | None:
        if self.previewing:
            x_diff = canvas_coords.pos.x - self.origin_x
            y_diff = canvas_coords.pos.y - self.origin_y
            self.preview_shape.radius = get_tri_hypotenuse(x_diff, y_diff)/2
            self.preview_shape.origin_x = self.origin_x + x_diff/2
            self.preview_shape.origin_y = self.origin_y + y_diff/2
            self.center_marker.origin_x = self.preview_shape.origin_x
            self.center_marker.origin_y = self.preview_shape.origin_y
            return (self.preview_shape, self.center_marker)
        return None
