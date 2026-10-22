import flet as ft
from flet.canvas import Canvas as BaseCanvas
from elements import MultiGestureDetector, GestureDetectorCallbacks, RibbonValueDisplay
from canvas_shapes import VectorShape, VectorMarker
from weakref import WeakSet

class DrawingCanvas(BaseCanvas):
    shapes : list[VectorShape]
    render_shapes : list[VectorShape] # shapes that are currently rendered
    placed_shapes : list[VectorShape] # all placed shapes
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.render_shapes = self.shapes
        self.placed_shapes = []
    def add_shape(self, shape : VectorShape, paint : ft.Paint | None):
        self.placed_shapes.append(shape)
        if paint is not None and shape.real:
            shape.apply_paint(paint)
        for child_shape in shape.get_shape_list():
            self.render_shapes.append(child_shape)
    def remove_shape(self, shape : VectorShape):
        if shape in self.placed_shapes:
            for child_shape in shape.get_shape_list():
                if child_shape in self.render_shapes:
                    self.render_shapes.remove(child_shape)
class StaticDrawingCanvas(ft.Stack):
    # Canvas layout:
    # - main stack
    #    - canvas stack
    #       - background
    #       - drawing canvas
    #       - preview canvas
    #    - gesture detector
    #    - indicators, message fields, ...
    default_paint : ft.Paint = ft.Paint(
        color=ft.Colors.SECONDARY, stroke_width=2, style=ft.PaintingStyle.STROKE, stroke_cap=ft.StrokeCap.SQUARE
    )
    default_preview_paint : ft.Paint = ft.Paint(
        color=ft.Colors.PRIMARY, stroke_width=3, style=ft.PaintingStyle.STROKE, stroke_cap=ft.StrokeCap.SQUARE
    )
    gesture_detector : MultiGestureDetector
    drawing_canvas : DrawingCanvas
    preview_canvas : DrawingCanvas
    canvas_bg : ft.Container
    canvas_stack : ft.Stack
    size_x : float = 0
    size_y : float = 0
    def __init__(self):
        super().__init__(
            expand=True,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            on_size_change=(lambda *args: self._size_changed(*args))
        )
        self.gesture_detector = MultiGestureDetector()
        self.drawing_canvas = DrawingCanvas(expand=True)
        self.preview_canvas = DrawingCanvas(expand=True)
        self.canvas_bg = ft.Container(expand=True, bgcolor=ft.Colors.SURFACE)
        self.canvas_stack = ft.Stack(
            expand=True,
            controls=[self.canvas_bg, self.drawing_canvas, self.preview_canvas],
            top=0, bottom=0, left=0, right=0
        )
        self.controls = [self.canvas_stack, self.gesture_detector]
    def _size_changed(self, event : ft.LayoutSizeChangeEvent[ft.Stack]):
        self.size_x = event.width
        self.size_y = event.height
    def translate_shape(self, shape : VectorShape):
        shape.translate(0, 0)
    def add_shapes(self, shapes : list[VectorShape], preview : bool = False):
        canvas = self.preview_canvas if preview else self.drawing_canvas
        paint = self.default_preview_paint if preview else self.default_paint
        for shape in shapes:
            self.translate_shape(shape)
            canvas.add_shape(shape, paint)
    def remove_shapes(self, shapes : list[VectorShape], preview : bool = False):
        canvas = self.preview_canvas if preview else self.drawing_canvas
        for shape in shapes:
            if shape in canvas.shapes:
                canvas.shapes.remove(shape)
    def mouse_to_canvas_pos(self, mouse_offset : ft.Offset) -> ft.Offset:
        return mouse_offset
class DynamicDrawingCanvas(StaticDrawingCanvas): # base for Sized and Infinite canvases that share some properties but implement them differently
    canvas_x : float = 0
    canvas_y : float = 0
    zoom : float = 1
    pixels_per_meter : float = 1
    info_rows : WeakSet["DynamicCanvasInfoRow"]
    last_mouse_pos : ft.Offset | None = None
    def __init__(self):
        super().__init__()
        self.info_rows = WeakSet()
        self.gesture_detector.add_callback(GestureDetectorCallbacks.HOVER, self._update_mouse_pos)
        self.gesture_detector.add_callback(GestureDetectorCallbacks.PAN_UPDATE, self._update_mouse_pos)
        self.gesture_detector.add_callback(GestureDetectorCallbacks.RIGHT_PAN_UPDATE, self._update_mouse_pos)
        self.gesture_detector.add_callback(GestureDetectorCallbacks.ENTER, self._update_mouse_pos)
        self.gesture_detector.add_callback(GestureDetectorCallbacks.EXIT, self._update_mouse_pos)
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
    def __init__(self, outside_area_size : int):
        super().__init__()
        self.outside_area_size = outside_area_size
        self.gesture_detector.add_callback(GestureDetectorCallbacks.PAN_UPDATE, self._gesture_pan_update)
        self.canvas_stack.margin = -self.outside_area_size
        # offsets are set on the first _size_changed event
        self.screen_translation_offset = ft.Offset()
        self.mouse_translation_offset = ft.Offset()
        self.shape_translation_offset = ft.Offset()
    def _size_changed(self, event : ft.LayoutSizeChangeEvent[ft.Stack]):
        self.screen_translation_offset = ft.Offset(event.width/2, event.height/2)
        self._calculate_translation_offsets()
        if self.size_x != 0 and self.size_y != 0:
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
    def _gesture_pan_update(self, event : ft.DragUpdateEvent[ft.GestureDetector]):
        self.move_canvas(getattr(event.local_delta, "x", 0), getattr(event.local_delta, "y", 0))
    def move_canvas(self, x : float, y : float, x_is_delta : bool = True, y_is_delta : bool = True):
        # x
        x_pos = (getattr(self.canvas_stack, "left", 0) + x) if x_is_delta else x
        x_pos_wrapped = x_pos % self.outside_area_size
        self.canvas_stack.left = x_pos_wrapped
        self.canvas_stack.right = -x_pos_wrapped
        self.canvas_x -= x
        # y
        y_pos = (getattr(self.canvas_stack, "top", 0) + y) if y_is_delta else y
        y_pos_wrapped = y_pos % self.outside_area_size
        self.canvas_stack.top = y_pos_wrapped
        self.canvas_stack.bottom = -y_pos_wrapped
        self.canvas_y -= y
        # update
        self._calculate_translation_offsets()
        self.shift_shapes(x_pos - x_pos_wrapped, y_pos - y_pos_wrapped)
        updated_canvas_pos_dict : dict[str, float | str] = {"x" : round(self.canvas_x), "y" : round(self.canvas_y)}
        for info_row in self.info_rows:
            info_row.value_updated("canvas_pos", updated_canvas_pos_dict)
    def shift_shapes(self, x_shift : float, y_shift : float):
        if x_shift == 0 and y_shift == 0:
            return
        for shape in self.drawing_canvas.shapes:
            shape.shift(x_shift, y_shift)
        for shape in self.preview_canvas.shapes:
            shape.shift(x_shift, y_shift)

class TechnicalDrawingCanvas(InfiniteDrawingCanvas):
    BG_IMAGE_SIZE : int = 160
    pixels_per_meter = 16000 # at smallest zoom
    origin_marker : VectorMarker | None = None
    def __init__(self):
        super().__init__(
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
            origin_marker = VectorMarker(0, 0, real=False)
            origin_marker.apply_paint(ft.Paint(ft.Colors.INVERSE_PRIMARY, stroke_width=2))
            self.origin_marker = origin_marker
            self.add_shapes([origin_marker])
