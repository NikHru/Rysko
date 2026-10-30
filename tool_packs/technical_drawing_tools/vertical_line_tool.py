from tool_manager import get_tool_icon_src
from tool_packs.technical_drawing_tools.free_line_tool import Tool as LineDrawingTool

class Tool(LineDrawingTool):
    name = "Vertical Line"
    icon_src = get_tool_icon_src(__file__)
    def move(self, canvas_coords):
        if self.previewing and self.preview_shape is not None:
            self.preview_shape.length_y = canvas_coords.pos.y - self.preview_shape.origin_y
            return (self.preview_shape,)
        return None