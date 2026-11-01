import flet as ft
import pathlib
import logging as loglib
import utils
import json
import importlib
import canvas_manager
import file_manager
import pynput
from enum import Enum
from elements import (
    ToggleIconButton, GestureDetectorCallbacks, KeyState, RibbonControlsRow,
    ControlDisplay, ControlDisplayIcon, ScaledText
)
from canvas_shapes import VectorShape
from utils import read_dict
logger = loglib.getLogger("main")

registered_tools : dict[str, type["ToolrowTool"]] = {}
def register_tool(name : str, tool_pack_name : str):
    register_name = f"{tool_pack_name}.{name}"
    if register_name in registered_tools:
        logger.warning(f"ToolrowTool under the import path \"{register_name}\" duplicate registry attempt")
    else:
        try:
            module = importlib.import_module(f"tool_packs.{register_name}")
            if "Tool" not in dir(module) or not issubclass(module.Tool, ToolrowTool):
                raise ValueError(f"No or invalid Tool class in tool file under import path \"{register_name}\"")
            registered_tools[register_name] = module.Tool
        except (ModuleNotFoundError, ImportError):
            raise ValueError(f"Invalid tool import path \"{register_name}\"")
def register_tools_from_pack(tool_pack_name : str):
    pack_assets_dir = utils.get_assets_path() / "tool_packs" / tool_pack_name
    if not pack_assets_dir.is_dir():
        raise ValueError("Invalid tool pack name")
    try:
        importlib.import_module(f"tool_packs.{tool_pack_name}")
    except (ModuleNotFoundError, ImportError):
        raise ValueError("Invalid tool pack name")
    for tool_assets_dir in pack_assets_dir.iterdir():
        if tool_assets_dir.is_dir() and not tool_assets_dir.name.startswith(("__", ".")):
            try:
                register_tool(tool_assets_dir.name, tool_pack_name)
            except ValueError as e:
                logger.error(f"Failed to load ToolrowTool at import path \"{tool_pack_name}.{tool_assets_dir.name}\"", exc_info=e)

class CanvasCoords:
    pos : ft.Offset
    delta : ft.Offset
    def __init__(self, pos : ft.Offset | None = None, delta : ft.Offset | None = None):
        self.pos = pos or ft.Offset()
        self.delta = delta or ft.Offset()
class ToolStatusMessageType(Enum):
    INFO = 1
    WARNING = 2
    ERROR = 3
class FinalizedShapes:
    shapes : list[VectorShape] | None
    status_message : str | None
    status_message_type : ToolStatusMessageType = ToolStatusMessageType.INFO
    def __init__(self, shapes : list[VectorShape] | None = None, message : str | None = None, message_type : ToolStatusMessageType = ToolStatusMessageType.INFO):
        self.shapes = shapes
        self.status_message = message
        self.status_message_type = message_type

class ToolrowTool:
    name : str
    icon_src : ft.IconData | str
    toggle : bool = True
    def __init__(self):
        pass
    def discard(self):
        pass
class ToolrowLinkTool[ToolType : ToolrowTool](ToolrowTool):
    tool_data : "LoadedToolData[ToolType]"
    local_path : str = "tool_packs"
    config_path : str = "{local}/toolrow.json"
    def __init__(
        self, toolrow : "ToolRow[ToolType]", auto_assign_keybinds : bool, auto_keybind_mod_key : str | None = None, auto_keybind_prefix : str = ""
    ):
        self.tool_data = LoadedToolData(
            self.config_path, toolrow, auto_assign_keybinds,
            auto_keybind_mod_key, auto_keybind_prefix, local_path=self.local_path
        )
class FileTool(ToolrowTool):
    toggle : bool = False
    async def run(self, canvas : canvas_manager.StaticDrawingCanvas, editing_file : file_manager.EditingFile):
        pass
class CanvasTool(ToolrowTool):
    def click(self, canvas_coords : CanvasCoords):
        pass
    def move(self, canvas_coords : CanvasCoords):
        pass
