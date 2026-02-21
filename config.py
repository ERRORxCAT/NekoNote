import logging
from ttkbootstrap.style import ThemeDefinition

DEBUG_LEVEL = logging.DEBUG
JSON_DUMP_INDENT = 2
APP_THEME = ThemeDefinition(
    name="sakura_dusk",
    themetype="dark",
    colors={
        "primary": "#f8a5b2",
        "secondary": "#7c6a8a",
        "success": "#a3d0b2",
        "info": "#93c5e4",
        "warning": "#f5c58c",
        "danger": "#f28b8b",
        "light": "#d6c6e0",
        "dark": "#332a3a",
        "bg": "#3a2e3f",
        "fg": "#f2e6f0",
        "selectbg": "#8d6b94",
        "selectfg": "#ffffff",
        "border": "#52435a",
        "inputfg": "#ecddf0",
        "inputbg": "#4d3f54",
        "active": "#ab7eb3",
    },
)