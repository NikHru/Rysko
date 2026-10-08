import flet as ft
import os
import pathlib

def get_assets_path() -> pathlib.Path:
    return pathlib.Path(os.environ.get(
        "FLET_ASSETS_DIR",
        pathlib.Path(__file__).parent / "assets"
    ))

def filename(filepath : pathlib.Path) -> str:
    return filepath.name.split(".")[0]

def icon_src_to_image(src : ft.IconData | str, **image_kwargs) -> ft.Image | ft.IconData:
    if isinstance(src, ft.IconData):
        return src
    return ft.Image(src, **image_kwargs)