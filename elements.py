import flet as ft
from typing import Any, Callable
from enum import Enum
from utils import NumberValueRef

DEFAULT_RIBBON_BAR_HEIGHT : int = 35
ribbon_bar_height = NumberValueRef(DEFAULT_RIBBON_BAR_HEIGHT)

class ToggleIconButton(ft.IconButton):
    norm_color : ft.Colors = ft.Colors.SURFACE_CONTAINER_HIGH
    norm_icon_color : ft.Colors = ft.Colors.ON_SURFACE
    norm_hover_color : ft.Colors = ft.Colors.SECONDARY_CONTAINER
    pressed_color : ft.Colors = ft.Colors.PRIMARY_FIXED_DIM
    pressed_icon_color : ft.Colors = ft.Colors.ON_PRIMARY_FIXED_VARIANT
    pressed_hover_color : ft.Colors = ft.Colors.SECONDARY_FIXED_DIM
    on_click_callback : Callable[[ft.Event[ft.IconButton]], None] | None = None
    on_hover_callback : Callable[[ft.Event[ft.IconButton]], None] | None = None
    selected : bool
    def __init__(self,
                 on_click : Callable[[ft.Event[ft.IconButton]], None] | None = None,
                 on_blur : Callable[[ft.Event[ft.IconButton]], None] | None = None, **kwargs
    ):
        if "icon" in kwargs and isinstance(kwargs["icon"], ft.Image):
            kwargs["icon"].color=self.norm_icon_color
        super().__init__(**kwargs)
        self.selected = False
        self.on_click = self._internal_event_handle
        self.on_hover = self._internal_event_handle
        self.on_click_callback = on_click if on_click is not None else self.on_click_callback
        self.on_hover_callback = on_blur if on_blur is not None else self.on_hover_callback

        self.icon_color = self.norm_icon_color
        self.selected_icon_color = self.pressed_icon_color
        if self.style is not None:
            self.style.icon_color = {ft.ControlState.DEFAULT : self.norm_icon_color, ft.ControlState.SELECTED : self.pressed_icon_color}
        self.set_selected(self.selected)
    def _internal_event_handle(self, event : ft.Event[ft.IconButton]):
        if event.name == "click":
            self.set_selected(not self.selected)
            if self.on_click_callback is not None:
                self.on_click_callback(event)
        elif event.name == "hover":
            if event.data and self.selected:
                self.hover_color = self.pressed_hover_color
            if self.on_hover_callback is not None:
                self.on_hover_callback(event)
    def set_selected(self, selected : bool):
        self.selected = selected
        if self.selected:
            self.bgcolor = self.pressed_color
            self.highlight_color = self.norm_color
            self.hover_color = self.pressed_color
            if isinstance(self.icon, ft.Image):
                self.icon.color = self.pressed_icon_color
        else:
            self.bgcolor = self.norm_color
            self.highlight_color = self.pressed_color
            self.hover_color = self.norm_hover_color
            if isinstance(self.icon, ft.Image):
                self.icon.color = self.norm_icon_color
        if self.parent is not None:
            self.update()
