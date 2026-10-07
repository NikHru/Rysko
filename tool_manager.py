import flet.canvas as fcv
import flet as ft
import pathlib
import logging as loglib
import utils
import json
from enum import Enum
from canvas_manager import DrawingCanvas
from elements import ToggleIconButton

TOOLBAR_HEIGHT = 35
TOOLBAR_ICON_NORM_SCALE_HEIGHT = 30

logger = loglib.getLogger("main")

registered_tools : dict[str, type["DrawingTool"]] = {}
def register_tool(tool_file_path : pathlib.Path):
    if not tool_file_path.is_file():
        raise ValueError(f"Invalid tool file path {tool_file_path}.")
    if tool_file_path.name in registered_tools:
        logger.warning(f"DrawingTool under the name \"{utils.filename(tool_file_path)}\" duplicate registry attempt")
    else:
        module = utils.import_module_by_path(tool_file_path)
        if "Tool" not in dir(module) or not issubclass(module.Tool, DrawingTool):
            raise ValueError(f"No or invalid Tool class in tool file \"{tool_file_path.name}\"")
        registered_tools[utils.filename(tool_file_path)] = module.Tool
def register_tools_from_directory(tool_dir_name:str="drawing_tools"):
    tool_dir_path = pathlib.Path(__file__).resolve().parent / tool_dir_name
    if not tool_dir_path.is_dir():
        raise ValueError("Invalid tool directory path")
    for tool_file_path in tool_dir_path.glob("*_tool.py"):
        try:
            register_tool(tool_file_path)
        except (ImportError, ModuleNotFoundError, ValueError) as e:
            logger.error(f"Failed to load DrawingTool \"{tool_file_path.name}\"", exc_info=e)

class ToolStatusMessageType(Enum):
    INFO = 1
    WARNING = 2
    ERROR = 3
class FinalizedShapes:
    shapes : list[fcv.Shape] | None
    status_message : str | None
    status_message_type : ToolStatusMessageType = ToolStatusMessageType.INFO
    def __init__(self, shapes : list[fcv.Shape] | None = None, message : str | None = None, message_type : ToolStatusMessageType = ToolStatusMessageType.INFO):
        self.shapes = shapes
        self.status_message = message
        self.status_message_type = message_type
class DrawingTool:
    name : str
    icon : ft.IconDataOrControl
    previewing : bool = False
    def __init__(self):
        pass
    def click(self, event : ft.TapEvent[ft.GestureDetector]) -> list[fcv.Shape] | None:
        return None
    def cancel(self):
        self.previewing = False
    def finalize(self) -> FinalizedShapes | None:
        return None
    def move(self, event : ft.PointerEvent[ft.GestureDetector]):
        pass

class ToolButton(ToggleIconButton):
    tool_idx : int
    parent_toolbar : "Toolbar"
    def __init__(self, tool_class : type[DrawingTool], tool_idx : int, toolbar : "Toolbar", icon_scale = 1):
        super().__init__(
            icon_scale=icon_scale,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=4),
                padding=0,
                visual_density=ft.VisualDensity.COMPACT
            ),
            aspect_ratio = 1,
            icon=tool_class.icon
        )
        self.parent_toolbar = toolbar
        self.tool_idx = tool_idx
        self.tooltip = tool_class.name
    def on_click_callback(self, event : ft.Event[ft.IconButton]):
        if event.name == "click":
            self.parent_toolbar.select_tool(self.tool_idx if self.selected else -1)
class ToolbarToolRow(ft.Row):
    controls : list[ToolButton]
    def __init__(self):
        super().__init__()
        self.vertical_alignment = ft.CrossAxisAlignment.STRETCH
        self.expand = True
        self.spacing = 0
        self.margin = 2