class DrawingTool(CanvasTool):
    previewing : bool = False
    uniform_tooltip : str | None = None
    place_tooltip : str | None = None
    repeat : bool = False
    repeat_start_coords : CanvasCoords | None = None
    def click(self, canvas_coords : CanvasCoords) -> tuple[VectorShape, ...] | None:
        return None
    def discard(self):
        self.previewing = False
    def move(self, canvas_coords : CanvasCoords) -> tuple[VectorShape, ...] | None:
        pass
    def finalize(self) -> FinalizedShapes | None:
        return None
    def set_uniform(self, uniform : bool) -> tuple[VectorShape, ...] | None:
        pass

class ToolButton(ft.Row):
    tool_idx : int
    tool_group : str | int
    parent_toolbar : "ToolRow"
    button : ToggleIconButton
    key_text : ScaledText
    mod_key_text : ScaledText
    mod_key_rotated_box : ft.RotatedBox
    linked : bool = False
    def __init__(
        self, tool_class : type[ToolrowTool], tool_idx : int, tool_group : str | int,
        toolbar : "ToolRow", key : str = "", mod_key : str = ""
    ):
        super().__init__(
            spacing=1,
            vertical_alignment=ft.CrossAxisAlignment.STRETCH,
            expand_loose=True
        )
        self.button = ToggleIconButton(
            on_click=self._on_click_callback,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=4),
                padding=2,
                visual_density=ft.VisualDensity.COMPACT
            ),
            aspect_ratio = 1,
            icon = utils.icon_src_to_image(tool_class.icon_src, anti_alias=True)
        )
        self.key_text = ScaledText(
            12, 5, key, aspect_ratio=0.3, scale_div=3,
            text_align=ft.TextAlign.CENTER, color=ft.Colors.ON_SURFACE_VARIANT
        )
        self.key_text.visible = key != ""
        self.mod_key_text = self.keybind_text = ScaledText(
            15, 14, mod_key, italic=True, expand=True,
            text_align=ft.TextAlign.CENTER, color=ft.Colors.ON_SURFACE_VARIANT
        )
        self.mod_key_rotated_box = ft.RotatedBox(content=self.mod_key_text, quarter_turns=-1, aspect_ratio=0.35)
        self.mod_key_rotated_box.visible = mod_key != ""
        self.parent_toolbar = toolbar
        self.tool_idx = tool_idx
        self.tool_group = tool_group
        self.tooltip = tool_class.name
        self.controls = [self.mod_key_rotated_box, self.key_text, self.button]
    def set_linked(self, key : str | None = None, mod_key : str | None = None):
        self.linked = True
        if key is not None:
            if self.key_text.data is None:
                self.key_text.data = self.key_text.value
            self.key_text.value = key
        if mod_key is not None:
            if self.mod_key_text.data is None:
                self.mod_key_text.data = self.mod_key_text.value
            self.mod_key_text.value = mod_key
    def discrad_linked(self):
        self.linked = False
        if type(self.key_text.data) is str:
            self.key_text.value = self.key_text.data
            self.key_text.data = None
        if type(self.mod_key_text.data) is str:
            self.mod_key_text.value = self.mod_key_text.data
            self.key_text.data = None
    def _on_click_callback(self, *_):
        if self.linked:
            self.parent_toolbar.apply_loaded(None)
        else:
            self.parent_toolbar.select_tool(self.tool_idx)
