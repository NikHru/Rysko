import flet as ft
from typing import Callable, NoReturn
from enum import Enum
from inspect import iscoroutinefunction
from pynput.mouse import Button as MouseButton
from pynput.mouse import Controller as MouseController

class ToggleIconButton(ft.IconButton):
    norm_color : ft.Colors = ft.Colors.TRANSPARENT
    norm_icon_color : ft.Colors = ft.Colors.ON_SURFACE
    norm_hover_color : ft.Colors = ft.Colors.SECONDARY_CONTAINER
    pressed_color : ft.Colors = ft.Colors.PRIMARY_FIXED_DIM
    pressed_icon_color : ft.Colors = ft.Colors.ON_PRIMARY_FIXED_VARIANT
    pressed_hover_color : ft.Colors = ft.Colors.SECONDARY_FIXED_DIM
    on_click_callback : Callable[[ft.Event[ft.IconButton]], NoReturn] | None = None
    on_hover_callback : Callable[[ft.Event[ft.IconButton]], NoReturn] | None = None
    selected : bool
    def __init__(self,
                 on_click : Callable[[ft.Event[ft.IconButton]], NoReturn] | None = None,
                 on_blur : Callable[[ft.Event[ft.IconButton]], NoReturn] | None = None,
                 icon_scale : float = 1, **kwargs
    ):
        if "icon" in kwargs and isinstance(kwargs["icon"], ft.Image):
            kwargs["icon"].color=self.norm_icon_color
            kwargs["icon"].scale=icon_scale
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
    callbacks : dict[GestureDetectorCallbacks, list[ft.ControlEventHandler | ft.EventHandler]] = {}
    def add_callback(self, callback : GestureDetectorCallbacks, callback_func : ft.ControlEventHandler | ft.EventHandler):
        if getattr(self, f"on_{callback.value}") is None:
            setattr(self, f"on_{callback.value}", lambda *args: self._internal_run_callbacks(callback, *args))
        if callback not in self.callbacks:
            self.callbacks[callback] = []
        self.callbacks[callback].append(callback_func)
    def remove_callback(self, callback : GestureDetectorCallbacks, callback_func : ft.ControlEventHandler | ft.EventHandler):
        if callback in self.callbacks and callback_func in self.callbacks[callback]:
            self.callbacks[callback].remove(callback_func)
    def _internal_run_callbacks(self, callback : GestureDetectorCallbacks, *args):
        if callback in self.callbacks:
            for callback_func in self.callbacks[callback]:
                if iscoroutinefunction(callback_func):
                    self.page.run_task(callback_func, *args)
                else:
                    callback_func(*args)

MOUSE_BUTTON_POS_TO_ORDER = {
    "left" : "primary",
    "right" : "secondary",
    "middle" : "tertiary"
}
class DragDetector(ft.InteractiveViewer):
    bound_gesture_detector : MultiGestureDetector
    mouse_controller : MouseController
    using_mouse_buttons : list[MouseButton] = []
    drag_enabled : bool = True
    primary_drag_enabled : bool = False
    secondary_drag_enabled : bool = False
    tertiary_drag_enabled : bool = False
    dragging : bool = False
    dragging_button : MouseButton | None = None
    def __init__(self, bound_gesture_detector : MultiGestureDetector, using_mouse_buttons : list[MouseButton], **kwargs):
        super().__init__(
            content=ft.Container(expand=True, bgcolor=ft.Colors.TRANSPARENT),
            constrained=True,
            expand=True,
            interaction_update_interval=10,
            visible=False,
            **kwargs
        )
        self.bound_gesture_detector = bound_gesture_detector
        self.mouse_controller = MouseController()
        for button in using_mouse_buttons:
            self.add_mouse_button(button)
        self.on_interaction_end = self._drag_end
        self.on_interaction_start = lambda *args: self.on_drag_start(*args)
        self.on_interaction_update = lambda *args: self.on_drag_update(*args)
    def add_mouse_button(self, button : MouseButton):
        if button not in self.using_mouse_buttons:
            button_order = MOUSE_BUTTON_POS_TO_ORDER[button.name]
            callback_prefix = "TAP" if button == MouseButton.left else f"{button_order.upper()}_TAP"
            setattr(self, f"{button_order}_drag_enabled", True)
            self.bound_gesture_detector.add_callback(GestureDetectorCallbacks[f"{callback_prefix}_DOWN"], self._gesture_tap)
            self.bound_gesture_detector.add_callback(GestureDetectorCallbacks[f"{callback_prefix}_UP"], self._gesture_tap)
            self.bound_gesture_detector.add_callback(GestureDetectorCallbacks[f"{callback_prefix}_CANCEL"], self._gesture_tap_cancel)
    def remove_mouse_button(self, button : MouseButton):
        if button in self.using_mouse_buttons:
            button_order = MOUSE_BUTTON_POS_TO_ORDER[button.name]
            callback_prefix = "TAP" if button == MouseButton.left else f"{button_order.upper()}_TAP"
            setattr(self, f"{button_order}_drag_enabled", False)
            self.bound_gesture_detector.remove_callback(GestureDetectorCallbacks[f"{callback_prefix}_DOWN"], self._gesture_tap)
            self.bound_gesture_detector.remove_callback(GestureDetectorCallbacks[f"{callback_prefix}_UP"], self._gesture_tap)
            self.bound_gesture_detector.remove_callback(GestureDetectorCallbacks[f"{callback_prefix}_CANCEL"], self._gesture_tap_cancel)
    def _gesture_tap(self, event : ft.TapEvent[ft.GestureDetector]):
        self.visible = event.name.endswith("down")
    def _gesture_tap_cancel(self, event : ft.TapEvent[ft.GestureDetector]):
        is_tertiary = event.name.startswith("tertiary")
        is_secondary = event.name.startswith("secondary")
        if not self.dragging and self.drag_enabled and (
                (self.primary_drag_enabled and not (is_secondary or is_tertiary))
                or (is_tertiary and self.tertiary_drag_enabled)
                or (is_secondary and self.secondary_drag_enabled)
        ):
            self.dragging = True
            button = MouseButton.middle if is_tertiary else (MouseButton.right if is_secondary else MouseButton.left)
            self.dragging_button = button
            # trick to get the pointer event to switch from the GestureDetector to the InteractiveViewer
            self.mouse_controller.release(button)
            self.mouse_controller.press(button)
    def _drag_end(self, event : ft.ScaleEndEvent[ft.InteractiveViewer]):
        self.visible = False
        self.dragging = False
        self.on_drag_end(event)
        self.dragging_button = None
    def on_drag_start(self, event : ft.ScaleStartEvent[ft.InteractiveViewer]):
        pass
    def on_drag_update(self, event : ft.ScaleUpdateEvent[ft.InteractiveViewer]):
        pass
    def on_drag_end(self, event : ft.ScaleEndEvent[ft.InteractiveViewer]):
        pass