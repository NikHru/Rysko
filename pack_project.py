from PyInstaller.utils.hooks import collect_submodules
import os

name = "Rysko (DEMO)"
version = "0.4.2.0"
desc = "Open technical drawing app"

tool_packs = collect_submodules("tool_packs")
hidden_imports = "--hidden-import " + " --hidden-import ".join(tool_packs)
os.system(
    f"flet pack main.py --name \"{name}\" --product-name \"Rysko\" --product-version \"{version}\" --company-name \"Ryško s.r.o.\" --file-description \"{desc}\" --icon \"assets/icons/Rysko_logo.ico\" --add-data \"assets:assets\" -y {hidden_imports}"
)