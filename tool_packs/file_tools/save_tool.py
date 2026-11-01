from canvas_manager import StaticDrawingCanvas
from file_manager import EditingFile
from tool_manager import FileTool, get_tool_icon_src
from tool_packs.file_tools.save_as_tool import Tool as SaveAsTool

class Tool(FileTool):
    name = "Save File"
    icon_src = get_tool_icon_src(__file__)
    async def run(self, canvas: StaticDrawingCanvas, editing_file: EditingFile):
        if editing_file.file_saved:
            editing_file.save(canvas)
        else:
            await SaveAsTool().run(canvas, editing_file)