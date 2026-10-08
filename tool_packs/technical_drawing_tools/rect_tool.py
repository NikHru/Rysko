import flet.canvas as fcv
from tool_manager import DrawingTool, FinalizedShapes, ToolStatusMessageType, get_tool_icon_src

class Tool(DrawingTool):
    name = "Rect"
    icon_src = get_tool_icon_src(__file__)
    preview_shape : fcv.Rect | None = None
    def click(self, event) -> list[fcv.Shape] | None:
        if self.previewing:
            self.previewing = False
            return None
        self.previewing = True
        rect = fcv.Rect(
            x=event.local_position.x,
            y=event.local_position.y,
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
        far_y = self.preview_shape.y + self.preview_shape.height
        far_x = self.preview_shape.x + self.preview_shape.width
        return FinalizedShapes([
            fcv.Line(x1=self.preview_shape.x, y1=self.preview_shape.y, x2=far_x, y2=self.preview_shape.y),
            fcv.Line(x1=self.preview_shape.x, y1=self.preview_shape.y, x2=self.preview_shape.x, y2=far_y),
            fcv.Line(x1=self.preview_shape.x, y1=far_y, x2=far_x, y2=far_y),
            fcv.Line(x1=far_x, y1=self.preview_shape.y, x2=far_x, y2=far_y)
        ])
    def move(self, event):
        if self.previewing and self.preview_shape is not None:
            self.preview_shape.width = event.local_position.x - self.preview_shape.x
            self.preview_shape.height = event.local_position.y - self.preview_shape.y