class LoadedToolData[ToolType : ToolrowTool]:
    config : str
    classes : list[type[ToolType] | ToolrowLinkTool[ToolType]]
    buttons : list[ToolButton]
    groups : dict[str, list[ToolButton]]
    keybinds : dict[str | None, dict[str, ToolButton]]
    toolrow : "ToolRow[ToolType]"
    def __init__(
        self, config_str_path : str, toolrow : "ToolRow[ToolType]", auto_assign_keybinds : bool,
        auto_keybind_mod_key : str | None = None, auto_keybind_prefix : str = "", local_path : str = "tool_packs"
    ):
        self.toolrow = toolrow
        self.load_config(config_str_path, auto_assign_keybinds, auto_keybind_mod_key, auto_keybind_prefix, local_path)
    def load_config(
        self, config_str_path : str, auto_assign_keybinds : bool,
        auto_keybind_mod_key : str | None = None, auto_keybind_prefix : str = "", local_path : str = "tool_packs"
    ):
        config_path = utils.get_assets_path() / config_str_path.format(local=local_path)
        if not config_path.is_file():
            raise ValueError(f"Invalid toolbar config filepath: {config_path}")
        config_file = config_path.open("r")
        tool_list = json.load(config_file)
        config_file.close()
        if not isinstance(tool_list, list):
            raise ValueError("Invalid toolbar config, needs to be an array")
        local_path_start = local_path.split("/")[0]
        pack_name = local_path_start
        config_path_parent = config_path
        while config_path_parent.name != local_path_start:
            pack_name = config_path_parent.name
            config_path_parent = config_path_parent.parent
        # clear previouse
        self.classes = []
        self.buttons = []
        self.groups = {}
        self.keybinds = {}
        self.config = config_str_path
        # load new
        tool_idx = 0
        tool_keybind_idx = 0
        for i, tool_data in enumerate(tool_list):
            tool_name : str = ""
            tool_key : str = ""
            tool_key_prefix : str = ""
            tool_mod_key : str | None = None
            tool_group : str | None = "main"
            if type(tool_data) is str:
                tool_name = tool_data
            elif type(tool_data) is dict:
                tool_name = read_dict(tool_data, "name", str, "")
                tool_key = read_dict(tool_data, "key", str, "")
                tool_key_prefix = read_dict(tool_data, "key_prefix", str, "")
                tool_mod_key = read_dict(tool_data, "mod_key", (str, type(None)), None)
                tool_group = read_dict(tool_data, "group", (str, type(None)), "main")
            tool_name = tool_name.format(local=pack_name)
            if tool_name == "":
                logger.warning(f"Invalid tool at index {i} of config: {config_path}")
            elif tool_name in registered_tools:
                tool_class = registered_tools[tool_name]
                if issubclass(tool_class, (self.toolrow.tool_type, ToolrowLinkTool)):
                    if auto_assign_keybinds and tool_key == "":
                        if tool_keybind_idx == 9:
                            tool_key = "0"
                        elif tool_keybind_idx < 9:
                            tool_key = str(tool_idx+1)
                        if tool_key_prefix == "" and auto_keybind_mod_key is not None:
                            tool_key_prefix = auto_keybind_prefix
                        tool_keybind_idx += 1
                    button = ToolButton(
                        tool_class, tool_idx, (tool_group or tool_idx),
                        self.toolrow, tool_key, tool_key_prefix
                    )
                    # loaded tool list
                    if issubclass(tool_class, ToolrowLinkTool):
                        self.classes.append(tool_class(
                            self.toolrow, auto_assign_keybinds, auto_keybind_mod_key, auto_keybind_prefix
                        ))
                    else:
                        self.classes.append(tool_class)
                    self.buttons.append(button)
                    # tool keybind
                    if tool_key != "":
                        if tool_mod_key not in self.keybinds:
                            self.keybinds[tool_mod_key] = {}
                        self.keybinds[tool_mod_key][tool_key] = button
                    # tool grop
                    if tool_group is not None:
                        if tool_group not in self.groups:
                            self.groups[tool_group] = []
                        self.groups[tool_group].append(button)
                    tool_idx += 1
                else:
                    logger.warning(f"Tool \"{tool_name}\" is not a {self.toolrow.tool_type}, index {i} in parent config: {config_path}")
            else:
                logger.warning(f"No tool under the name \"{tool_name}\" is registered, index {i} in parent config: {config_path}")
