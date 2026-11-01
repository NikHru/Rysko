from canvas_manager import StaticDrawingCanvas
from file_manager import EditingFile
from tool_manager import FileTool, get_tool_icon_src

class Tool(FileTool):
    name = "Open File"
    icon_src = get_tool_icon_src(__file__)
    async def run(self, canvas: StaticDrawingCanvas, editing_file: EditingFile):
        picked_files = await editing_file.file_picker.pick_files(
            "Open",
            str(editing_file.file_path.resolve()),
            allowed_extensions=list(editing_file.ext_coders.keys())
        )
        if len(picked_files) == 1 and picked_files[0].path is not None:
            editing_file.load(picked_files[0].path, canvas)