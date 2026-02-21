def print_widget_tree_limited(
        widget, max_level=None, level=0, is_last=False, prefix="", show_path=False
    ):
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
        node_id = widget_id.split(".")[-1]
        if node_id:  # 确保不是空字符串
            display_parts.append(node_id)

    # 获取文本内容（如果有）
    try:
        if hasattr(widget, "cget"):
            text = widget.cget("text")
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
        is_child_last = i == len(children) - 1
        print_widget_tree_limited(
            child, max_level, level + 1, is_child_last, next_prefix, show_path
        )


pwt = print_widget_tree_limited