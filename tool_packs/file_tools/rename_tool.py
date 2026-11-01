from canvas_manager import StaticDrawingCanvas
from file_manager import EditingFile
from tool_manager import FileTool, get_tool_icon_src
from tool_packs.file_tools.save_as_tool import Tool as SaveAsTool

class Tool(FileTool):
    name = "Rename File"
    icon_src = get_tool_icon_src(__file__)
    async def run(self, canvas: StaticDrawingCanvas, editing_file: EditingFile):
        if editing_file.file_saved:
            rename_path = await editing_file.file_picker.save_file(
                "Rename",
                f"{editing_file.file_name}.{editing_file.file_ext}",
                str(editing_file.file_path.resolve()),
                allowed_extensions=list(editing_file.ext_coders.keys())
            )
            if rename_path is not None:
                editing_file.rename_current(rename_path, new_ext=editing_file.file_ext)
        else:
            await SaveAsTool().run(canvas, editing_file)