class ToolRow[ToolType : ToolrowTool](ft.Row):
    tool_type : type[ToolType]
    loaded_stack : list[ToolrowLinkTool[ToolType] | LoadedToolData[ToolType]]
    loaded : LoadedToolData[ToolType]
    _arrow_image : ft.Image = ft.Image(
        "icons/shallow_arrow_right.png", anti_alias=True, 
        fit=ft.BoxFit.FIT_HEIGHT, color=ft.Colors.ON_SURFACE_VARIANT
    )
    _mod_key : str | None = None
    selected_tool_indexes : dict[str | int, int]
    selected_tools : dict[int, ToolType]
    canvas : canvas_manager.StaticDrawingCanvas
    controls_row : RibbonControlsRow
    auto_assign_keybinds : bool
    auto_keybind_prefix : str
    auto_keybind_mod_key : str | None
    stack_close_key : str = ""
    stack_close_key_prefix : str = ""
    stack_close_mod_key : str | None = None
    def __init__(
        self, tool_type : type[ToolType], config_str_path : str, canvas : canvas_manager.StaticDrawingCanvas,
        controls_row : RibbonControlsRow, auto_assign_keybinds : bool = False, auto_keybind_prefix : str = "",
        auto_keybind_mod_key : str | None = None, stack_close_key : str = "", stack_close_key_prefix : str = "",
        stack_close_mod_key : str | None = None, **kwargs
    ):
        kwargs["vertical_alignment"] = ft.CrossAxisAlignment.STRETCH
        kwargs["spacing"] = 15
        kwargs["margin"] = -2
        super().__init__(**kwargs)
        self.tool_type = tool_type
        self._pressed_keys = []
        self.selected_tool_indexes = {}
        self.selected_tools = {}

        self.canvas = canvas
        self.canvas.keyboard_listener.add_callback(None, KeyState.DOWN, self._key_event)
        self.canvas.keyboard_listener.add_callback(None, KeyState.UP, self._key_event)
        self.controls_row = controls_row

        self.auto_assign_keybinds = auto_assign_keybinds
        self.auto_keybind_prefix = auto_keybind_prefix
        self.auto_keybind_mod_key = auto_keybind_mod_key
        self.stack_close_key = stack_close_key
        self.stack_close_key_prefix = stack_close_key_prefix
        self.stack_close_mod_key = stack_close_mod_key

        self.loaded_stack = []
        self.apply_loaded(LoadedToolData(
            config_str_path, self,
            self.auto_assign_keybinds,
            self.auto_keybind_mod_key,
            self.auto_keybind_prefix
        ))
    def apply_loaded(self, toolrow_link : LoadedToolData[ToolType] | ToolrowLinkTool[ToolType] | None):
        # unload old
        if toolrow_link is None:
            if len(self.loaded_stack) <= 1:
                return # early return, no stack links to close, nothing will happen
            prev_toolrow_link = self.loaded_stack.pop()
            toolrow_link = self.loaded_stack[-1]
            if isinstance(prev_toolrow_link, ToolrowLinkTool): # always is
                prev_loaded_data = toolrow_link.tool_data if isinstance(toolrow_link, ToolrowLinkTool) else toolrow_link
                prev_link_button = prev_loaded_data.buttons[prev_loaded_data.classes.index(prev_toolrow_link)]
                prev_link_button.discrad_linked()
                prev_link_button.button.set_selected(False)
        # get new parts
        link_button : ToolButton | None = None
        loaded_data : LoadedToolData[ToolType]
        if isinstance(toolrow_link, ToolrowLinkTool):
            loaded_data = toolrow_link.tool_data
            link_button = self.loaded.buttons[self.loaded.classes.index(toolrow_link)]
        else:
            loaded_data = toolrow_link
        # unselect selected tools
        for group in list(self.selected_tool_indexes.keys()):
            if link_button is None or group != link_button.tool_group:
                self.clear_tool(group)
        # load new
        if len(self.loaded_stack) == 0 or self.loaded_stack[0] is not toolrow_link:
            self.loaded_stack.append(toolrow_link)
        self.loaded = loaded_data
        self.controls = []
        if link_button is not None:
            loaded_stack_row = ft.Row(
                spacing=5, vertical_alignment=ft.CrossAxisAlignment.STRETCH, expand_loose=True
            )
            link_button.set_linked(self.stack_close_key, self.stack_close_key_prefix)
            for _ in range(len(self.loaded_stack)-2):
                loaded_stack_row.controls.append(self._arrow_image)
            loaded_stack_row.controls.append(link_button)
            loaded_stack_row.controls.append(self._arrow_image)
            self.controls.append(loaded_stack_row)
        for button in self.loaded.buttons:
            self.controls.append(button)
        if self.parent is not None:
            self.update()
    def select_tool(self, tool_idx : int, reselect : bool = False):
        if -1 < tool_idx < len(self.loaded.classes):
            tool_button = self.loaded.buttons[tool_idx]
            prev_tool = self.selected_tool_indexes.get(tool_button.tool_group)
            self.clear_tool(tool_button.tool_group)
            if tool_idx != prev_tool or reselect:
                if not tool_button.button.selected:
                    tool_button.button.set_selected(True)
                tool_class : type[ToolType] | ToolrowLinkTool = self.loaded.classes[tool_idx]
                if isinstance(tool_class, ToolrowLinkTool):
                    self.apply_loaded(tool_class)
                elif issubclass(tool_class, self.tool_type):
                    self.selected_tool_indexes[tool_button.tool_group] = tool_idx
                    tool = tool_class()
                    self.selected_tools[tool_idx] = tool
                    self.on_tool_selected(tool_idx)
                    if not tool.toggle:
                        self.clear_tool(tool_button.tool_group)
    def on_tool_selected(self, tool_idx : int):
        pass
    def clear_tool(self, group : str | int):
        selected_tool_index = self.selected_tool_indexes.get(group)
        if selected_tool_index is not None:
            tool_button = self.loaded.buttons[selected_tool_index]
            if tool_button.button.selected:
                tool_button.button.set_selected(False)
            self.selected_tools[selected_tool_index].discard()
            self.on_tool_cleared()
            self.selected_tools.pop(selected_tool_index)
            self.selected_tool_indexes.pop(group)
    def on_tool_cleared(self):
        pass
    def _key_event(self, event : ft.KeyDownEvent | ft.KeyUpEvent):
        if isinstance(event, ft.KeyUpEvent):
            if event.key == self._mod_key:
                self._mod_key = None
        else:
            if len(self.loaded_stack) > 1 and self._mod_key == self.stack_close_mod_key and event.key == self.stack_close_key:
                self.apply_loaded(None)
            elif self._mod_key in self.loaded.keybinds and event.key in self.loaded.keybinds[self._mod_key]:
                self.select_tool(self.loaded.keybinds[self._mod_key][event.key].tool_idx)
            self._mod_key = event.key

