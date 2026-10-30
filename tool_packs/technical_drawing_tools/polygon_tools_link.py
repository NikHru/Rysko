from tool_manager import ToolrowLinkTool, get_tool_icon_src, get_tool_assets_local_path

class Tool(ToolrowLinkTool):
    name = "Polygon Tools"
    icon_src = get_tool_icon_src(__file__)
    local_path = get_tool_assets_local_path(__file__)