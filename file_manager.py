from canvas_manager import StaticDrawingCanvas, DynamicDrawingCanvas, DrawingType
from canvas_shapes import RYS_NAME_TO_SHAPE, VectorShape
from typing import Callable
from io import TextIOWrapper
import flet as ft
import pathlib
import os
import sys
import utils
import shutil
import logging as loglib
logger = loglib.getLogger("main")

extension_config_changed : bool = False
def WINDOWS_setup_prog_id(prog_id : str, prog_name : str, icon_src : str, launcher_src : str):
    global extension_config_changed
    appdata_icon_path = utils.get_appdata_path("icons") / f"{prog_id}_icon.ico"
    appdata_lanucher_path = utils.get_appdata_path("launchers") / f"{prog_id}_launcher.cmd"
    if not appdata_lanucher_path.exists():
        extension_config_changed = True
        assets_path = utils.get_assets_path()
        shutil.copyfile(assets_path / icon_src, appdata_icon_path)
        shutil.copyfile(assets_path / launcher_src, appdata_lanucher_path)
        import winreg
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\{prog_id}") as key:
            winreg.SetValue(key, None, winreg.REG_SZ, prog_name)
            winreg.SetValue(key, "DefaultIcon", winreg.REG_SZ, str(appdata_icon_path.resolve()))
        winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\{prog_id}\shell").Close()
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\{prog_id}\shell\open") as key:
            winreg.SetValue(key, "command", winreg.REG_SZ, rf'"{str(appdata_lanucher_path.resolve())}" "%1"')
def WINDOWS_setup_extension(ext : str, prog_id : str):
    global extension_config_changed
    import winreg
    ext_is_set = True
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\.{ext}") as key:
            if winreg.QueryValue(key, None) != prog_id:
                ext_is_set = False
    except OSError:
        ext_is_set = False
    if not ext_is_set:
        extension_config_changed = True
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\.{ext}") as key:
            winreg.SetValue(key, None, winreg.REG_SZ, prog_id)
def WINDOWS_setup_finish():
    global extension_config_changed
    if extension_config_changed:
        extension_config_changed = False
        from ctypes import windll
        windll.shell32.SHChangeNotify( # neviem ako to funguje ale zevraj to mam zavolat
            0x08000000,  # SHCNE_ASSOCCHANGED
            0x0000,      # SHCNF_IDLIST
            None,
            None
        )

def setup_extension_launcher(prog_id : str, prog_name : str, icon_src : str, launcher_src : str):
    if getattr(sys, "frozen", False):
        if sys.platform == "win32":
            WINDOWS_setup_prog_id(prog_id, prog_name, icon_src, launcher_src)
        else:
            pass # TODO: linux MIME however that works
def setup_extension(ext : str, prog_id : str):
    if getattr(sys, "frozen", False):
        if sys.platform == "win32":
            WINDOWS_setup_extension(ext, prog_id)
        else:
            pass # TODO: linux MIME however that works
def setup_finish():
    if getattr(sys, "frozen", False):
        if sys.platform == "win32":
            WINDOWS_setup_finish()
        else:
            pass # TODO: linux MIME however that works

def encode_canvas_to_rys(canvas : StaticDrawingCanvas) -> str:
    content = ""
    def add_dict_header(header : str):
        nonlocal content
        content += f"@{header}\n"
    def add_field(name : str, val : str):
        nonlocal content
        content += f"{name}={val}\n"
    def add_list_header(header : str):
        nonlocal content
        content += f"#{header}\n"
    def add_item(val : str):
        nonlocal content
        content += f"{val}\n"
    
    add_dict_header("DRAWING")
    add_field("type", canvas.drawing_type.name)

    add_dict_header("CANVAS")
    if isinstance(canvas, DynamicDrawingCanvas):
        add_field("canvas_x", str(round(canvas.canvas_x)))
        add_field("canvas_y", str(round(canvas.canvas_y)))

    add_list_header("SHAPES")
    for shape in canvas.drawing_canvas.placed_shapes:
        if shape.real and not shape.temporary:
            add_item(shape.encode_to_rys())
    
    return content
