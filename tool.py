import logging
import time
import re
import tkinter
from time import struct_time

from rich.logging import RichHandler
from typing import Literal, Any

import config
from widgetlib import AskToplevel


def ask_toplevel(
    master, title: str = "title", prompt: str = "prompt", default: str = ""
):
    return AskToplevel(master, title, prompt, default).result


def get_logger():
    """只配置你自己的记录器，不影响全局"""
    logger = logging.getLogger(__name__)
    logger.setLevel(config.LOG_LEVEL)

    logger.handlers.clear()
    logger.addHandler(
        RichHandler(
            rich_tracebacks=True,  # 启用富文本异常追踪
            tracebacks_show_locals=True,  # 显示局部变量
            tracebacks_width=80,  # 设置异常追踪宽度
            tracebacks_max_frames=5,  # 限制最大帧数
            tracebacks_suppress=["logging"],  # 排除 logging 模块的追踪
            # keywords=[]
        )
    )

    # 防止传递给父记录器
    logger.propagate = False

    return logger


# def str2timestamp(
#     time_data: str,
#     *,
#     default_time: float | None = None,
# ) -> tuple[Literal["relative", "absolute"], float] | tuple[None, None]:
#     # 转换成时间数组
#     _logger.debug(f"input {time_data=}")
#     time_format_abs = ["%Y-%m-%d", "%Y.%m.%d", "%m-%d", "%m.%d"]
#     time_format_rel = ["%H:%M:%S", "%M:%S"]

#     def td2st(time_data, formats) -> struct_time | None:
#         for i in formats:
#             try:
#                 return time.strptime(time_data, i)
#             except ValueError as e:
#                 _logger.warning(e)

#     time_array = td2st(time_data, time_format_rel)
#     time_type: Literal["relative", "absolute"] = "relative"

#     if time_array is None:
#         time_array = td2st(
#             time_data, [f"{i} {j}" for i in time_format_abs for j in time_format_rel]
#         )
#         time_type = "absolute"

#     if time_array is None:
#         return None, None

#     if time_type == "relative":
#         if default_time is None:
#             st: struct_time = time.localtime(time.time())
#         else:
#             st = time.localtime(default_time)
#         time_array = time.struct_time((*st[:3], *time_array[3:]))

#     # 转换成时间戳
#     timestamp = time.mktime(time_array)

#     return (time_type, timestamp)


AppGlobalLogger = get_logger()
_logger = AppGlobalLogger.getChild(__name__)


def test0():
    root = tkinter.Tk()
    # print(str2timestamp("12:10:10"), str2timestamp("2024.12.32 12:10:10"), str2timestamp("2024.12.31 12:10:10"), sep=", ")
    print(ask_toplevel(root))


if __name__ == "__main__":
    test0()
