import flet as ft
import logging as loglib
import tool_manager
import canvas_manager
from utils import get_appdata_path
from elements import Spacer, ribbon_bar_height, RibbonBar

logger = loglib.getLogger("main")

def main(page : ft.Page):
    # initialize submodules
    tool_manager.register_tools_from_pack("technical_drawing_tools")

    # creating canvas layer
    canvas = canvas_manager.TechnicalDrawingCanvas()
    ribbon_bar_spacer = Spacer()
    ribbon_bar_spacer.height = ribbon_bar_height.reference(ribbon_bar_spacer, "height")
    canvas_layer = ft.Column(
        controls=[
            ribbon_bar_spacer,
            canvas,
            ribbon_bar_spacer
        ],
        expand=True,
        spacing=0
    )

    # creating toolbar layer
    toolbar = tool_manager.Toolbar(
        "general_toolbars/main_technical_toolbar.json",
        canvas
    )
    info_ribbon_bar = RibbonBar(
        ft.Text("Unsaved*\t(placeholder text)", color=ft.Colors.ON_SURFACE, expand=True),
        None,
        canvas_manager.DynamicCanvasInfoRow(canvas)
    )
    toolbar_layer = ft.Column(
        controls=[
            toolbar,
            Spacer(expand=True),
            info_ribbon_bar
        ],
        expand=True,
        spacing=0
    )

    # configure page
    page.title = "Rysko"
    page.window.icon = "icons/Rysko_logo.ico"
    page.fonts = {
        "Lexend" : "fonts/Lexend-VariableFont_wght.ttf"
    }
    page.padding = 0
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(
        color_scheme_seed=ft.Colors.BLUE,
        font_family="Lexend"
    )
    page.add(ft.Stack(
        controls=[canvas_layer, toolbar_layer],
        expand=True
    ))
    #page.add(ft.Column(
    #    controls=[toolbar, canvas],
    #    spacing=0,
    #    expand=True
    #))

if __name__ == "__main__":
    # configure logger
    loglib.basicConfig(filename=(get_appdata_path("logs") / "rysko.log"), filemode="w", level=loglib.INFO)
    # run
    ft.run(main)