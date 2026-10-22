import flet as ft
import os
import sys
import pathlib
import math
from weakref import WeakKeyDictionary

def get_assets_path() -> pathlib.Path:
    return pathlib.Path(os.environ.get(
        "FLET_ASSETS_DIR",
        pathlib.Path(__file__).parent / "assets"
    ))

def get_appdata_path(subdirectory : str | None = None) -> pathlib.Path:
    if not getattr(sys, "frozen", False):
        return pathlib.Path(__file__).parent
    if sys.platform == "win32":
        appdata_dir = pathlib.Path(os.environ["LOCALAPPDATA"]) / "Rysko"
    else:
        appdata_dir = pathlib.Path.home() / ".local" / "state" / "Rysko"
    if subdirectory is not None:
        appdata_dir /= subdirectory
    appdata_dir.resolve()
    appdata_dir.mkdir(parents=True, exist_ok=True)
    return appdata_dir

def filename(filepath : pathlib.Path) -> str:
    return filepath.name.split(".")[0]

def icon_src_to_image(src : ft.IconData | str, **image_kwargs) -> ft.Image | ft.IconData:
    if isinstance(src, ft.IconData):
        return src
    return ft.Image(src, **image_kwargs)

def trunc_remainder(x : float, y : float):
    return x - y * math.trunc(x / y)

def get_number(string : str) -> float | None:
    try:
        return float(string)
    except ValueError:
        return None

class ValueRef[T]:
    _v : T
    references : WeakKeyDictionary[object, str] = WeakKeyDictionary()
    def __init__(self, value : T):
        self._v = value
    def reference(self, obj : object, prop : str) -> T:
        self.references[obj] = prop
        return self._v
    def read(self) -> T:
        return self._v
    def change(self, new_value : T):
        self.value = new_value
        for obj, prop in self.references.items():
            setattr(obj, prop, self._v)
    value = property(read, change)