class DrawingToolRow(ToolRow[DrawingTool]):
    selected_tool_preview_shapes : list[VectorShape] | None = None
    preview_unlocked : bool = False
    preview_uniform : bool = False
    tool_click_control_display : ControlDisplay
    tool_cancel_control_display : ControlDisplay
    tool_uniform_mode_control_display : ControlDisplay
    preview_unlock_control_display : ControlDisplay
    _mouse_controller : pynput.mouse.Controller
    _ignore_click : bool = False
    _control_is_pressed : bool = False
    _last_canvas_coords : CanvasCoords | None = None
    def __init__(
        self, config_str_path : str, canvas : canvas_manager.StaticDrawingCanvas, controls_row : RibbonControlsRow,
        auto_assign_keybinds : bool = False, auto_keybind_prefix : str = "", auto_keybind_mod_key : str | None = None, 
        stack_close_key : str = "", stack_close_key_prefix : str = "", stack_close_mod_key : str | None = None, **kwargs
    ):
        super().__init__(DrawingTool,
            config_str_path, canvas, controls_row, auto_assign_keybinds,
            auto_keybind_prefix, auto_keybind_mod_key, stack_close_key,
            stack_close_key_prefix, stack_close_mod_key, **kwargs
        )

        self.canvas.gesture_detector.add_callback(GestureDetectorCallbacks.TAP, self._mouse_tap)
        self.canvas.gesture_detector.add_callback(GestureDetectorCallbacks.SECONDARY_TAP, self.selected_tool_cancel)
        self.canvas.gesture_detector.add_callback(GestureDetectorCallbacks.HOVER, self._mouse_hover)
        self.canvas.keyboard_listener.add_callback("Escape", KeyState.DOWN, self.selected_tool_cancel)
        self.canvas.keyboard_listener.add_callback("Alt Left", KeyState.UP, self._alt_up)
        self.canvas.keyboard_listener.add_callback("Control Left", KeyState.DOWN, self._ctrl_pressed)
        self.canvas.keyboard_listener.add_callback("Control Left", KeyState.UP, self._ctrl_pressed)
        self._mouse_controller = pynput.mouse.Controller()

        self.tool_cancel_control_display = ControlDisplay(
            "Deselect Tool", key_or_icon_list=[ControlDisplayIcon.MOUSE_RIGHT, "ESC"], visible=False
        )
        self.controls_row.add_control("tool_cancel", self.tool_cancel_control_display)
        self.tool_click_control_display = ControlDisplay(
            "Place", key_or_icon_list=[ControlDisplayIcon.MOUSE_LEFT], visible=False
        )
        self.controls_row.add_control("tool_click", self.tool_click_control_display)
        self.tool_uniform_mode_control_display = ControlDisplay(
            "Uniform", key_or_icon_list=["CTRL"], visible=False
        )
        self.controls_row.add_control("tool_uniform_mode", self.tool_uniform_mode_control_display)
        self.preview_unlock_control_display = ControlDisplay(
            "Unlock Preview", key_or_icon_list=["ALT"], visible=False
        )
        self.controls_row.add_control("tool_preview_unlock", self.preview_unlock_control_display)
        self.controls_row.add_control("canvas_move", ControlDisplay(
            "Move Canvas", key_or_icon_list=[ControlDisplayIcon.MOUSE_LEFT_DRAG]
        ))
    # tool selection
    def on_tool_selected(self, tool_idx : int):
        self.controls_row.set_control_visible("tool_click", True)
        self.controls_row.set_control_visible("tool_cancel", True)
    def on_tool_cleared(self):
        self.controls_row.set_control_visible("tool_click", False)
        self.controls_row.set_control_visible("tool_cancel", False)
        self.tool_clear_preview()
    def selected_tool_cancel(self, *_):
        selected_tool_idx = self.selected_tool_indexes.get("main")
        if selected_tool_idx is not None and not self.preview_unlocked:
            selected_tool = self.selected_tools[selected_tool_idx]
            if selected_tool.previewing:
                self.select_tool(selected_tool_idx, True) # discard old tool inst
            else:
                self.clear_tool("main")
    # tool state
    def tool_click(self, selected_tool : DrawingTool, selected_tool_idx : int, canvas_coords : CanvasCoords):
        self._last_canvas_coords = canvas_coords
        preview_shapes = selected_tool.click(canvas_coords)
        was_previewed = self.selected_tool_preview_shapes is not None
        if not was_previewed:
            self.tool_initial_click(selected_tool, selected_tool_idx, canvas_coords)
        if selected_tool.previewing:
            self.tool_start_preview(preview_shapes)
            self.tool_update_tooltips(selected_tool)
        else:
            self.tool_finalize(selected_tool, selected_tool_idx)
            if was_previewed and selected_tool.repeat:
                if selected_tool.repeat_start_coords is not None:
                    canvas_coords = selected_tool.repeat_start_coords
                # get new tool since self.tool_finalize reloads the tool
                new_selected_tool = self.selected_tools[self.selected_tool_indexes.get("main", 0)]
                self.tool_click(new_selected_tool, selected_tool_idx, canvas_coords)
    def tool_initial_click(self, selected_tool : DrawingTool, selected_tool_idx : int, canvas_coords : CanvasCoords):
        if selected_tool.uniform_tooltip is not None and self._control_is_pressed:
            self.tool_set_uniform(selected_tool, True)
    def tool_finalize(self, selected_tool : DrawingTool, selected_tool_idx : int):
        self.tool_clear_preview()
        finalized_shapes = selected_tool.finalize()
        if finalized_shapes is not None:
            if finalized_shapes.status_message is not None:
                pass # TODO: show toolbar message is any specified
            if finalized_shapes.shapes is not None:
                self.canvas.add_shapes(finalized_shapes.shapes, preview=False)
        self.select_tool(selected_tool_idx, True) # discard old tool inst
    # tool preview
    def tool_start_preview(self, preview_shapes : tuple[VectorShape, ...] | None):
        if isinstance(self.canvas, canvas_manager.DynamicDrawingCanvas):
            self.canvas.drag_unlocked = False
        self.canvas.set_selection_enabled(False)
        self.controls_row.set_control_visible("canvas_move", False)
        self.tool_cancel_control_display.label_text.value = "Cancel Placement"
        self.controls_row.set_control_visible("tool_preview_unlock", True)
        self.preview_unlock_control_display.label_text.value = "Unlock Preview"
        if self.selected_tool_preview_shapes is None:
            self.selected_tool_preview_shapes = []
        if preview_shapes is not None:
            self.selected_tool_preview_shapes.extend(preview_shapes)
            self.canvas.add_shapes(preview_shapes, preview=True)
    def tool_update_tooltips(self, selected_tool : DrawingTool):
        if selected_tool.place_tooltip is not None:
            self.tool_click_control_display.label_text.value = selected_tool.place_tooltip
        else:
            self.tool_click_control_display.label_text.value = "Place"
        if selected_tool.uniform_tooltip is not None:
            self.tool_uniform_mode_control_display.label_text.value = selected_tool.uniform_tooltip
            self.controls_row.set_control_visible("tool_uniform_mode", True)
            if self._control_is_pressed:
                self.tool_set_uniform(selected_tool, True)
        else:
            self.controls_row.set_control_visible("tool_uniform_mode", False)
            self.tool_set_uniform(selected_tool, False)
    def tool_set_uniform(self, selected_tool : DrawingTool, uniform : bool):
        if self.preview_uniform != uniform:
            self.preview_uniform = uniform
            self.tool_translate_changed_shapes(selected_tool.set_uniform(uniform))
    def tool_translate_changed_shapes(self, changed_shapes : tuple[VectorShape, ...] | None):
        if changed_shapes is not None:
            for shape in changed_shapes:
                self.canvas.translate_shape(shape)
    def tool_clear_preview(self):
        if self.selected_tool_preview_shapes is not None:
            self.canvas.remove_shapes(self.selected_tool_preview_shapes)
            self.selected_tool_preview_shapes = None
        self.canvas.set_selection_enabled(True)
        self.preview_unlocked = False
        self.preview_uniform = False
        if isinstance(self.canvas, canvas_manager.DynamicDrawingCanvas):
            self.canvas.drag_unlocked = True
        self._last_canvas_coords = None
        self.controls_row.set_control_visible("canvas_move", True)
        self.controls_row.set_control_visible("tool_preview_unlock", False)
        self.controls_row.set_control_visible("tool_uniform_mode", False)
        self.tool_cancel_control_display.label_text.value = "Deselect Tool"
    def tool_preview_unlock_toggle(self):
        selected_tool_idx = self.selected_tool_indexes.get("main")
        if selected_tool_idx is not None and self.selected_tool_preview_shapes is not None:
            selected_tool = self.selected_tools[selected_tool_idx]
            self.preview_unlocked = not self.preview_unlocked
            if isinstance(self.canvas, canvas_manager.DynamicDrawingCanvas):
                self.canvas.drag_unlocked = self.preview_unlocked
            self.controls_row.set_control_visible("canvas_move", self.preview_unlocked)
            self.controls_row.set_control_visible("tool_click", (not self.preview_unlocked))
            self.controls_row.set_control_visible("tool_cancel", (not self.preview_unlocked))
            if not self.preview_unlocked and selected_tool.uniform_tooltip is not None:
                self.controls_row.set_control_visible("tool_uniform_mode", True)
                if not self._control_is_pressed:
                    self.tool_set_uniform(selected_tool, False)
            else:
                self.controls_row.set_control_visible("tool_uniform_mode", False)
            self.preview_unlock_control_display.label_text.value = "Lock Preview" if self.preview_unlocked else "Unlock Preview"
    # input callbacks
    def _mouse_tap(self, event : ft.TapEvent[ft.GestureDetector]):
        selected_tool_idx = self.selected_tool_indexes.get("main")
        if selected_tool_idx is not None and not self.preview_unlocked and not self._ignore_click:
            selected_tool = self.selected_tools[selected_tool_idx]
            canvas_coords = CanvasCoords(
                self.canvas.mouse_to_canvas_pos(event.local_position or ft.Offset())
            )
            self.tool_click(selected_tool, selected_tool_idx, canvas_coords)
        self._ignore_click = False
    def _mouse_hover(self, event : ft.PointerEvent[ft.GestureDetector]):
        selected_tool_idx = self.selected_tool_indexes.get("main")
        if selected_tool_idx is not None and self.selected_tool_preview_shapes is not None and not self.preview_unlocked:
            selected_tool = self.selected_tools[selected_tool_idx]

            new_canvas_pos = self.canvas.mouse_to_canvas_pos(event.local_position)
            new_delta : ft.Offset | None = None
            if self._last_canvas_coords is not None:
                new_delta = ft.Offset(
                    new_canvas_pos.x - self._last_canvas_coords.pos.x,
                    new_canvas_pos.y - self._last_canvas_coords.pos.y
                )
            canvas_coords = CanvasCoords(new_canvas_pos, new_delta)
            self._last_canvas_coords = canvas_coords

            self.tool_translate_changed_shapes(selected_tool.move(canvas_coords))
    def _alt_up(self, *_):
        self._ignore_click = True
        self._mouse_controller.click(pynput.mouse.Button.left) # regain focus, for some reason pressing alt unfocuses everything
        self.tool_preview_unlock_toggle()
    def _ctrl_pressed(self, event : ft.KeyDownEvent | ft.KeyUpEvent):
        self._control_is_pressed = isinstance(event, ft.KeyDownEvent)
        selected_tool_idx = self.selected_tool_indexes.get("main")
        if selected_tool_idx is not None and self.selected_tool_preview_shapes is not None and not self.preview_unlocked:
            selected_tool = self.selected_tools[selected_tool_idx]
            if selected_tool.uniform_tooltip is not None:
                self.tool_set_uniform(selected_tool, self._control_is_pressed)