class ScaledText(ft.Text):
    norm_height : int
    norm_size : int
    min_aspect_ratio : float | None
    min_character_count : int | None
    aspect_ratio_increase : float | None = None
    aspect_ratio_decrease_interval : float | None
    prev_character_count : int = 0
    scale_div : float
    def __init__(
            self, norm_height : int, norm_size : int, *text_args, min_aspect_ratio : float | None = None, aspect_ratio_increase : float | None = None,
            min_char_count : int | None = None, aspect_ratio_decrease_interval : float | None = None, scale_div : float = 2.5, **text_kwargs
    ):
        super().__init__(*text_args, **text_kwargs)
        self.scale_div = scale_div
        self.min_aspect_ratio = min_aspect_ratio
        self.min_character_count = min_char_count
        self.aspect_ratio_increase = aspect_ratio_increase
        self.aspect_ratio_decrease_interval = aspect_ratio_decrease_interval
        self.aspect_ratio = self.min_aspect_ratio
        self.norm_height = norm_height
        self.norm_size = norm_size
        self.on_size_change = self._size_changed
    def _size_changed(self, event : ft.LayoutSizeChangeEvent[ft.LayoutControl]):
        self.size = (event.height / self.norm_height) * self.norm_size
        self.offset = ft.Offset(y=(event.height-self.size)/event.height/self.scale_div)
    def before_update(self):
        character_count = len(self.value)
        if character_count != self.prev_character_count:
            self.prev_character_count = character_count
            if self.min_aspect_ratio is not None and self.min_character_count is not None and self.aspect_ratio_increase is not None:
                self.aspect_ratio = self.min_aspect_ratio + self.aspect_ratio_increase*max(0, character_count - self.min_character_count)