def decode_rys_to_canvas(file : TextIOWrapper, canvas : StaticDrawingCanvas):
    def seek_section(section : str, termination_chars : tuple[str, ...], decode_func : Callable[[str], None]):
        starting_stream_pos = file.tell()
        line : str = "x"
        while line != section and line != "":
            line = file.readline().strip()
        if line == "":
            file.seek(starting_stream_pos)
        else:
            pre_line_stream_pos = file.tell()
            line = file.readline().strip()
            while line != "" and line[0] not in termination_chars:
                decode_func(line)
                pre_line_stream_pos = file.tell()
                line = file.readline().strip()
            if line != "":
                file.seek(pre_line_stream_pos)
    loaded_dict : dict[str, str] = {}
    def dict_item_decode(line : str):
        item = line.split("=")
        if len(item) == 2:
            loaded_dict[item[0]] = item[1]
    def load_dict_header(header : str):
        nonlocal loaded_dict
        loaded_dict = {}
        seeking_section = f"@{header}"
        seek_section(seeking_section, ("#", "@"), dict_item_decode)
    loaded_list : list[str] = []
    def list_item_decode(line : str):
        loaded_list.append(line)
    def load_list_header(header : str):
        nonlocal loaded_list
        loaded_list = []
        seeking_section = f"#{header}"
        seek_section(seeking_section, ("#", "@"), list_item_decode)

    loaded_shapes : list[VectorShape] = []
    def load_shape_item(shape_item : str):
        nonlocal loaded_shapes
        shape_data = shape_item.split(":", 1)
        if len(shape_data) == 2:
            shape_class = RYS_NAME_TO_SHAPE.get(shape_data[0], None)
            if shape_class is not None:
                try:
                    shape = shape_class.decode_from_rys(shape_data[1])
                    loaded_shapes.append(shape)
                except Exception as e:
                    logger.error(f"Failed to load shape encoded as \"{shape_item}\"", exc_info=e)
            else:
                logger.error(f"Failed to load shape encoded as \"{shape_item}\", invalid name")

    load_dict_header("DRAWING")
    drawing_type : str = loaded_dict.get("type", "")
    if drawing_type == DrawingType.TECHNICAL.name or drawing_type == DrawingType.DYNAMIC.name:
        if isinstance(canvas, DynamicDrawingCanvas):

            load_dict_header("CANVAS")
            canvas.move_canvas(
                utils.get_number(loaded_dict.get("canvas_x", "0")) or 0,
                utils.get_number(loaded_dict.get("canvas_y", "0")) or 0,
                False, False
            )

            load_list_header("SHAPES")
            for shape_item in loaded_list:
                load_shape_item(shape_item)
            canvas.add_shapes(loaded_shapes)

        else:
            raise ValueError(f"Invalid drawing type \"{drawing_type}\" for canvas {type(canvas)}")
    else:
        raise ValueError(f"Invalid drawing type \"{drawing_type}\"") 

type DrawingCoderPair = tuple[Callable[[StaticDrawingCanvas], str], Callable[[TextIOWrapper, StaticDrawingCanvas], None]]
TECHNICAL_DRAWING_CODERS : dict[str, DrawingCoderPair] = {
    "rys" : (encode_canvas_to_rys, decode_rys_to_canvas)
}
DRAWING_CODERS : dict[str, DrawingCoderPair] = {
    **TECHNICAL_DRAWING_CODERS
}

