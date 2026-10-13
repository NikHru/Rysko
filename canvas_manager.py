import flet as ft
import flet.canvas as fcv
from elements import MultiGestureDetector, GestureDetectorCallbacks, DragDetector, MouseButton

def color_shape_list(shapes : list[fcv.Shape], paint : ft.Paint):
    for shape in shapes:
        if isinstance(shape, (fcv.Line, fcv.Rect)):
            shape.paint = paint
class StaticDrawingCanvas(ft.Stack):
    # Canvas layout:
    # - main stack
    #    - canvas stack
    #       - background
    #       - drawing canvas
    #       - preview canvas
    #       - gesture detector
    #    - indicators, message fields, dynamic canvas movement controls, ...
    default_paint : ft.Paint = ft.Paint(
        color=ft.Colors.SECONDARY, stroke_width=2, style=ft.PaintingStyle.STROKE, stroke_cap=ft.StrokeCap.SQUARE
    )
    default_preview_paint : ft.Paint = ft.Paint(
        color=ft.Colors.PRIMARY, stroke_width=3, style=ft.PaintingStyle.STROKE, stroke_cap=ft.StrokeCap.SQUARE
    )
    gesture_detector : MultiGestureDetector
    drawing_canvas : fcv.Canvas
    preview_canvas : fcv.Canvas
    canvas_bg : ft.Container
    canvas_stack : ft.Stack
    def __init__(self):
        super().__init__(expand=True)
        self.gesture_detector = MultiGestureDetector()
        self.drawing_canvas = fcv.Canvas(expand=True)
        self.preview_canvas = fcv.Canvas(expand=True)
        self.canvas_bg = ft.Container(expand=True, bgcolor=ft.Colors.SURFACE)
        self.canvas_stack = ft.Stack(
            expand=True,
            controls=[self.canvas_bg, self.drawing_canvas, self.preview_canvas, self.gesture_detector]
        )
        self.controls = [self.canvas_stack]
    def add_shapes(self, shapes : list[fcv.Shape], preview : bool = False):
        canvas = self.preview_canvas if preview else self.drawing_canvas
        color_shape_list(shapes, self.default_preview_paint if preview else self.default_paint)
        canvas.shapes.extend(shapes)
    def remove_shapes(self, shapes : list[fcv.Shape], preview : bool = False):
        canvas = self.preview_canvas if preview else self.drawing_canvas
        for shape in shapes:
            if shape in canvas.shapes:
                canvas.shapes.remove(shape)

class DynamicDrawingCanvas(StaticDrawingCanvas): # TODO: fixed-size canvas for pixel art and vector drawing
    drag_detector : DragDetector

class InfiniteDrawingCanvas(StaticDrawingCanvas): # infinitely sized canvas for technical drawings
    drag_detector : DragDetector
    def __init__(self):
        super().__init__()
        self.drag_detector = DragDetector(self.gesture_detector, [MouseButton.left, MouseButton.middle])
        self.drag_detector.on_drag_start = lambda *_: print("start", self.drag_detector.dragging_button)
        self.drag_detector.on_drag_end = lambda *_: print("end", self.drag_detector.dragging_button)
        self.controls.append(self.drag_detector)

class TechnicalDrawingCanvas(InfiniteDrawingCanvas):
    def __init__(self):
        super().__init__()
        self.canvas_bg.image = ft.DecorationImage(
            "canvas/technical_canvas_bg_quad.png",
            repeat=ft.ImageRepeat.REPEAT,
            anti_alias=True,
            color_filter=ft.ColorFilter(color=ft.Colors.ON_SECONDARY_FIXED_VARIANT, blend_mode=ft.BlendMode.MODULATE)
        )

