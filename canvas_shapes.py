import flet.canvas as fcv
from flet import Paint, LayoutControl

class VectorShape(fcv.Shape):
    origin_x : float
    origin_y : float
    real : bool = True # wheter it gets saved, for example the canvas origin marker isnt "real"
    temporary : bool = False # changes drawing mode
    def __init__(self, origin_x : float, origin_y : float, real : bool = True, temporary : bool = False, **kwargs):
        self.origin_x = origin_x
        self.origin_y = origin_y
        self.real = real
        self.temporary = temporary
        super().__init__(**kwargs)
    def shift(self, shift_x : float, shift_y : float):
        pass
    def translate(self, origin_offset_x : float, origin_offset_y : float):
        pass
    def apply_paint(self, paint : Paint):
        pass
    def get_shape_list(self) -> list["VectorShape"]:
        return [self]
class VectorLine(VectorShape, fcv.Line):
    length_x : float
    length_y : float
    def __init__(self, origin_x : float, origin_y : float, length_x : float, length_y : float, **kwargs):
        kwargs["x1"] = origin_x
        kwargs["y1"] = origin_y
        kwargs["x2"] = origin_x+length_x
        kwargs["y2"] = origin_y+length_y
        super().__init__(origin_x, origin_y, **kwargs)
        self.length_x = length_x
        self.length_y = length_y
    def translate(self, origin_offset_x : float, origin_offset_y : float):
        self.x1 = self.origin_x + origin_offset_x
        self.y1 = self.origin_y + origin_offset_y
        self.x2 = self.origin_x + self.length_x + origin_offset_x
        self.y2 = self.origin_y + self.length_y + origin_offset_y
    def shift(self, shift_x : float, shift_y : float):
        self.x1 += shift_x
        self.x2 += shift_x
        self.y1 += shift_y
        self.y2 += shift_y
    def apply_paint(self, paint : Paint):
        self.paint = paint
class CompositeVectorShape(VectorLine): # Line class itself doenst actually get added to render list ever, only for flet compatibility
    shapes : list[VectorShape]
    def __init__(self, origin_x : float, origin_y : float, shapes : list[VectorShape], **kwargs):
        super().__init__(origin_x, origin_y, 0, 0, **kwargs)
        self.shapes = shapes
    def shift(self, shift_x : float, shift_y : float):
        super().shift(shift_x, shift_y)
        for shape in self.shapes:
            shape.shift(shift_x, shift_y)
    def translate(self, origin_offset_x : float, origin_offset_y : float):
        super().translate(origin_offset_x, origin_offset_y)
        for shape in self.shapes:
            shape.translate(origin_offset_x, origin_offset_y)
    def apply_paint(self, paint : Paint):
        super().apply_paint(paint)
        for shape in self.shapes:
            shape.apply_paint(paint)
    def get_shape_list(self) -> list[VectorShape]:
        return self.shapes
class VectorRect(VectorShape, fcv.Rect):
    def __init__(self, origin_x : float, origin_y : float, **kwargs):
        kwargs["x"] = origin_x
        kwargs["y"] = origin_y
        super().__init__(origin_x, origin_y, **kwargs)
    def translate(self, origin_offset_x : float, origin_offset_y : float):
        self.x = self.origin_x + origin_offset_x
        self.y = self.origin_y + origin_offset_y
    def shift(self, shift_x : float, shift_y : float):
        self.x += shift_x
        self.y += shift_y
    def apply_paint(self, paint : Paint):
        self.paint = paint
class VectorMarker(CompositeVectorShape):
    size : int
    def __init__(self, pos_x : int, pos_y : int, size : int = 16, **kwargs):
        line1 = VectorLine(pos_x, pos_y-size/2, 0, size)
        line2 = VectorLine(pos_x-size/2, pos_y, size, 0)
        super().__init__(pos_x, pos_y, [line1, line2], **kwargs)
        self.size = size