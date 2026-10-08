from PyInstaller.utils.hooks import collect_submodules
import os

canvas_tools = collect_submodules("tool_packs")
hidden_imports = "--hidden-import " + " --hidden-import ".join(canvas_tools)
os.system(f"flet pack main.py --name \"Rysko\" --icon \"assets/icons/Rysko_logo.ico\" --add-data \"assets:assets\" -y {hidden_imports}")