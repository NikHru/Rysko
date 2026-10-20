from tool_manager import DrawingTool, FinalizedShapes, ToolStatusMessageType, get_tool_icon_src
from canvas_shapes import VectorLine, VectorRect

class Tool(DrawingTool):
    name = "Rect"
    icon_src = get_tool_icon_src(__file__)
    preview_shape : VectorRect | None = None
    def click(self, event):
        if self.previewing:
            self.previewing = False
            return None
        self.previewing = True
        rect = VectorRect(
            origin_x=getattr(event.local_position, "x"),
            origin_y=getattr(event.local_position, "y"),
            width=0,
            height=0
        )
        self.preview_shape = rect
        return [rect]
    def cancel(self):
        self.previewing = False
        self.preview_shape = None
    def finalize(self):
        if self.preview_shape is None or self.preview_shape.width == 0 or self.preview_shape.height == 0:
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
    def move(self, event):
        if self.previewing and self.preview_shape is not None:
            self.preview_shape.width = event.local_position.x - self.preview_shape.origin_x
            self.preview_shape.height = event.local_position.y - self.preview_shape.origin_y
            return [self.preview_shape]
        return None