class EditingFile:
    page : ft.Page
    page_title_prefix : str
    file_path : pathlib.Path
    file_name : str = "unsaved"
    file_ext : str = ""
    file_saved : bool = False
    file_modified : bool = False
    file_picker : ft.FilePicker
    ext_coders : dict[str, DrawingCoderPair]
    saved_canvas : StaticDrawingCanvas | None = None
    pending_load_path : str | pathlib.Path | None = None
    pending_load_canvas : StaticDrawingCanvas | None = None
    def __init__(self, page : ft.Page, page_title_prefix : str, ext_coders : dict[str, DrawingCoderPair]) -> None:
        self.page = page
        self.page_title_prefix = page_title_prefix
        self.ext_coders = ext_coders
        self.file_picker = ft.FilePicker()
        self.file_path = pathlib.Path.home()
        docs_path = self.file_path / "Documents"
        if docs_path.is_dir():
            self.file_path = docs_path
    def process_file_path(self, path : str | pathlib.Path):
        prev_file_path = self.file_path
        if type(path) is str:
            self.file_path = pathlib.Path(path)
        elif isinstance(path, pathlib.Path):
            self.file_path = path
        if not self.file_path.exists() or self.file_path.is_file():
            if not self.file_path.parent.exists():
                self.file_path = prev_file_path
            else:
                self.file_name = self.file_path.stem
                if self.file_path.suffix != "":
                    self.file_ext = self.file_path.suffix[1:]
                self.file_path = self.file_path.parent 
    def set_file(self, path : str | pathlib.Path | None = None, name : str | None = None, ext : str | None = None):
        self.file_saved = False
        if path is not None:
             self.process_file_path(path)
        if name is not None:
            self.file_name = name
        if ext is not None:
            if ext in self.ext_coders:
                self.file_ext = ext
        self.update_window_name()
    def set_modified(self, modified : bool = True):
        prev_modified = self.file_modified
        self.file_modified = modified
        if prev_modified != modified:
            self.update_window_name()
    def get_file_display_name(self) -> str:
        display_name = self.file_name
        if self.file_ext != "":
            display_name += "." + self.file_ext
        if not self.file_saved or self.file_modified:
            display_name += "*"
        return display_name
    def get_file_display_path(self) -> str | None:
        if self.file_saved:
            return str(self.file_path).replace(str(pathlib.Path.home()), "~")
        return None
    def get_file_path(self) -> pathlib.Path:
        return self.file_path / f"{self.file_name}.{self.file_ext}"
    def update_window_name(self):
        title = f"{self.page_title_prefix} - {self.get_file_display_name()}"
        file_display_path = self.get_file_display_path()
        if file_display_path is not None:
            title += f" ({file_display_path})"
        self.page.title = title
    def rename_current(self, new_path : str | pathlib.Path | None = None, new_name : str | None = None, new_ext : str | None = None) -> bool:
        if self.file_saved:
            prev_file_path = self.get_file_path()
            self.set_file(new_path, new_name, new_ext)
            self.file_saved = True
            self.update_window_name()
            new_file_path = self.get_file_path()
            try:
                if new_file_path.is_file():
                    os.remove(new_file_path)
                os.rename(str(prev_file_path), str(new_file_path))
                return True
            except PermissionError as e:
                self.set_file(prev_file_path)
                self.file_saved = True
                self.update_window_name()
                logger.error(f"Failed to rename drawing file at {str(prev_file_path)} to {str(new_file_path)}:", exc_info=e)
        return False
    def save(self, canvas : StaticDrawingCanvas) -> bool:
        if self.file_saved and not self.file_modified and canvas is self.saved_canvas:
            return True
        if self.file_path.is_dir() and self.file_ext in self.ext_coders:
            encoder = self.ext_coders[self.file_ext][0]
            content = encoder(canvas)
            file_path = self.get_file_path()
            try:
                with open(file_path, "w") as f:
                    f.write(content)
                self.file_saved = True
                self.file_modified = False
                self.saved_canvas = canvas
                self.update_window_name()
                return True
            except PermissionError as e:
                logger.error(f"Failed to save drawing file to {str(file_path)}:", exc_info=e)
        return False
    def load(self, file_path_or_src : str | pathlib.Path, canvas : StaticDrawingCanvas) -> bool:
        if not canvas.loaded:
            self.pending_load_path = file_path_or_src
            self.pending_load_canvas = canvas
            return False
        file_path : pathlib.Path
        if type(file_path_or_src) is str:
            file_path = pathlib.Path(file_path_or_src)
        elif isinstance(file_path_or_src, pathlib.Path):
            file_path = file_path_or_src
        ext = file_path.suffix[1:]
        if file_path.is_file() and ext in self.ext_coders:
            decoder = self.ext_coders[ext][1]
            try:
                canvas.clear_canvas()
                with open(file_path, "r") as f:
                    decoder(f, canvas)
                self.file_path = file_path.parent
                self.file_name = file_path.stem
                self.file_ext = ext
                self.file_saved = True
                self.file_modified = False
                self.update_window_name()
                canvas.update()
                return True
            except Exception as e:
                logger.error(f"Failed to load drawing file at {str(file_path_or_src)}:", exc_info=e)
        return False
    def load_pending(self, canvas : StaticDrawingCanvas) -> bool:
        if self.pending_load_canvas == canvas and self.pending_load_path is not None:
            load_success = self.load(self.pending_load_path, canvas)
            self.pending_load_canvas = None
            self.pending_load_path = None
            return load_success
        return False
    def clear(self, canvas : StaticDrawingCanvas, clear_canvas : bool = True):
        if clear_canvas:
            canvas.clear_canvas()
        self.file_name = "unsaved"
        self.file_ext = ""
        self.file_saved = False
        self.file_modified = False
        self.file_path = pathlib.Path.home()
        docs_path = self.file_path / "Documents"
        if docs_path.is_dir():
            self.file_path = docs_path
        self.saved_canvas = None
        self.update_window_name()
