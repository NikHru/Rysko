import flet as ft
from typing import Callable, NoReturn

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
            kwargs["icon"] = ft.Image(kwargs["icon"].src, color=self.norm_icon_color, anti_alias=True, scale=icon_scale) # create unique image instances
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