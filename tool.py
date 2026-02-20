import logging
import time
import re
import tkinter
from time import struct_time

from rich.logging import RichHandler
from typing import Literal, Any

import config
from widgetlib import InputDialog


def print_widget_tree_limited(widget, max_level=None, level=0, is_last=False, 
                             prefix="", show_path=False):
    """打印带层级限制的 tkinter 组件树
    
    Args:
        widget: 当前组件
        max_level: 最大打印层级，None表示无限制
        level: 当前层级
        is_last: 当前组件是否是父组件的最后一个子组件
        prefix: 前缀字符串（用于递归传递）
        show_path: True显示完整路径，False只显示当前节点标识
    """
    if max_level is not None and level > max_level:
        return
    
    # 确定当前行的前缀
    if level == 0:
        current_prefix = ""
        next_prefix = ""
    else:
        current_prefix = prefix + ("└── " if is_last else "├── ")
        next_prefix = prefix + ("    " if is_last else "│   ")
    
    # 获取组件信息
    widget_type = widget.winfo_class()
    
    # 构建显示内容
    display_parts = [widget_type]
    
    # 添加节点标识
    widget_id = str(widget)
    if show_path:
        # 显示完整路径
        display_parts.append(widget_id)
    else:
        # 只显示当前节点标识（最后一个部分）
        node_id = widget_id.split('.')[-1]
        if node_id:  # 确保不是空字符串
            display_parts.append(node_id)
    
    # 获取文本内容（如果有）
    try:
        if hasattr(widget, 'cget'):
            text = widget.cget('text')
            if text:
                display_parts.append(f"[text='{text}']")
    except:
        pass
    
    # 打印当前组件
    print(f"{current_prefix}{' '.join(display_parts)}")
    
    # 如果到达最大层级，不再打印子组件
    if max_level is not None and level >= max_level:
        return
    
    # 递归处理子组件
    children = widget.winfo_children()
    for i, child in enumerate(children):
        is_child_last = (i == len(children) - 1)
        print_widget_tree_limited(child, max_level, level + 1, is_child_last, 
                                 next_prefix, show_path)

pwt = print_widget_tree_limited

def input_toplevel(
    master, title: str = "title", prompt: str = "prompt", default: str = ""
):
    return InputDialog(master, title, prompt, default).result


def get_logger():
    """只配置你自己的记录器，不影响全局"""
    logger = logging.getLogger(__name__)
    logger.setLevel(config.DEBUG_LEVEL)

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


def str2timestamp(
    time_data: str,
    *,
    default_time: float | None = None,
    ) -> tuple[Literal["relative", "absolute"], float] | tuple[None, None]:
    # 转换成时间数组
    _logger.debug(f"input {time_data=}")
    time_format_abs = ["%Y-%m-%d", "%Y.%m.%d", "%m-%d", "%m.%d"]
    time_format_rel = ["%H:%M:%S", "%M:%S"]

    def td2st(time_data, formats) -> struct_time | None:
        for i in formats:
            try:
                return time.strptime(time_data, i)
            except ValueError as e:
                _logger.warning(e)

    time_array = td2st(time_data, time_format_rel)
    time_type: Literal["relative", "absolute"] = "relative"

    if time_array is None:
        time_array = td2st(
            time_data, [
                f"{i} {j}"
                for i in time_format_abs 
                for j in time_format_rel
            ]
        )
        time_type = "absolute"

    if time_array is None:
        return None, None

    if time_type == "relative":
        if default_time is None:
            st: struct_time = time.localtime(time.time())
        else:
            st = time.localtime(default_time)
        time_array = time.struct_time((*st[:3], *time_array[3:]))

    # 转换成时间戳
    timestamp = time.mktime(time_array)

    return (time_type, timestamp)


AppGlobalLogger = get_logger()
_logger = AppGlobalLogger.getChild(__name__)


def test0():
    root = tkinter.Tk()
    # print(str2timestamp("12:10:10"), str2timestamp("2024.12.32 12:10:10"), str2timestamp("2024.12.31 12:10:10"), sep=", ")
    print(input_toplevel(root))

if __name__ == "__main__":
    test0()