class FileToolRow(ToolRow[FileTool]):
    editing_file : file_manager.EditingFile
    def __init__(
        self, config_str_path : str, canvas : canvas_manager.StaticDrawingCanvas, controls_row : RibbonControlsRow,
        editing_file : file_manager.EditingFile,
        auto_assign_keybinds : bool = False, auto_keybind_prefix : str = "", auto_keybind_mod_key : str | None = None, 
        stack_close_key : str = "", stack_close_key_prefix : str = "", stack_close_mod_key : str | None = None, **kwargs
    ):
        super().__init__(FileTool,
            config_str_path, canvas, controls_row, auto_assign_keybinds,
            auto_keybind_prefix, auto_keybind_mod_key, stack_close_key,
            stack_close_key_prefix, stack_close_mod_key, **kwargs
        )
        self.editing_file = editing_file
    def on_tool_selected(self, tool_idx: int):
        self.page.run_task(self.selected_tools[tool_idx].run, self.canvas, self.editing_file)

def get_tool_assets_path(tool_file_path_str : str) -> pathlib.Path:
    file_path = pathlib.Path(tool_file_path_str)
    return utils.get_assets_path() / "tool_packs" / file_path.parent.name / file_path.stem
def get_tool_assets_local_path(tool_file_path_str : str) -> str:
    file_path = pathlib.Path(tool_file_path_str)
    return f"tool_packs/{file_path.parent.name}/{file_path.stem}"
def get_tool_icon_src(tool_file_path_str : str) -> str:
    return get_tool_assets_local_path(tool_file_path_str) + "/icon.png"