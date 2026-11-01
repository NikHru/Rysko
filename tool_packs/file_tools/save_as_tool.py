from canvas_manager import StaticDrawingCanvas
from file_manager import EditingFile
from tool_manager import FileTool, get_tool_icon_src

class Tool(FileTool):
    name = "Save File As"
    icon_src = get_tool_icon_src(__file__)
    async def run(self, canvas: StaticDrawingCanvas, editing_file: EditingFile):
        allowed_extensions = list(editing_file.ext_coders.keys())
        default_ext = editing_file.file_ext
        if default_ext == "":
            default_ext = allowed_extensions[0]
        file_path = await editing_file.file_picker.save_file(
            "Save As",
            f"{editing_file.file_name}.{default_ext}",
            str(editing_file.file_path.resolve()),
            allowed_extensions=allowed_extensions
        )
        if file_path is not None:
            editing_file.file_ext = default_ext
            editing_file.set_file(path=file_path)
            editing_file.save(canvas)