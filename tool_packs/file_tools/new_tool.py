from canvas_manager import StaticDrawingCanvas
from file_manager import EditingFile
from tool_manager import FileTool, get_tool_icon_src

class Tool(FileTool):
    name = "New File"
    icon_src = get_tool_icon_src(__file__)
    async def run(self, canvas: StaticDrawingCanvas, editing_file: EditingFile):
        editing_file.clear(canvas)