class LinkedScaledText(ft.Text):
    linked_text : ft.Text
    def __init__(self, linked_text : ft.Text, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.linked_text = linked_text
    def before_update(self):
        self.size = self.linked_text.size

class UnitMenuButton(ft.PopupMenuButton):
    color : ft.Colors
    unit_dict : dict[str, float]
    default_unit : str | None = None
    base_unit : str
    current_unit : str
    unit_text : ScaledText
    on_update : Callable[[str | None], None] | None = None
    def __init__(
            self, unit_dict : dict[str, float], base_unit : str | None, default_unit : str | None,
            on_update : Callable[[str | None], None] | None = None, norm_text_height : int = 25, norm_text_size : int = 14,
            color : ft.Colors = ft.Colors.SECONDARY
    ):
        self.unit_dict = unit_dict
        default_unit = list(unit_dict.keys())[0] if default_unit is None or default_unit not in unit_dict else default_unit
        self.base_unit = base_unit or default_unit
        self.default_unit = default_unit
        self.current_unit = default_unit
        self.color = color
        self.on_update = on_update
        self.unit_text = ScaledText(
            norm_text_height, norm_text_size, f"[{self.current_unit}]",
            weight=ft.FontWeight.BOLD, color=self.color
        )
        super().__init__(
            expand_loose=True,
            content=self.unit_text,
            tooltip="Change unit",
            items=[
                ft.PopupMenuItem(
                    content=LinkedScaledText(self.unit_text, unit, color=self.color),
                    on_click=(lambda _, current_unit=unit: self._option_clicked(current_unit)),
                    height=0
                ) for unit in unit_dict.keys()
            ],
            popup_animation_style=ft.AnimationStyle(ft.Duration(milliseconds=200), curve=ft.AnimationCurve.EASE_OUT),
        )
    def _option_clicked(self, unit : str):
        self.current_unit = unit
        self.unit_text.value = f"[{unit}]"
        if self.on_update is not None:
            self.on_update(unit)

class RibbonValueDisplay(ft.Row):
    color : ft.Colors
    value_texts : dict[str, ScaledText]
    values_row : ft.Row
    unit_menu : UnitMenuButton | None = None
    decimal_count : int = 3
    def __init__(
            self, tooltip : str, icon_src : str, *values : tuple[str, str | float], color : ft.Colors = ft.Colors.ON_SURFACE_VARIANT,
            unit_dict : dict[str, float] | None = None, base_unit : str | None = None, default_unit : str | None = None, decimal_count : int = 3
    ):
        self.color = color
        self.decimal_count = decimal_count
        self.values_row = ft.Row(
            expand_loose=True,
            spacing=4,
            vertical_alignment=ft.CrossAxisAlignment.STRETCH
        )
        image = ft.Image(icon_src, anti_alias=True, color=self.color)
        super().__init__(
            expand_loose=True,
            spacing=4,
            controls=[image, self.values_row],
            tooltip=tooltip,
            vertical_alignment=ft.CrossAxisAlignment.STRETCH,
            alignment=ft.MainAxisAlignment.CENTER
        )
        self.value_texts = {}
        if unit_dict is not None and len(unit_dict) > 0:
            unit_menu = UnitMenuButton(unit_dict, base_unit, default_unit, on_update=self.calculate_unit)
            self.controls.append(unit_menu)
            self.unit_menu = unit_menu
        for value in values:
            self.set_value(value[0], value[1])
    def set_value(self, label : str, value : str | float):
        if label in self.value_texts:
            self.value_texts[label].value = str(value)
        else:
            self.value_texts[label] = ScaledText(
                25, 14, str(value),
                color=self.color, no_wrap=True, min_aspect_ratio=1.3, aspect_ratio_increase=0.3, min_char_count=4
            )
            if label != "":
                self.values_row.controls.append(ScaledText(
                    25, 14, label,
                    weight=ft.FontWeight.BOLD, color=self.color, expand_loose=True, text_align=ft.TextAlign.CENTER
                ))
            self.values_row.controls.append(self.value_texts[label])
        value_text = self.value_texts[label]
        if type(value) is str:
            value_text.text_align = ft.TextAlign.CENTER
            value_text.data = None
        else:
            value_text.text_align = ft.TextAlign.LEFT
            value_text.data = value
            self.calculate_unit_for_label(label)
    def calculate_unit(self, unit : str | None = None):
        for label in self.value_texts.keys():
            self.calculate_unit_for_label(label, unit)
    def calculate_unit_for_label(self, label : str, unit : str | None = None):
        if label in self.value_texts and self.unit_menu is not None:
            value_text = self.value_texts[label]
            if unit is None:
                unit = self.unit_menu.current_unit
            if type(value_text.data) is float or type(value_text.data) is int:
                val = value_text.data / self.unit_menu.unit_dict[unit]
                if unit == self.unit_menu.base_unit:
                    value_text.value = str(int(val))
                else:
                    str_float = str(round(val*(10**self.decimal_count)))
                    value_text.value = str_float[:-self.decimal_count] + "." + str_float[-self.decimal_count:]
class ControlDisplayIcon(Enum):
    MOUSE_LEFT = "icons/mouse_left_button.png"
    MOUSE_RIGHT = "icons/mouse_right_button.png"
    MOUSE_MIDDLE = "icons/mouse_middle_button.png"
    MOUSE_LEFT_DRAG = "icons/mouse_left_drag.png"
    MOUSE_RIGHT_DRAG = "icons/mouse_right_drag.png"
    MOUSE_RIGHT_DRAG_TO_LEFT = "icons/mouse_right_drag_to_left.png"
    MOUSE_RIGHT_DRAG_TO_RIGHT = "icons/mouse_right_drag_to_right.png"
class ControlDisplay(ft.Row):
    label_text : ScaledText
    color : ft.Colors
    behind_color : ft.Colors
    def __init__(
        self, label : str, key_or_icon_list : list[str | ControlDisplayIcon | tuple[str | ControlDisplayIcon, str]],
        visible : bool = True, color : ft.Colors = ft.Colors.ON_SURFACE_VARIANT, behind_color : ft.Colors = ft.Colors.SURFACE_CONTAINER_HIGH
    ):
        super().__init__(expand_loose=True, vertical_alignment=ft.CrossAxisAlignment.STRETCH, spacing=2, visible=visible)
        self.color = color
        self.behind_color = behind_color
        max_i = len(key_or_icon_list)-1
        for i, key_or_icon in enumerate(key_or_icon_list):
            # decode keybind info
            icon : ControlDisplayIcon | None = None
            key_text : str | None = None
            mod_text : str | None = None
            if type(key_or_icon) is tuple:
                if isinstance(key_or_icon[0], ControlDisplayIcon):
                    icon = key_or_icon[0]
                else:
                    key_text = key_or_icon[0]
                mod_text = key_or_icon[1]
            elif isinstance(key_or_icon, ControlDisplayIcon):
                icon = key_or_icon
            elif type(key_or_icon) is str:
                key_text = key_or_icon
            # create texts and images
            if mod_text is not None:
                self._apend_key_text(mod_text)
                self._append_separator_text("+")
            if icon is not None:
                self.controls.append(ft.Image(
                    icon.value, anti_alias=True, fit=ft.BoxFit.FIT_HEIGHT, 
                    expand_loose=True, color=self.color, tooltip=icon.name.replace("_", " ").capitalize()
                ))
            if key_text is not None:
                self._apend_key_text(key_text)
            if i < max_i:
                self._append_separator_text("/")
        self.label_text = ScaledText(
            25, 14, label, expand_loose=True, 
            color=self.color, italic=True
        )
        self.controls.append(self.label_text)
    def _apend_key_text(self, key : str):
        self.controls.append(ft.Container(
            content=ScaledText(
                20, 14, key, expand=True,
                color=self.behind_color, weight=ft.FontWeight.BOLD, scale_div=10
            ),
            bgcolor=self.color,
            margin=1,
            padding=1.5,
            border_radius=5
        ))
    def _append_separator_text(self, separator : str):
        self.controls.append(ScaledText(
            25, 12, separator, weight=ft.FontWeight.BOLD, color=self.color
        ))
class RibbonControlsRow(ft.Row):
    control_displays : dict[str, ControlDisplay]
    def __init__(self, expand : bool | int = True, spacing : float = 15, margin : float = 1, **kwargs) -> None:
        kwargs["vertical_alignment"] = ft.CrossAxisAlignment.STRETCH
        kwargs["alignment"] = ft.MainAxisAlignment.CENTER
        super().__init__(expand=expand, spacing=spacing, margin=margin, **kwargs)
        self.control_displays = {}
    def add_control(self, id : str, control_display : ControlDisplay):
        self.control_displays[id] = control_display
        self.controls.append(control_display)
    def remove_control(self, id : str):
        control_display = self.control_displays.pop(id, None)
        if control_display is not None:
            self.controls.remove(control_display)
    def set_control_visible(self, id : str, visible : bool):
        if id in self.control_displays:
            self.control_displays[id].visible = visible
        if self.parent is not None:
            self.update()

class RibbonBar(ft.Container):
    DIVIDER = None
    content : ft.Row
    divider_color : ft.Colors
    def __init__(
            self, *fields : ft.Control | None, padding : int = 5,
            color : ft.Colors = ft.Colors.SURFACE_CONTAINER_HIGH, 
            divider_color : ft.Colors = ft.Colors.ON_SECONDARY_FIXED_VARIANT, 
            height_offset : float = 0
    ):
        super().__init__(
            bgcolor=color,
            height=ribbon_bar_height.reference(self, "height", height_offset),
            padding=padding
        )
        self.content = ft.Row(
            spacing=4,
            vertical_alignment=ft.CrossAxisAlignment.STRETCH
        )
        self.divider_color = divider_color
        for field in fields:
            if field is None:
                self.add_separator()
            else:
                self.add_field(field)
    def add_field(self, field : ft.Control):
        self.content.controls.append(field)
    def add_separator(self):
        self.content.controls.append(ft.VerticalDivider(
            color=self.divider_color,
            thickness=2
        ))
class RibbonMenuItemButton(ft.MenuItemButton):
    def __init__(self, *args, **kwargs) -> None:
        kwargs["height"] = 0
        super().__init__(*args, **kwargs)
class RibbonSubmenuButton(ft.SubmenuButton):
    pass
class RibbonMenuBar(RibbonBar):
    menu_bar : ft.MenuBar
    def __init__(
            self, *buttons: ft.SubmenuButton | None,
            color: ft.Colors = ft.Colors.SURFACE_CONTAINER_HIGH
        ):
        self.menu_bar = ft.MenuBar(
            expand=True,
            style=ft.MenuStyle(
                shape=ft.BeveledRectangleBorder(side=ft.BorderSide(color=color))
            )
        )
        super().__init__(*buttons, padding=0, color=color, height_offset=-15)
        self.content.controls.append(self.menu_bar)
    def add_field(self, button: ft.SubmenuButton):
        self.menu_bar.controls.append(button)

class GestureDetectorCallbacks(Enum):
    TAP = "tap"
    TAP_CANCEL = "tap_cancel"
    TAP_DOWN = "tap_down"
    TAP_UP = "tap_up"
    TAP_MOVE = "tap_move"
    DOUBLE_TAP = "double_tap"
    DOUBLE_TAP_CANCEL = "double_tap_cancel"
    DOUBLE_TAP_DOWN = "double_tap_down"
    ENTER = "enter"
    EXIT = "exit"
    FORCE_PRESS_END = "force_press_end"
    FORCE_PRESS_START = "force_press_start"
    FORCE_PRESS_PEAK = "force_press_peak"
    FORCE_PRESS_UPDATE = "force_press_update"
    HORIZONTAL_DRAG_CANCEL = "horizontal_drag_cancel"
    HORIZONTAL_DRAG_END = "horizontal_drag_end"
    HORIZONTAL_DRAG_START = "horizontal_drag_start"
    HORIZONTAL_DRAG_UPDATE = "horizontal_drag_update"
    HORIZONTAL_DRAG_DOWN = "horizontal_drag_down"
    HOVER = "hover"
    LONG_PRESS = "long_press"
    LONG_PRESS_CANCEL = "long_press_cancel"
    LONG_PRESS_DOWN = "long_press_down"
    LONG_PRESS_END = "long_press_end"
    LONG_PRESS_MOVE_UPDATE = "long_press_move_update"
    LONG_PRESS_START = "long_press_start"
    LONG_PRESS_UP = "long_press_up"
    MULTI_LONG_PRESS = "multi_long_press"
    MULTI_TAP = "multi_tap"
    PAN_CANCEL = "pat_cancel"
    PAN_START = "pan_start"
    PAN_END = "pan_end"
    PAN_UPDATE = "pan_update"
    PAN_DOWN = "pan_down"
    RIGHT_PAN_END = "right_pan_end"
    RIGHT_PAN_START = "right_pan_start"
    RIGHT_PAN_UPDATE = "right_pan_update"
    SCALE_END = "scale_end"
    SCALE_START = "scale_start"
    SCALE_UPDATE = "scale_update"
    SCROLL = "scroll"
    SECONDARY_LONG_PRESS = "secondary_long_press"
    SECONDARY_LONG_PRESS_DOWN = "secondary_long_press_down"
    SECONDARY_LONG_PRESS_START = "secondary_long_press_start"
    SECONDARY_LONG_PRESS_END = "secondary_long_press_end"
    SECONDARY_LONG_PRESS_UP = "secondary_long_press_up"
    SECONDARY_LONG_PRESS_CANCEL = "secondary_long_press_cancel"
    SECONDARY_LONG_PRESS_MOVE_UPDATE = "secondary_long_press_move_update"
    SECONDARY_TAP = "secondary_tap"
    SECONDARY_TAP_CANCEL = "secondary_tap_cancel"
    SECONDARY_TAP_DOWN = "secondary_tap_down"
    SECONDARY_TAP_UP = "secondary_tap_up"
    TERTIARY_LONG_PRESS = "tertiary_long_press"
    TERTIARY_LONG_PRESS_DOWN = "tertiary_long_press_down"
    TERTIARY_LONG_PRESS_START = "tertiary_long_press_start"
    TERTIARY_LONG_PRESS_END = "tertiary_long_press_end"
    TERTIARY_LONG_PRESS_UP = "tertiary_long_press_up"
    TERTIARY_LONG_PRESS_CANCEL = "tertiary_long_press_cancel"
    TERTIARY_LONG_PRESS_MOVE_UPDATE = "tertiary_long_press_update"
    TERTIARY_TAP = "tertiary_tap"
    TERTIARY_TAP_CANCEL = "tertiary_tap_cancel"
    TERTIARY_TAP_DOWN = "tertiary_tap_down"
    TERTIARY_TAP_UP = "tertiary_tap_up"
    VERTICAL_DRAG_CANCEL = "vertical_drag_cancel"
    VERTICAL_DRAG_END = "vertical_drag_end"
    VERTICAL_DRAG_START = "vertical_drag_start"
    VERTICAL_DRAG_UPDATE = "vertical_drag_update"
    VERTICAL_DRAG_DOWN = "vertical_drag_down"
class MultiGestureDetector(ft.GestureDetector):
    callbacks : dict[GestureDetectorCallbacks, list[ft.ControlEventHandler | ft.EventHandler]]
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.callbacks = {}
    def add_callback(self, callback : GestureDetectorCallbacks, callback_func : ft.ControlEventHandler | ft.EventHandler):
        if getattr(self, f"on_{callback.value}") is None:
            setattr(self, f"on_{callback.value}", lambda *args: self.run_callbacks(callback, *args))
        if callback not in self.callbacks:
            self.callbacks[callback] = []
        self.callbacks[callback].append(callback_func)
    def remove_callback(self, callback : GestureDetectorCallbacks, callback_func : ft.ControlEventHandler | ft.EventHandler):
        if callback in self.callbacks and callback_func in self.callbacks[callback]:
            self.callbacks[callback].remove(callback_func)
    def run_callbacks(self, callback : GestureDetectorCallbacks, *args):
        if callback in self.callbacks:
            for callback_func in self.callbacks[callback]:
                callback_func(*args)

class KeyState(Enum):
    DOWN = 1
    HOLD = 2
    UP = 3
class MultiKeyListener(ft.KeyboardListener):
    callbacks : dict[tuple[str, KeyState] | KeyState, list[ft.EventHandler]]
    def __init__(self, autofocus : bool, **kwargs) -> None:
        super().__init__(
            ft.Row(), autofocus, **kwargs
        )
        self.on_key_down = lambda e: self.run_callbacks(e.key, KeyState.DOWN, e)
        self.on_key_repeat = lambda e: self.run_callbacks(e.key, KeyState.HOLD, e)
        self.on_key_up = lambda e: self.run_callbacks(e.key, KeyState.UP, e)
        self.callbacks = {}
    def add_callback(self, key : str | None, key_state : KeyState, callback_func : ft.ControlEventHandler | ft.EventHandler):
        callback = key_state
        if key is not None:
            callback = (key, key_state)
        if callback not in self.callbacks:
            self.callbacks[callback] = []
        self.callbacks[callback].append(callback_func)
    def remove_callback(self, key : str | None, key_state : KeyState, callback_func : ft.ControlEventHandler | ft.EventHandler):
        callback = key_state
        if key is not None:
            callback = (key, key_state)
        if callback in self.callbacks and callback_func in self.callbacks[callback]:
            self.callbacks[callback].remove(callback_func)
    def run_callbacks(self, key : str, key_state : KeyState, *args):
        #print(key, key_state)
        callback = (key, key_state)
        if callback in self.callbacks:
            for callback_func in self.callbacks[callback]:
                callback_func(*args)
        if key_state in self.callbacks:
            for callback_func in self.callbacks[key_state]:
                callback_func(*args)

class Spacer(ft.Container):
    def __init__(self, **container_kwargs):
        super().__init__(**container_kwargs)
        self.ignore_interactions = True
        self.bgcolor = ft.Colors.TRANSPARENT