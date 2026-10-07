import os
import pathlib
import importlib.util

def get_assets_path() -> pathlib.Path:
    return pathlib.Path(os.environ.get(
        "FLET_ASSETS_DIR",
        pathlib.Path(__file__).parent / "assets"
    ))

def import_module_by_path(module_path : pathlib.Path):
    module_spec = importlib.util.spec_from_file_location("module", module_path)
    if module_spec is None or module_spec.loader is None:
        raise ValueError("Invalid module path.")
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module

def filename(filepath : pathlib.Path) -> str:
    return filepath.name.split(".")[0]