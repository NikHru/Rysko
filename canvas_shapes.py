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
        if getattr(self, "paint", None) is not None:
            setattr(self, "paint", paint)
    def get_shape_list(self) -> list["VectorShape"]:
        return [self]

# BASE SHAPES
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
class VectorCircle(VectorShape, fcv.Circle):
    def __init__(self, origin_x: float, origin_y: float, radius : float, **kwargs):
        kwargs["x"] = origin_x
        kwargs["y"] = origin_y
        super().__init__(origin_x, origin_y, **kwargs)
        self.radius = radius
    def translate(self, origin_offset_x : float, origin_offset_y : float):
        self.x = self.origin_x + origin_offset_x
        self.y = self.origin_y + origin_offset_y
    def shift(self, shift_x : float, shift_y : float):
        self.x += shift_x
        self.y += shift_y
# COMPOSITE SHAPES
class CompositeVectorShape(VectorLine): # Line class itself doenst actually get added to render list ever, only for flet compatibility
    shapes : list[VectorShape]
    _origin_x : float
    _origin_y : float
    def __init__(self, origin_x : float, origin_y : float, shapes : list[VectorShape], local_shapes : bool = False, **kwargs):
        for shape in shapes:
            if local_shapes:
                shape.origin_x += origin_x
                shape.origin_y += origin_y
            setattr(shape, "_origin_offset_x", shape.origin_x - origin_x)
            setattr(shape, "_origin_offset_y", shape.origin_y - origin_y)
        self.shapes = shapes
        super().__init__(origin_x, origin_y, 0, 0, **kwargs)
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
    @property
    def origin_x(self):
        return self._origin_x
    @origin_x.setter
    def origin_x(self, value : float) -> None:
        self._origin_x = value
        for shape in self.shapes:
            shape.origin_x = getattr(shape, "_origin_offset_x", 0) + value
    @property
    def origin_y(self):
        return self._origin_y
    @origin_y.setter
    def origin_y(self, value : float) -> None:
        self._origin_y = value
        for shape in self.shapes:
            shape.origin_y = getattr(shape, "_origin_offset_y", 0) + value
class VectorMarker(CompositeVectorShape):
    size : float
    def __init__(self, origin_x : float, origin_y : float, size : float = 16, **kwargs):
        line1 = VectorLine(origin_x, origin_y-size/2, 0, size)
        line2 = VectorLine(origin_x-size/2, origin_y, size, 0)
        super().__init__(origin_x, origin_y, [line1, line2], **kwargs)
        self.size = size