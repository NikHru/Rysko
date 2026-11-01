import flet as ft
import logging as loglib
import tool_manager
import canvas_manager
import file_manager
import sys
from utils import get_appdata_path, update_exe_path
from elements import Spacer, ribbon_bar_height, RibbonBar, RibbonControlsRow

logger = loglib.getLogger("main")

def main(page : ft.Page):
    # configure file extensions
    update_exe_path()
    file_manager.setup_extension_launcher(
        "RyskoDrawing",
        "Rysko Drawing File",
        "icons/drawing_file_icon.ico",
        "launchers/drawing_launcher_windows.cmd"
    )
    file_manager.setup_extension("rys", "RyskoDrawing")
    file_manager.setup_finish()

    # initialize submodules
    tool_manager.register_tools_from_pack("file_tools")
    tool_manager.register_tools_from_pack("technical_drawing_tools")
    
    # creating editing file manager
    editing_file = file_manager.EditingFile(
        page, "Rysko (DEMO)",
        file_manager.TECHNICAL_DRAWING_CODERS
    )
    # creating main ControlsRow (shows availible controls)
    main_controls_row = RibbonControlsRow(expand=True)

    # creating canvas layer
    canvas = canvas_manager.TechnicalDrawingCanvas(editing_file, main_controls_row)
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
    drawing_toolrow = tool_manager.DrawingToolRow(
        "{local}/technical_drawing_tools/toolrow.json",
        canvas, main_controls_row, 
        auto_assign_keybinds=True, stack_close_key="`", expand=2
    )
    file_toolrow = tool_manager.FileToolRow(
        "{local}/file_tools/toolrow.json",
        canvas, main_controls_row, editing_file, expand=1
    )
    toolbar_ribbon_bar = RibbonBar(
        Spacer(width=3),
        file_toolrow,
        RibbonBar.DIVIDER,
        drawing_toolrow,
        color=ft.Colors.SURFACE_CONTAINER_HIGHEST,
        divider_color=ft.Colors.SURFACE_CONTAINER_HIGH
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
    editing_file.update_window_name()
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

    # load provided file if any
    if len(sys.argv) > 1:
        editing_file.load(sys.argv[1], canvas)

if __name__ == "__main__":
    # configure logger
    loglib.basicConfig(filename=(get_appdata_path("logs", True) / "rysko.log"), filemode="w", level=loglib.INFO)
    # run
    ft.run(main)