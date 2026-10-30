import flet as ft
import logging as loglib
import tool_manager
import canvas_manager
from utils import get_appdata_path
from elements import Spacer, ribbon_bar_height, RibbonBar, RibbonControlsRow

logger = loglib.getLogger("main")

def main(page : ft.Page):
    # initialize submodules
    tool_manager.register_tools_from_pack("technical_drawing_tools")

    # creating main ControlsRow (shows availible controls)
    main_controls_row = RibbonControlsRow(expand=True)

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
    main_toolrow = tool_manager.DrawingToolRow(
        "{local}/technical_drawing_tools/toolrow.json",
        canvas, main_controls_row, 
        auto_assign_keybinds=True, expand=True, stack_close_key="`"
    )
    toolbar_ribbon_bar = RibbonBar(
        main_toolrow, padding=1,
        color=ft.Colors.SURFACE_CONTAINER_HIGHEST
    )
    info_ribbon_bar = RibbonBar(
        main_controls_row,
        RibbonBar.DIVIDER,
        canvas_manager.DynamicCanvasInfoRow(canvas)
    )
    toolbar_layer = ft.Column(
        controls=[
            toolbar_ribbon_bar,
            Spacer(expand=True),
            info_ribbon_bar
        ],
        expand=True,
        spacing=0
    )

    # configure page
    page.title = "Rysko (DEMO)"
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

if __name__ == "__main__":
    # configure logger
    loglib.basicConfig(filename=(get_appdata_path("logs") / "rysko.log"), filemode="w", level=loglib.INFO)
    # run
    ft.run(main)