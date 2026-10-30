from tool_manager import DrawingTool, FinalizedShapes, ToolStatusMessageType, get_tool_icon_src, CanvasCoords
from canvas_shapes import VectorLine, VectorShape
from utils import get_line_shift, get_distance_to_line

class Tool(DrawingTool):
    name = "Free Triangle"
    icon_src = get_tool_icon_src(__file__)
    base_line : VectorLine
    base_line_shift : tuple[float, float] = (0, 0)
    tri_lines : tuple[VectorLine, VectorLine] | None = None
    uniform : bool = False
    _last_hover_canvas_coords : CanvasCoords
    def click(self, canvas_coords : CanvasCoords) -> None | tuple[VectorShape, ...]:
        if not self.previewing:
            self.previewing = True
            self.base_line = VectorLine(
                origin_x=canvas_coords.pos.x,
                origin_y=canvas_coords.pos.y,
                length_x=0,
                length_y=0
            )
            self._last_hover_canvas_coords = canvas_coords
            return (self.base_line,)
        elif self.tri_lines is None and (self.base_line.length_x != 0 or self.base_line.length_y != 0):
            lx1 = self.base_line.origin_x
            ly1 = self.base_line.origin_y
            lx2 = self.base_line.origin_x+self.base_line.length_x
            ly2 = self.base_line.origin_y+self.base_line.length_y
            self.base_line_shift = get_line_shift(lx1, ly1, lx2, ly2)
            self.uniform_tooltip = "Isosceles"
            self.tri_lines = (
                VectorLine(lx1, ly1, 0, 0),
                VectorLine(lx2, ly2, 0, 0)
            )
            return self.tri_lines
        self.previewing = False
        return None
    def finalize(self) -> FinalizedShapes:
        if self.tri_lines is None:
            return FinalizedShapes(message="length of base line equal to 0", message_type=ToolStatusMessageType.ERROR)
        return FinalizedShapes([self.base_line, *self.tri_lines])
    def move(self, canvas_coords : CanvasCoords) -> tuple[VectorShape, ...] | None:
        if self.previewing:
            transformed_tuple : tuple[VectorShape, ...]
            if self.tri_lines is None:
                self.base_line.length_x = canvas_coords.pos.x - self.base_line.origin_x
                self.base_line.length_y = canvas_coords.pos.y - self.base_line.origin_y
                transformed_tuple = (self.base_line, )
            else:
                canvas_x = canvas_coords.pos.x
                canvas_y = canvas_coords.pos.y
                if self.uniform:
                    distance = get_distance_to_line(
                        canvas_x, canvas_y,
                        self.base_line.origin_x, self.base_line.origin_y,
                        self.base_line.origin_x+self.base_line.length_x,
                        self.base_line.origin_y+self.base_line.length_y
                    )
                    canvas_x = self.base_line.origin_x + self.base_line.length_x/2 + self.base_line_shift[0]*distance
                    canvas_y = self.base_line.origin_y + self.base_line.length_y/2 + self.base_line_shift[1]*distance
                self.tri_lines[0].length_x = canvas_x - self.base_line.origin_x
                self.tri_lines[0].length_y = canvas_y - self.base_line.origin_y
                self.tri_lines[1].length_x = canvas_x - (self.base_line.origin_x+self.base_line.length_x)
                self.tri_lines[1].length_y = canvas_y - (self.base_line.origin_y+self.base_line.length_y)
                transformed_tuple = self.tri_lines
            self._last_hover_canvas_coords = canvas_coords
            return transformed_tuple
        return None
    def set_uniform(self, uniform: bool) -> tuple[VectorShape, ...] | None:
        self.uniform = uniform
        if self.previewing:
            return self.move(self._last_hover_canvas_coords)
        return None