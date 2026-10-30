# only for tool directory to be registered as a module so in installation tools under it can be accessed as submodules
# TEMPLATE:
"""
from tool_manager import DrawingTool, FinalizedShapes, ToolStatusMessageType, get_tool_icon_src
from canvas_shapes import VectorLine

class Tool(DrawingTool):
    name = "Line"
    icon_src = get_tool_icon_src(__file__)
    preview_shape : VectorLine | None = None
"""