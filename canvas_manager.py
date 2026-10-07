import flet as ft
import flet.canvas as fcv

def color_shape_list(shapes : list[fcv.Shape], paint : ft.Paint):
    for shape in shapes:
        if isinstance(shape, (fcv.Line, fcv.Rect)):
            shape.paint = paint
class DrawingCanvas(ft.Container):
    default_paint : ft.Paint = ft.Paint(
        color=ft.Colors.SECONDARY, stroke_width=2, style=ft.PaintingStyle.STROKE, stroke_cap=ft.StrokeCap.SQUARE
    )
    default_preview_paint : ft.Paint = ft.Paint(
        color=ft.Colors.PRIMARY, stroke_width=3, style=ft.PaintingStyle.STROKE, stroke_cap=ft.StrokeCap.SQUARE
    )
    gesture_detector : ft.GestureDetector
    drawing_canvas : fcv.Canvas
    preview_canvas : fcv.Canvas
    content : ft.Stack
    def __init__(self):
        super().__init__(
            bgcolor=ft.Colors.SURFACE,
            expand=True
        )
        self.gesture_detector = ft.GestureDetector()
        self.drawing_canvas = fcv.Canvas(expand=True)
        self.preview_canvas = fcv.Canvas(expand=True)
        self.content = ft.Stack(
            expand=True,
            controls=[self.drawing_canvas, self.preview_canvas, self.gesture_detector]
        )
    def add_shapes(self, shapes : list[fcv.Shape], preview : bool = False):
        canvas = self.preview_canvas if preview else self.drawing_canvas
        color_shape_list(shapes, self.default_preview_paint if preview else self.default_paint)
        canvas.shapes.extend(shapes)
    def remove_shapes(self, shapes : list[fcv.Shape], preview : bool = False):
        canvas = self.preview_canvas if preview else self.drawing_canvas
        for shape in shapes:
            if shape in canvas.shapes:
                canvas.shapes.remove(shape)

class TechnicalDrawingCanvas(DrawingCanvas):
    def __init__(self):
        super().__init__()
        self.image = ft.DecorationImage(
            "canvas/technical_canvas_bg.png",
            repeat=ft.ImageRepeat.REPEAT,
            anti_alias=True,
            color_filter=ft.ColorFilter(color=ft.Colors.ON_SECONDARY_FIXED_VARIANT, blend_mode=ft.BlendMode.MODULATE)
        )