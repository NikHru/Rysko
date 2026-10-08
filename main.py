import flet as ft
import logging as loglib
import tool_manager
import canvas_manager

logger = loglib.getLogger("main")

def main(page : ft.Page):
    # initialize submodules
    tool_manager.register_tools_from_pack("technical_drawing_tools")

    # creating canvas
    canvas = canvas_manager.TechnicalDrawingCanvas()

    # creating toolbar
    toolbar = tool_manager.Toolbar(
        "general_toolbars/main_technical_toolbar.json",
        canvas
    )

    # configure page
    page.title = "Rysko"
    page.window.icon = "icons/Rysko_logo.ico"
    page.padding = 0
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(
        color_scheme_seed=ft.Colors.BLUE,
    )
    page.add(ft.Column(
        controls=[toolbar, canvas],
        spacing=0,
        expand=True
    ))

if __name__ == "__main__":
    # configure logger
    loglib.basicConfig(filename="rysko.log", filemode="w", level=loglib.INFO)
    # run
    ft.run(main)