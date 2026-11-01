from flet.canvas import Canvas as BaseCanvas
from elements import (
    MultiGestureDetector, GestureDetectorCallbacks, RibbonValueDisplay, KeyState,
    MultiKeyListener, RibbonControlsRow, ControlDisplay, ControlDisplayIcon
)
from canvas_shapes import VectorShape, VectorMarker, VectorRect
from weakref import WeakSet
from enum import Enum
from typing import TYPE_CHECKING
from shapely import box as GeometryBox
import shapely
import flet as ft
if TYPE_CHECKING:
    from file_manager import EditingFile

class DrawingType(Enum):
    STATIC = 1
    DYNAMIC = 2
    TECHNICAL = 3

class VectorShapeCanvas(BaseCanvas):
    shapes : list[VectorShape]
    render_shapes : list[VectorShape] # shapes that are currently rendered
    placed_shapes : list[VectorShape] # all placed shapes
    selected_shapes : list[VectorShape]
    default_paint : ft.Paint = ft.Paint(
        color=ft.Colors.SECONDARY, stroke_width=2, style=ft.PaintingStyle.STROKE, stroke_cap=ft.StrokeCap.SQUARE
    )
    temporary_paint : ft.Paint = ft.Paint(
        color=ft.Colors.PRIMARY, stroke_width=3, style=ft.PaintingStyle.STROKE, stroke_cap=ft.StrokeCap.SQUARE
    )
    selected_paint : ft.Paint = ft.Paint(
        color=ft.Colors.TERTIARY_FIXED, stroke_width=3, style=ft.PaintingStyle.STROKE, stroke_cap=ft.StrokeCap.SQUARE
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.render_shapes = self.shapes
        self.placed_shapes = []
        self.selected_shapes = []
    def add_shape(self, shape : VectorShape):
        self.placed_shapes.append(shape)
        if shape.real:
            shape.apply_paint(self.default_paint)
        elif shape.temporary:
            shape.apply_paint(self.temporary_paint)
        for child_shape in shape.get_shape_list():
            self.render_shapes.append(child_shape)
    def remove_shape(self, shape : VectorShape):
        if shape in self.placed_shapes:
            self.deselect_shape(shape)
            self.placed_shapes.remove(shape)
            for child_shape in shape.get_shape_list():
                if child_shape in self.render_shapes:
                    self.render_shapes.remove(child_shape)
    def select_shape(self, shape : VectorShape):
        if shape in self.placed_shapes and shape.real and not shape.temporary:
            shape.apply_paint(self.selected_paint)
            self.selected_shapes.append(shape)
    def deselect_shape(self, shape : VectorShape):
        if shape in self.selected_shapes:
            shape.apply_paint(self.default_paint)
            self.selected_shapes.remove(shape)
    def deselect_all(self):
        for _ in range(len(self.selected_shapes)):
            self.deselect_shape(self.selected_shapes[0])
    def clear_shapes(self):
        old_placed_shapes = self.placed_shapes
        self.render_shapes = []
        self.shapes = self.render_shapes
        self.placed_shapes = []
        for shape in old_placed_shapes:
            if not shape.real:
                self.add_shape(shape)
    def get_relevant_shapes(self, area_x : float, area_y : float, area_width : float, area_height : float) -> list[VectorShape]:
        # TODO: regioning implementation
        relevant_shapes : list[VectorShape] = []
        for shape in self.render_shapes:
            if shape.geometry is not None:
                relevant_shapes.append(shape)
        return relevant_shapes
    def get_intersecting_shapes(self, fully : bool, area_x : float, area_y : float, area_width : float, area_height : float) -> list[VectorShape]:
        intersected_shapes : list[VectorShape] = []
        area_box = GeometryBox(
            area_x, area_y, area_x+area_width, area_y+area_height
        )
        shapely.prepare(area_box)
        for shape in self.get_relevant_shapes(area_x, area_y, area_width, area_height):
            intersects = (
                (not fully and shapely.intersects(area_box, shape.geometry)) 
                or shapely.within(shape.geometry, area_box)
            )
            if intersects:
                intersected_shapes.append(shape)
        return intersected_shapes
class StaticDrawingCanvas(ft.Stack):
    """
    Canvas layout:
    - main stack
        - canvas stack
            - background
            - drawing canvas
        - keyboard listener
        - indicators, message fields, ...            
        - gesture detector
    """
    gesture_detector : MultiGestureDetector
    keyboard_listener : MultiKeyListener
    drawing_canvas : VectorShapeCanvas
    canvas_bg : ft.Container
    canvas_stack : ft.Stack
    size_x : float = 0
    size_y : float = 0
    loaded : bool = False
    drawing_type : DrawingType = DrawingType.STATIC
    editing_file : "EditingFile"
    controls_row : RibbonControlsRow
    selection_enabled : bool = True
    selection_box_outline : VectorRect | None = None
    selection_box : VectorRect | None = None
    selection_is_full : bool = False
    selection_is_additive : bool = False # TODO: handle through selection tools
    full_selection_enabled : bool = True
    full_selection_outline_paint : ft.Paint = ft.Paint(
        color=ft.Colors.INVERSE_PRIMARY, stroke_cap=ft.StrokeCap.SQUARE,
        stroke_width=3, style=ft.PaintingStyle.STROKE
    )
    full_selection_paint : ft.Paint = ft.Paint(
        color=ft.Colors.with_opacity(0.2, ft.Colors.INVERSE_PRIMARY),
        style=ft.PaintingStyle.FILL
    )
    partial_selection_enabled : bool = True
    partial_selection_outline_paint : ft.Paint = ft.Paint(
        color=ft.Colors.INVERSE_PRIMARY, stroke_cap=ft.StrokeCap.SQUARE,
        stroke_width=3, style=ft.PaintingStyle.STROKE, stroke_dash_pattern=[25, 25]
    )
    partial_selection_paint : ft.Paint = ft.Paint(
        color=ft.Colors.with_opacity(0.2, ft.Colors.INVERSE_PRIMARY),
        style=ft.PaintingStyle.FILL
    )
    def __init__(self, editing_file : "EditingFile", controls_row : RibbonControlsRow):
        super().__init__(
            expand=True,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            on_size_change=(lambda *args: self._size_changed(*args))
        )
        self.editing_file = editing_file
        self.controls_row = controls_row
        self.gesture_detector = MultiGestureDetector(drag_interval=25, hover_interval=15)
        self.keyboard_listener = MultiKeyListener(autofocus=True)
        self.drawing_canvas = VectorShapeCanvas(expand=True)
        self.canvas_bg = ft.Container(expand=True, bgcolor=ft.Colors.SURFACE)
        self.canvas_stack = ft.Stack(
            expand=True,
            controls=[self.canvas_bg, self.drawing_canvas],
            top=0, bottom=0, left=0, right=0
        )
        self.controls = [self.canvas_stack, self.keyboard_listener, self.gesture_detector]
        # events
        self.gesture_detector.add_callback(GestureDetectorCallbacks.RIGHT_PAN_START, self._right_pan)
        self.gesture_detector.add_callback(GestureDetectorCallbacks.RIGHT_PAN_END, self._right_pan)
        self.gesture_detector.add_callback(GestureDetectorCallbacks.RIGHT_PAN_UPDATE, self._right_pan)
        self.gesture_detector.add_callback(GestureDetectorCallbacks.EXIT, self._right_pan)
        self.keyboard_listener.add_callback("Delete", KeyState.DOWN, self.remove_selected)
        self.keyboard_listener.add_callback("Backspace", KeyState.DOWN, self.remove_selected)
        self.keyboard_listener.add_callback("Shift Left", KeyState.DOWN, self._left_shift)
        self.keyboard_listener.add_callback("Shift Left", KeyState.UP, self._left_shift)
        # control displays
        self.controls_row.add_control("canvas_delete_selection", ControlDisplay(
            "Delete Selection", ["DEL", "BACK"], visible=False
        ))
        self.controls_row.add_control("canvas_selection", ControlDisplay(
            "Selection", [ControlDisplayIcon.MOUSE_RIGHT_DRAG], visible=False
        ))
        self.controls_row.add_control("canvas_full_selection", ControlDisplay(
            "Full Selection", [ControlDisplayIcon.MOUSE_RIGHT_DRAG_TO_RIGHT], visible=False
        ))
        self.controls_row.add_control("canvas_partial_selection", ControlDisplay(
            "Partial Selection", [ControlDisplayIcon.MOUSE_RIGHT_DRAG_TO_LEFT], visible=False
        ))
        self.set_selection_enabled(None, self.full_selection_enabled, self.partial_selection_enabled)
    def _size_changed(self, event : ft.LayoutSizeChangeEvent[ft.Stack]):
        self.size_x = event.width
        self.size_y = event.height
        if not self.loaded:
            self.loaded = True
            self.editing_file.load_pending(self)
    def translate_shape(self, shape : VectorShape):
        shape.translate(0, 0)
    def add_shapes(self, shapes : list[VectorShape] | tuple[VectorShape, ...], preview : bool = False):
        is_modification = False
        for shape in shapes:
            if shape.real or shape.temporary:
                shape.temporary = preview
                shape.real = not preview
            if shape.real and not shape.temporary:
                is_modification = True
            self.translate_shape(shape)
            self.drawing_canvas.add_shape(shape)
        if is_modification:
            self.editing_file.set_modified()
    def remove_shapes(self, shapes : list[VectorShape] | tuple[VectorShape, ...]):
        is_modification = False
        for shape in shapes:
            if shape.real and not shape.temporary:
                is_modification = True
            self.drawing_canvas.remove_shape(shape)
        if is_modification:
            self.editing_file.set_modified()
    def select_shapes(self, shapes : list[VectorShape] | tuple[VectorShape, ...]):
        for shape in shapes:
            self.drawing_canvas.select_shape(shape)
        if len(self.drawing_canvas.selected_shapes) > 0:
            self.controls_row.set_control_visible("canvas_delete_selection", True)
    def deselect_shapes(self, shapes : list[VectorShape] | tuple[VectorShape, ...]):
        for shape in shapes:
            self.drawing_canvas.deselect_shape(shape)
        if len(self.drawing_canvas.selected_shapes) == 0:
            self.controls_row.set_control_visible("canvas_delete_selection", False)
    def deselect_all(self):
        self.drawing_canvas.deselect_all()
        self.controls_row.set_control_visible("canvas_delete_selection", False)
    def select(self, full : bool, area_x : float, area_y : float, area_width : float, area_height : float):
        self.select_shapes(self.drawing_canvas.get_intersecting_shapes(
            full, area_x, area_y, area_width, area_height
        ))
    def remove_selected(self, *_):
        self.remove_shapes(self.drawing_canvas.selected_shapes[:])
        self.controls_row.set_control_visible("canvas_delete_selection", False)
    def mouse_to_canvas_pos(self, mouse_offset : ft.Offset) -> ft.Offset:
        return mouse_offset
    def clear_canvas(self):
        self.drawing_canvas.clear_shapes()
    def set_selection_enabled(self, selection : bool | None = None, full_selection : bool | None = None, partial_selection : bool | None = None):
        if selection is not None:
            self.selection_enabled = selection
        if full_selection is not None:
            self.full_selection_enabled = full_selection
        if partial_selection is not None:
            self.partial_selection_enabled = partial_selection
        double_selection_enabled = self.full_selection_enabled and self.partial_selection_enabled and self.selection_enabled
        any_selection_enabled = (self.full_selection_enabled or self.partial_selection_enabled) and self.selection_enabled
        single_selection_enabled = not double_selection_enabled and any_selection_enabled
        self.controls_row.set_control_visible("canvas_selection", single_selection_enabled)
        self.controls_row.set_control_visible("canvas_full_selection", double_selection_enabled)
        self.controls_row.set_control_visible("canvas_partial_selection", double_selection_enabled)
    def _right_pan(self, event : ft.PointerEvent[ft.GestureDetector]):
        if event.name.endswith("start") and (self.full_selection_enabled or self.partial_selection_enabled) and self.selection_enabled:
            self.selection_is_full = not self.partial_selection_enabled
            canvas_pos = self.mouse_to_canvas_pos(event.local_position)
            selection_box = VectorRect(canvas_pos.x, canvas_pos.y, real=False)
            selection_box.apply_paint(
                self.full_selection_paint if self.selection_is_full else self.partial_selection_paint
            )
            selection_box_outline = VectorRect(canvas_pos.x, canvas_pos.y, real=False)
            selection_box_outline.apply_paint(
                self.full_selection_outline_paint if self.selection_is_full else self.partial_selection_outline_paint
            )
            self.selection_box = selection_box
            self.selection_box_outline = selection_box_outline
            self.add_shapes((selection_box, selection_box_outline))
        elif self.selection_box is not None and self.selection_box_outline is not None:
            if event.name.endswith("end") or event.name == "exit" or not self.selection_enabled:
                if self.selection_box.width == 0 and self.selection_box.height == 0:
                    self.selection_box.origin_x += 2.5
                    self.selection_box.origin_y -= 2.5
                    self.selection_box.width = -5
                    self.selection_box.height = 5
                    self.translate_shape(self.selection_box)
                self.remove_shapes((self.selection_box, self.selection_box_outline))
                if not self.selection_is_additive:
                    self.deselect_all()
                self.select(self.selection_is_full, 
                    self.selection_box.origin_x, self.selection_box.origin_y,
                    self.selection_box.width, self.selection_box.height
                )
                self.selection_box = None
                self.selection_box_outline = None
                self.canvas_stack.update()
            else:
                prev_selection_is_full = self.selection_is_full
                canvas_pos = self.mouse_to_canvas_pos(event.local_position)
                self.selection_box.width = canvas_pos.x - self.selection_box.origin_x
                self.selection_box.height = canvas_pos.y - self.selection_box.origin_y
                self.selection_box_outline.width = self.selection_box.width
                self.selection_box_outline.height = self.selection_box.height
                self.selection_is_full = (self.selection_box.width > 0 or not self.partial_selection_enabled)
                self.translate_shape(self.selection_box)
                self.translate_shape(self.selection_box_outline)
                if prev_selection_is_full != self.selection_is_full:
                    self.selection_box.apply_paint(
                        self.full_selection_paint if self.selection_is_full else self.partial_selection_paint
                    )
                    self.selection_box_outline.apply_paint(
                        self.full_selection_outline_paint if self.selection_is_full else self.partial_selection_outline_paint
                    )
    def _left_shift(self, event : ft.KeyDownEvent | ft.KeyUpEvent):
        self.selection_is_additive = isinstance(event, ft.KeyDownEvent)
class DynamicDrawingCanvas(StaticDrawingCanvas): # base for Sized and Infinite canvases that share some properties but implement them differently
    canvas_x : float = 0
    canvas_y : float = 0
    zoom : float = 1
    pixels_per_meter : float = 1
    info_rows : WeakSet["DynamicCanvasInfoRow"]
    last_mouse_pos : ft.Offset | None = None
    min_drag_distance : float = 6
    drag_distance : float = 0
    drag_unlocked : bool = True
    drawing_type : DrawingType = DrawingType.DYNAMIC
    def __init__(self, editing_file : "EditingFile", controls_row : RibbonControlsRow):
        super().__init__(editing_file, controls_row)
        self.info_rows = WeakSet()
        self.gesture_detector.add_callback(GestureDetectorCallbacks.HOVER, self._update_mouse_pos)
        self.gesture_detector.add_callback(GestureDetectorCallbacks.PAN_UPDATE, self._update_mouse_pos)
        self.gesture_detector.add_callback(GestureDetectorCallbacks.RIGHT_PAN_UPDATE, self._update_mouse_pos)
        self.gesture_detector.add_callback(GestureDetectorCallbacks.ENTER, self._update_mouse_pos)
        self.gesture_detector.add_callback(GestureDetectorCallbacks.EXIT, self._update_mouse_pos)
    def move_canvas(self, x : float, y : float, x_is_delta : bool = True, y_is_delta : bool = True):
        pass
    def _size_changed(self, event : ft.LayoutSizeChangeEvent[ft.Stack]):
        super()._size_changed(event)
        self._update_mouse_pos(None)
    def _update_mouse_pos(self, event : ft.PointerEvent[ft.GestureDetector] | ft.DragUpdateEvent[ft.GestureDetector] | None):
        update_dict : dict[str, str | float] = {"x" : "-", "y" : "-"}
        if event is not None:
            self.last_mouse_pos = None if event.name == "exit" else event.local_position
        if self.last_mouse_pos is not None:
            canvas_pos = self.mouse_to_canvas_pos(self.last_mouse_pos)
            update_dict["x"] = round(canvas_pos.x)
            update_dict["y"] = round(canvas_pos.y)
        for info_row in self.info_rows:
            info_row.value_updated("mouse_pos", update_dict)
class DynamicCanvasInfoRow(ft.Row):
    canvas : DynamicDrawingCanvas
    values : dict[str, RibbonValueDisplay]
    pos_unit_dict : dict[str, float]
    def __init__(self, canvas : DynamicDrawingCanvas):
        super().__init__(
            expand_loose=True,
            spacing=5
        )
        self.canvas = canvas
        self.pos_unit_dict = {
            "px" : 1,
            "km" : self.canvas.pixels_per_meter*1000,
            "m" : self.canvas.pixels_per_meter,
            "dm" : self.canvas.pixels_per_meter/10,
            "cm" : self.canvas.pixels_per_meter/100,
            "mm" : self.canvas.pixels_per_meter/1000,
        }
        self.values = {
            "canvas_zoom" : RibbonValueDisplay("Canvas Zoom", "icons/canvas_zoom.png", ("", 1)),
            "canvas_pos" : RibbonValueDisplay(
                "Canvas Position", "icons/canvas_position.png", ("x", 0), ("y", 0),
                unit_dict=self.pos_unit_dict, base_unit="px", default_unit="mm"
            ),
            "mouse_pos" : RibbonValueDisplay(
                "Mouse Position", "icons/mouse_position.png", ("x", "-"), ("y", "-"),
                unit_dict=self.pos_unit_dict, base_unit="px", default_unit="mm"
            )
        }
        self.controls = list(self.values.values())
        self.canvas.info_rows.add(self)
    def value_updated(self, name : str, updated_values : dict[str, str | float]):
        if name in self.values:
            for field_name, field_value in updated_values.items():
                self.values[name].set_value(field_name, field_value)

class LimitedDrawingCanvas(DynamicDrawingCanvas): # TODO: fixed-size canvas for pixel art and vector drawings
    pass
class InfiniteDrawingCanvas(DynamicDrawingCanvas): # infinitely sized canvas for technical drawings
    outside_area_size : int
    screen_translation_offset : ft.Offset
    mouse_translation_offset : ft.Offset
    shape_translation_offset : ft.Offset
    def __init__(self, editing_file : "EditingFile", controls_row : RibbonControlsRow, outside_area_size : int):
        super().__init__(editing_file, controls_row)
        self.outside_area_size = outside_area_size
        self.gesture_detector.add_callback(GestureDetectorCallbacks.PAN_START, self._gesture_pan_start)
        self.gesture_detector.add_callback(GestureDetectorCallbacks.PAN_UPDATE, self._gesture_pan_update)
        self.gesture_detector.add_callback(GestureDetectorCallbacks.PAN_END, self._gesture_pan_end)
        self.canvas_stack.margin = -self.outside_area_size
        # offsets are set on the first _size_changed event
        self.screen_translation_offset = ft.Offset()
        self.mouse_translation_offset = ft.Offset()
        self.shape_translation_offset = ft.Offset()
    def _size_changed(self, event : ft.LayoutSizeChangeEvent[ft.Stack]):
        self.screen_translation_offset = ft.Offset(event.width/2, event.height/2)
        self._calculate_translation_offsets()
        if self.loaded:
            # division by half because the bg image grows / shrinks in both directions equally
            self.shift_shapes((event.width - self.size_x)/2, (event.height - self.size_y)/2)
        super()._size_changed(event)
    def mouse_to_canvas_pos(self, mouse_offset : ft.Offset):
        return mouse_offset.copy(
            x=mouse_offset.x + self.mouse_translation_offset.x,
            y=mouse_offset.y + self.mouse_translation_offset.y
        )
    def translate_shape(self, shape : VectorShape):
        shape.translate(self.shape_translation_offset.x, self.shape_translation_offset.y)
    def _calculate_translation_offsets(self):
        self.mouse_translation_offset = ft.Offset(
            x=-self.screen_translation_offset.x + self.canvas_x,
            y=-self.screen_translation_offset.y + self.canvas_y
        )
        self.shape_translation_offset = ft.Offset(
            x=self.outside_area_size + self.screen_translation_offset.x - self.canvas_x - getattr(self.canvas_stack, "left", 0),
            y=self.outside_area_size + self.screen_translation_offset.y - self.canvas_y - getattr(self.canvas_stack, "top", 0)
        )
    def _send_tap_signal_from_drag(self, event : ft.DragStartEvent[ft.GestureDetector] | ft.DragEndEvent[ft.GestureDetector]):
        self.gesture_detector.run_callbacks(
            GestureDetectorCallbacks.TAP,
            ft.TapEvent("tap", event.control,
                data=event.data, local_position=event.local_position, global_position=event.global_position
            )
        )
    def _gesture_pan_start(self, event : ft.DragStartEvent[ft.GestureDetector]):
        if not self.drag_unlocked:
            self._send_tap_signal_from_drag(event)
    def _gesture_pan_update(self, event : ft.DragUpdateEvent[ft.GestureDetector]):
        if self.drag_unlocked:
            delta_x : int = getattr(event.local_delta, "x", 0)
            delta_y : int = getattr(event.local_delta, "y", 0)
            self.drag_distance += abs(delta_x) + abs(delta_y)
            if self.drag_distance >= self.min_drag_distance:
                self.move_canvas(delta_x, delta_y)
    def _gesture_pan_end(self, event : ft.DragEndEvent[ft.GestureDetector]):
        if self.drag_unlocked and self.drag_distance < self.min_drag_distance:
            self._send_tap_signal_from_drag(event)
        self.drag_distance = 0
    def move_canvas(self, x : float, y : float, x_is_delta : bool = True, y_is_delta : bool = True):
        self.editing_file.set_modified()
        # x
        x_move = x if x_is_delta else (self.canvas_x - x)
        x_pos = getattr(self.canvas_stack, "left", 0) + x_move
        x_pos_wrapped = x_pos % self.outside_area_size
        self.canvas_stack.left = x_pos_wrapped
        self.canvas_stack.right = -x_pos_wrapped
        x_shift = x_pos - x_pos_wrapped
        self.canvas_x -= x_move
        # y
        y_move = y if y_is_delta else (self.canvas_y - y)
        y_pos = getattr(self.canvas_stack, "top", 0) + y_move
        y_pos_wrapped = y_pos % self.outside_area_size
        self.canvas_stack.top = y_pos_wrapped
        y_shift = y_pos - y_pos_wrapped
        self.canvas_stack.bottom = -y_pos_wrapped
        self.canvas_y -= y_move
        # update
        self._calculate_translation_offsets()

        self.shift_shapes(x_shift, y_shift)
        updated_canvas_pos_dict : dict[str, float | str] = {"x" : round(self.canvas_x), "y" : round(self.canvas_y)}
        for info_row in self.info_rows:
            info_row.value_updated("canvas_pos", updated_canvas_pos_dict)
    def shift_shapes(self, x_shift : float, y_shift : float):
        if x_shift == 0 and y_shift == 0:
            return
        for shape in self.drawing_canvas.shapes:
            shape.shift(x_shift, y_shift)
    def clear_canvas(self):
        super().clear_canvas()
        self.move_canvas(0, 0, False, False)
        self.canvas_stack.update()
        for info_row in self.info_rows:
            info_row.update()

class TechnicalDrawingCanvas(InfiniteDrawingCanvas):
    BG_IMAGE_SIZE : int = 160
    pixels_per_meter = 16000 # at smallest zoom
    origin_marker : VectorMarker | None = None
    drawing_type : DrawingType = DrawingType.TECHNICAL
    def __init__(self, editing_file : "EditingFile", controls_row : RibbonControlsRow):
        super().__init__(
            editing_file, controls_row,
            self.BG_IMAGE_SIZE
        )
        self.canvas_bg.image = ft.DecorationImage(
            "canvas/technical_canvas_bg.png",
            repeat=ft.ImageRepeat.REPEAT,
            anti_alias=True,
            color_filter=ft.ColorFilter(color=ft.Colors.ON_SECONDARY_FIXED_VARIANT, blend_mode=ft.BlendMode.MODULATE)
        )
    def _size_changed(self, event : ft.LayoutSizeChangeEvent[ft.Stack]):
        super()._size_changed(event)
        if self.origin_marker is None:
            origin_marker = VectorMarker(0, 0, 24, real=False)
            origin_marker.apply_paint(ft.Paint(ft.Colors.INVERSE_PRIMARY, stroke_width=4))
            self.origin_marker = origin_marker
            self.add_shapes([origin_marker])
