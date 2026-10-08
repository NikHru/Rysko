import flet.canvas as fcv
from tool_manager import DrawingTool, FinalizedShapes, ToolStatusMessageType, get_tool_icon_src

class Tool(DrawingTool):
    name = "Line"
    icon_src = get_tool_icon_src(__file__)
    preview_shape : fcv.Line | None = None
    def click(self, event) -> list[fcv.Shape] | None:
        if self.previewing:
            self.previewing = False
            return None
        self.previewing = True
        line = fcv.Line(
            x1=event.local_position.x,
            y1=event.local_position.y,
            x2=event.local_position.x,
            y2=event.local_position.y
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
            self.preview_shape.x2 = event.local_position.x
            self.preview_shape.y2 = event.local_position.y