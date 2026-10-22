from tool_manager import DrawingTool, FinalizedShapes, ToolStatusMessageType, get_tool_icon_src
from canvas_shapes import VectorLine

class Tool(DrawingTool):
    name = "Line"
    icon_src = get_tool_icon_src(__file__)
    preview_shape : VectorLine | None = None
    def click(self, event):
        if self.previewing:
            self.previewing = False
            return None
        self.previewing = True
        line = VectorLine(
            origin_x=getattr(event.local_position, "x"),
            origin_y=getattr(event.local_position, "y"),
            length_x=0,
            length_y=0
        )
        self.preview_shape = line
        return [line]
    def cancel(self):
        self.previewing = False
        self.preview_shape = None
    def finalize(self):
        if self.preview_shape is None or (self.preview_shape.x1 == self.preview_shape.x2 and self.preview_shape.y1 == self.preview_shape.y2):
            return FinalizedShapes(message="equal start and end point", message_type=ToolStatusMessageType.ERROR)
        return FinalizedShapes([self.preview_shape])
    def move(self, event):
        if self.previewing and self.preview_shape is not None:
            self.preview_shape.length_x = event.local_position.x - self.preview_shape.origin_x
            self.preview_shape.length_y = event.local_position.y - self.preview_shape.origin_y
            return [self.preview_shape]
        return None