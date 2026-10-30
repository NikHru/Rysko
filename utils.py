import flet as ft
import os
import sys
import pathlib
import math
from weakref import WeakKeyDictionary
from typing import Any

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

def get_trunc_remainder(x : float, y : float):
    return x - y * math.trunc(x / y)
def get_number(string : str) -> float | None:
    try:
        return float(string)
    except ValueError:
        return None
def get_number_sign(x : int | float) -> int:
    if x == 0:
        return 1
    return int(x // abs(x))

def get_tri_hypotenuse(a : float, b : float) -> float:
    return math.sqrt(a**2 + b**2)
def get_tri_leg(a : float, c : float) -> float:
    return math.sqrt(c**2 - a**2)

def get_distance_to_line(x : float, y : float, lx1 : float, ly1 : float, lx2 : float, ly2 : float) -> float:
    # using https://en.wikipedia.org/wiki/Distance_from_a_point_to_a_line
    a = ly2 - ly1
    b = lx2 - lx1
    c = lx2*ly1 - lx1*ly2
    return (a*x - b*y + c) / math.sqrt(a**2 + b**2)
def get_line_len(lx1 : float, ly1 : float, lx2 : float, ly2 : float) -> float:
    return get_tri_hypotenuse((lx2 - lx1), (ly2 - ly1))
def get_line_shift(lx1 : float, ly1 : float, lx2 : float, ly2 : float) -> tuple[float, float]:
    line_len = get_line_len(lx1, ly1, lx2, ly2)
    shift_x = (lx2 - lx1) / line_len
    shift_y = (ly2 - ly1) / line_len
    return (shift_y, -shift_x)

def read_dict[K, T](dictionary : dict[K, Any], key : K, valid_value_type : tuple[type[T],...] | type[T], default : T) -> T:
    val : T = dictionary.get(key, default)
    if isinstance(val, valid_value_type):
        return val
    return default

class ValueRef[T]:
    _v : T
    references : WeakKeyDictionary[object, str]
    def __init__(self, value : T):
        self._v = value
        self.references = WeakKeyDictionary()
    def reference(self, obj : object, prop : str) -> T:
        self.references[obj] = prop
        return self.read()
    def read(self) -> T:
        return self._v
    def change(self, new_value : T):
        self._v = new_value
        for obj, prop in self.references.items():
            setattr(obj, prop, self._v)
    value = property(read, change)
class NumberValueRef(ValueRef[float | int]):
    references : WeakKeyDictionary[object, tuple[str, float | int]]
    def reference(self, obj: object, prop: str, offset: float | int = 0) -> float | int:
        self.references[obj] = (prop, offset)
        return self._v + offset
    def change(self, new_value: float | int):
        self._v = new_value
        for obj, prop_tuple in self.references.items():
            setattr(obj, prop_tuple[0], self._v + prop_tuple[1])