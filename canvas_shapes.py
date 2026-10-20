import flet.canvas as fcv

class VectorShape(fcv.Shape):
    origin_x : float
    origin_y : float
    def __init__(self, origin_x : float, origin_y : float, **kwargs):
        self.origin_x = origin_x
        self.origin_y = origin_y
        super().__init__(**kwargs)
    def shift(self, shift_x : float, shift_y : float):
        pass
    def translate(self, origin_offset_x : float, origin_offset_y : float):
        pass
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