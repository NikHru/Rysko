# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('assets', 'assets')],
    hiddenimports=['tool_packs', 'tool_packs.technical_drawing_tools', 'tool_packs.technical_drawing_tools.circular_tools_link', 'tool_packs.technical_drawing_tools.diameter_circle_tool', 'tool_packs.technical_drawing_tools.free_line_tool', 'tool_packs.technical_drawing_tools.free_rect_tool', 'tool_packs.technical_drawing_tools.free_triangle_tool', 'tool_packs.technical_drawing_tools.horizontal_line_tool', 'tool_packs.technical_drawing_tools.line_rect_tool', 'tool_packs.technical_drawing_tools.line_tools_link', 'tool_packs.technical_drawing_tools.midpoint_rect_tool', 'tool_packs.technical_drawing_tools.point_polygon_tool', 'tool_packs.technical_drawing_tools.polygon_tools_link', 'tool_packs.technical_drawing_tools.radius_circle_tool', 'tool_packs.technical_drawing_tools.vertical_line_tool'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Rysko (DEMO)',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='C:/Users/hrusk/AppData/Local/Temp/5453c9c1-f9bb-4b6a-91b3-2b8137a372db',
    icon=['assets/icons/Rysko_logo.ico'],
)
