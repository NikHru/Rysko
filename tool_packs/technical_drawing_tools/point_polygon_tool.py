from tool_manager import DrawingTool, FinalizedShapes, ToolStatusMessageType, get_tool_icon_src, CanvasCoords
from canvas_shapes import VectorLine, VectorShape

class Tool(DrawingTool):
    name = "Point Polygon"
    icon_src = get_tool_icon_src(__file__)
    base_line : VectorLine
    tri_lines : tuple[VectorLine, VectorLine] | None = None
    lines : list[VectorShape]
    point_count : int = 2
    add_point : bool = False
    def click(self, canvas_coords : CanvasCoords) -> None | tuple[VectorShape, ...]:
        if not self.previewing:
            self.previewing = True
            self.base_line = VectorLine(
                origin_x=canvas_coords.pos.x,
                origin_y=canvas_coords.pos.y,
                length_x=0,
                length_y=0
            )
            self.lines = [self.base_line]
            return (self.base_line,)
        elif self.tri_lines is None and (self.base_line.length_x != 0 or self.base_line.length_y != 0):
            self.tri_lines = (
                VectorLine(self.base_line.origin_x, self.base_line.origin_y, 0, 0),
                VectorLine(
                    self.base_line.origin_x+self.base_line.length_x,
                    self.base_line.origin_y+self.base_line.length_y, 0, 0
                )
            )
            self.lines.append(self.tri_lines[0])
            self.lines.append(self.tri_lines[1])
            self.point_count += 1
            return self.tri_lines
        elif self.tri_lines is not None and (self.point_count < 4 or self.add_point):
            self.uniform_tooltip = "Add Point"
            new_line = VectorLine(
                self.tri_lines[0].origin_x+self.tri_lines[0].length_x,
                self.tri_lines[0].origin_y+self.tri_lines[0].length_y,
                0, 0
            )
            self.base_line = VectorLine(
                self.tri_lines[0].origin_x, self.tri_lines[0].origin_y,
                new_line.origin_x - self.tri_lines[0].origin_x,
                new_line.origin_y - self.tri_lines[0].origin_y
            )
            self.tri_lines = (
                self.tri_lines[0],
                new_line
            )
            self.lines.append(new_line)
            self.point_count += 1
            return (new_line,)
        self.previewing = False
        return None
    def finalize(self) -> FinalizedShapes:
        if self.tri_lines is None:
            return FinalizedShapes(message="length of base line equal to 0", message_type=ToolStatusMessageType.ERROR)
        return FinalizedShapes(self.lines)
    def move(self, canvas_coords : CanvasCoords) -> tuple[VectorShape, ...] | None:
        if self.previewing:
            transformed_tuple : tuple[VectorShape, ...]
            if self.tri_lines is None:
                self.base_line.length_x = canvas_coords.pos.x - self.base_line.origin_x
                self.base_line.length_y = canvas_coords.pos.y - self.base_line.origin_y
                transformed_tuple = (self.base_line, )
            else:
                self.tri_lines[0].length_x = canvas_coords.pos.x - self.base_line.origin_x
                self.tri_lines[0].length_y = canvas_coords.pos.y - self.base_line.origin_y
                self.tri_lines[1].length_x = canvas_coords.pos.x - (self.base_line.origin_x+self.base_line.length_x)
                self.tri_lines[1].length_y = canvas_coords.pos.y - (self.base_line.origin_y+self.base_line.length_y)
                transformed_tuple = self.tri_lines
            return transformed_tuple
        return None
    def set_uniform(self, uniform: bool) -> tuple[VectorShape, ...] | None:
        self.add_point = uniform
        return None