class Toolbar(ft.Container):
    content : ft.Column
    toolbar_row : ToolbarToolRow
    row_divider : ft.Divider
    tool_config_row : ft.Row
    loaded_config : str | None = None
    loaded_tool_classes : list[type[DrawingTool]] = []
    selected_tool_idx : int = -1
    selected_tool : DrawingTool | None = None
    selected_tool_preview_shapes : list[fcv.Shape] | None = None
    canvas : DrawingCanvas
    def __init__(self, config_str_path : str | None, canvas : DrawingCanvas):
        super().__init__(
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            height=TOOLBAR_HEIGHT
        )
        self.canvas = canvas
        self.canvas.gesture_detector.on_tap = self._gesture_detector_tap
        self.canvas.gesture_detector.on_secondary_tap = self._gesture_detector_secondary_tap
        self.canvas.gesture_detector.on_hover = self._gesture_detector_hover

        self.content = ft.Column()
        self.content.expand = True
        self.content.spacing = 0

        self.toolbar_row = ToolbarToolRow()
        self.content.controls.append(self.toolbar_row)

        self.row_divider = ft.Divider()
        self.row_divider.visible = False
        self.content.controls.append(self.row_divider)

        self.tool_config_row = ft.Row()
        self.tool_config_row.visible = False
        self.content.controls.append(self.tool_config_row)

        if config_str_path is not None:
            self.load_config(config_str_path)
    def clear_config(self):
        self.loaded_config = None
        self.clear_selected_tool()
        self.toolbar_row.controls.clear()
        self.loaded_tool_classes.clear()
    def load_config(self, config_str_path : str):
        config_path = utils.get_assets_path() / config_str_path
        if not config_path.is_file():
            raise ValueError("Invalid toolbar config filepath")
        config_file = config_path.open("r")
        tool_list = json.load(config_file)
        config_file.close()
        if not isinstance(tool_list, list):
            raise ValueError("Invalid toolbar config, needs to be an array")
        if self.loaded_config is not None:
            self.clear_config()
        self.loaded_config = config_str_path
        icon_scale : float = self.height / TOOLBAR_ICON_NORM_SCALE_HEIGHT
        tool_idx = 0
        for tool_name in tool_list:
            if tool_name in registered_tools:
                tool_class = registered_tools[tool_name]
                button = ToolButton(tool_class, tool_idx, self, icon_scale)
                self.loaded_tool_classes.append(tool_class)
                self.toolbar_row.controls.append(button)
                tool_idx += 1
            else:
                logger.warning(f"No tool under the name \"{tool_name}\" is registered, parent config: {config_path}")
    def clear_selected_tool_preview(self):
        if self.selected_tool is not None and self.selected_tool_preview_shapes is not None:
            self.canvas.remove_shapes(self.selected_tool_preview_shapes, preview=True)
    def clear_selected_tool(self):
        if self.selected_tool is not None:
            tool_button = self.toolbar_row.controls[self.selected_tool_idx]
            if tool_button.selected:
                tool_button.set_selected(False)
            self.clear_selected_tool_preview()
            self.selected_tool.cancel()
            self.selected_tool = None
            self.selected_tool_idx = -1
    def select_tool(self, tool_idx : int):
        self.clear_selected_tool()
        if -1 < tool_idx < len(self.loaded_tool_classes):
            self.selected_tool_idx = tool_idx
            selected_tool = self.loaded_tool_classes[tool_idx]()
            self.selected_tool = selected_tool
    def finalize_selected_tool(self):
        if self.selected_tool is not None:
            self.clear_selected_tool_preview()
            finalized_shapes = self.selected_tool.finalize()
            if finalized_shapes is not None:
                if finalized_shapes.status_message is not None:
                    pass # TODO: show toolbar message is any specified
                if finalized_shapes.shapes is not None:
                    self.canvas.add_shapes(finalized_shapes.shapes, preview=False)
            self.selected_tool = self.loaded_tool_classes[self.selected_tool_idx]() # discard old tool inst
    def _gesture_detector_tap(self, event : ft.TapEvent[ft.GestureDetector]):
        if self.selected_tool is not None:
            preview_shapes = self.selected_tool.click(event)
            if self.selected_tool.previewing:
                if preview_shapes is not None:
                    collected_preview_shapes = self.selected_tool_preview_shapes
                    if collected_preview_shapes is not None:
                        collected_preview_shapes.extend(preview_shapes)
                    else:
                        collected_preview_shapes = preview_shapes
                    self.selected_tool_preview_shapes = collected_preview_shapes
                    self.canvas.add_shapes(preview_shapes, preview=True)
            else:
                self.finalize_selected_tool()
    def _gesture_detector_secondary_tap(self):
        if self.selected_tool is not None:
            if self.selected_tool.previewing:
                self.clear_selected_tool_preview()
                self.selected_tool.cancel()
                self.selected_tool = self.loaded_tool_classes[self.selected_tool_idx]() # discard old tool inst
            else:
                self.clear_selected_tool()
    def _gesture_detector_hover(self, event : ft.PointerEvent[ft.GestureDetector]):
        if self.selected_tool is not None:
            self.selected_tool.move(event)

def get_tool_assets_path(tool_file_path : str) -> pathlib.Path:
    return utils.get_assets_path() / "drawing_tools" / utils.filename(pathlib.Path(tool_file_path))
def get_tool_icon(tool_file_path : str) -> ft.Image:
    return ft.Image(f"drawing_tools/{utils.filename(pathlib.Path(tool_file_path))}/icon.png", anti_alias=True)