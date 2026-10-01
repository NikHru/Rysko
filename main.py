import flet as ft
import flet.canvas as cv
import math

def main(page : ft.Page):
    stroke_paint = ft.Paint(stroke_width=2, style=ft.PaintingStyle.STROKE, color=ft.Colors.WHITE)
    fill_paint = ft.Paint(style=ft.PaintingStyle.FILL, color=ft.Colors.BLUE)
    canvas = cv.Canvas(
        width=float("inf"),
        expand=True,
        shapes=[]
    )
    def on_click(e : ft.TapEvent):
        canvas.shapes.append(cv.Rect(
            x=e.local_position.x,
            y=e.local_position.y,
            width=100,
            height=100
        ))
    canvas_gesture_detector = ft.GestureDetector(
        mouse_cursor=ft.MouseCursor.CLICK,
        on_tap=on_click
    )
    canvas.content = canvas_gesture_detector

    tool_bar = ft.NavigationBar()
    page.add(
        ft.SafeArea(
            content=canvas
        )
    )

if __name__ == "__main__":
    ft.run(main)