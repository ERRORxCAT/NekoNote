from __future__ import annotations

import os
import time
import json
from datetime import datetime, timedelta

import tkinter
from tkinter import Misc, Event
from ttkbootstrap import *
from ttkbootstrap.constants import *
from tkinter.messagebox import showinfo, showerror

from functools import partial, singledispatchmethod
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict, InitVar, replace
from collections.abc import Sequence
from typing import (
    Any,
    Callable,
    Literal,
    NamedTuple,
    TextIO,
    cast,
    overload,
    override,
    Self,
    TypeAlias,
    TypeVar,
    TYPE_CHECKING,
)

# from widgetlib import InputDialog
import config
from tool import AppGlobalLogger, ask_toplevel

_logger = AppGlobalLogger.getChild(__name__)

RingTimeType = Literal["start", "end", "point"] | str
if TYPE_CHECKING:
    T_NoteLike = TypeVar("T_NoteLike", bound=NoteLike)


@dataclass
class RingTime:
    type: RingTimeType = "point"
    tip: str = ""
    datetime: datetime = field(default_factory=lambda: datetime(1, 1, 1))

    @classmethod
    def build(cls, data: list[str | int]):
        ring_time = cls()
        ring_time.type = str(data[0])
        ring_time.tip = str(data[1])
        ring_time.datetime = datetime(
            *map(int, data[2:])
        )  # pyright: ignore[reportArgumentType]
        return ring_time

    def aslist(self):
        return [
            self.type,
            self.tip,
            self.datetime.year,
            self.datetime.month,
            self.datetime.day,
            self.datetime.hour,
            self.datetime.minute,
            self.datetime.second,
        ]


@dataclass
class NoteData:
    type_: InitVar[type[NoteLike] | None] = None
    type: str = ""
    time: list[RingTime] | None = None
    title: str = ""
    note: str = ""
    ringable: bool = False

    def __post_init__(self, type_: type[NoteLike] | None):
        if type_:
            self.type = type_.__name__

    def dump(self):
        data = asdict(self)
        _logger.debug(f"dump asdict: {data}")

        if self.time:
            data["time"] = [t.aslist() for t in self.time]
            _logger.debug(f"conv {data['time']=}")

        return data


class TimeInput(Frame):
    def __init__(self, master: Misc, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.pack(fill="x", expand=True, pady=2)

        self._data = RingTime()

        self.time_type_option = Combobox(
            self, width=6, height=3, values=["start", "end", "point"]
        )
        self.time_type_option.set("point")
        self.time_type_option.pack(side="left", padx=2)

        self.time_inp_var = [StringVar() for i in range(6)]

        time_entry_config = [
            (4, "/"),
            (2, "/"),
            (2, "  "),
            (2, ":"),
            (2, ":"),
            (2, ""),
        ]

        self.time_entry: list[Entry] = []

        for i in range(len(time_entry_config)):
            self.time_entry.append(
                Entry(
                    self,
                    width=time_entry_config[i][0],
                    textvariable=self.time_inp_var[i],
                    justify="center",
                )
            )
            self.time_entry[-1].config(
                validate="key",
                validatecommand=(
                    self.register(partial(self._input_validate, i)),
                    "%d",
                    "%P",
                    "%S",
                ),
            )
            self.time_entry[-1].pack(side="left")
            # time_entry[-1].bind("<KeyRelease>", )

            if time_entry_config[i][1]:
                Label(self, text=time_entry_config[i][1]).pack(side="left")

        # time_entry[-1].bind("<Tab>", lambda e: "break")
        self.edit_button = Button(self, text="X", bootstyle=(DANGER, OUTLINE))
        self.edit_button.pack(side="right", padx=2)
        self.tip_input = Entry(self, width=16)
        self.tip_input.pack(side="right", padx=2)

    def _input_validate(
        self, index: int, operation: str, new_content: str, this_input: str
    ) -> bool:
        if not this_input.isdigit():
            return False

        operation: int = int(operation)
        if operation != 0:
            max_length = self.time_entry[index]["width"]
            if len(new_content) > max_length:
                # self.time_entry[index].delete(0, END)
                # self.time_entry[index].insert(0, new_content[-max_length:])
                if index < len(self.time_entry) - 1:
                    self.time_entry[index + 1].delete(0, END)
                    self.time_entry[index + 1].insert(0, this_input)
                    self.time_entry[index + 1].focus_set()
                else:
                    self.time_entry[0].delete(0, END)
                    self.time_entry[0].insert(0, this_input)
                    self.time_entry[0].focus_set()
                return False

        return True

    def bind_edit_button(self, func: Callable[[], Any]):
        self.edit_button.config(command=func)

    def get(self) -> RingTime:
        data: list[str | int] = []
        data.append(self.time_type_option.get())
        data.append(self.tip_input.get())
        data.extend([int(i.get()) for i in self.time_entry])
        return RingTime.build(data)

    def set(self, data: Sequence[str | int] | RingTime) -> None:
        if isinstance(data, RingTime):
            data = data.aslist()
        self.time_type_option.set(data[0])
        self.tip_input.delete(0, END)
        self.tip_input.insert(0, str(data[1]))
        data = data[2:]
        for i in range(len(self.time_entry)):
            self.time_entry[i].delete(0, END)
            self.time_entry[i].insert(0, str(data[i]))

    def set_now(self):
        data = RingTime(self.time_type_option.get(), "", datetime.now())
        self.set(data)

    # def hide(self):
    #     self.pack_forget()

    # def show(self):
    #     self.pack(fill="x", expand=True)


class TimeSettingList(Frame):
    def __init__(self, master: Misc, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.pack(fill="x", expand=True)

        self.time_input_widgets: list[TimeInput] = []

        self.time_input_frame = Frame(self)
        self.time_input_frame.pack(fill="x", expand=True)
        self.menu = Frame(self)
        self.menu.pack(fill="x", expand=True)

        Button(self.menu, text="ADD", command=self.add_time_input, bootstyle = (OUTLINE, INFO)).pack(
            side="left", fill="x", expand=True, pady=2
        )

    def add_time_input(self, value=None):
        time_input = TimeInput(self.time_input_frame)
        if value is not None:
            time_input.set(value)
        else:
            time_input.set_now()
        time_input.bind_edit_button(self.build_remove_func(time_input))
        self.time_input_widgets.append(time_input)

    def build_remove_func(self, widget: TimeInput):
        def remove():
            self.time_input_widgets.remove(widget)
            widget.destroy()

        return remove

    def get(self):
        return [i.get() for i in self.time_input_widgets]

    def set(self, value):
        _logger.debug(f"set TimeSettingList {value=}")
        for i in range(len(value)):
            if i < len(self.time_input_widgets):
                self.time_input_widgets[i].set(value[i])
            else:
                self.add_time_input(value[i])


class NoteLike(Frame, ABC):
    def load(self, name: str):
        return self._build(*self._load_data(self.save_file_name_(name)))

    def _build(
        self, data: NoteData | dict[str, Any], child: list[dict[str, Any]] | None
    ):
        if type(data) is NoteData:
            self.data = data
        elif type(data) is dict:
            self.data = NoteData(**data)
        return self

    def _load_data(
        self, path: str
    ) -> tuple[dict[str, Any], list[dict[str, Any]] | None]:
        with open(path, encoding="utf-8") as f:
            data: dict[str, Any] = json.load(f)

        return self._normal_data(data)

    def _normal_data(
        self, data: dict[str, Any]
    ) -> tuple[dict[str, Any], list[dict[str, Any]] | None]:
        data = dict(data)
        if data["time"]:
            data["time"] = [RingTime.build(t) for t in data["time"]]
        items = None
        if "_items" in data.keys():
            items = data["_items"]
            del data["_items"]

        return data, items

    def dump(self):
        data = self.data.dump()
        return data

    def save(self):
        data = self.dump()
        try:
            with open(
                self.save_file_name_(self.data.title), "w", encoding="utf-8"
            ) as f:
                json.dump(data, f, indent=config.JSON_DUMP_INDENT)
        except Exception:
            _logger.exception(f"Save {self.save_file_name_(self.data.title)} error:")

    def config_data(self, **kwargs):
        self.data = replace(self.data, **kwargs)
        _logger.debug(f"config_data {self.data}")

    def save_file_name(self, name: str | None = None):
        if name is None:
            name = self.data.title
        return self.save_file_name_(name)

    @classmethod
    def save_file_name_(cls, name: str):
        return f"{name}.{cls.__name__}.json"

    @property
    @abstractmethod
    def data(self) -> NoteData: ...

    @data.setter
    @abstractmethod
    def data(self, value: NoteData): ...


class NoteHolder(NoteLike, ABC):
    def add(self, item_type: type[NoteLike], /, *args, **kwarg):
        item = item_type(master=self, *args, **kwarg)
        # item.bg_color(len(self.items))
        self.items.append(item)
        return item

        # def bg_color(self, index:int):
        #     if index % 2 == 1:
        #         self.frame_color_tree_set(self)

        # def frame_color_tree_set(self, widget):
        #     widget.config(bootstyle=INFO)
        #     for i in widget.children.values():
        #         if type(i) is Frame or type(i) is Label:
        #             self.frame_color_tree_set(i)

    @override
    def _build(
        self, data: NoteData | dict[str, Any], child: list[dict[str, Any]] | None
    ):
        super()._build(data, child)
        if child is not None:
            for i in child:
                widget = NoteLikeStrMapping[i["type"]]
                item = self.add(widget)
                item._build(*self._normal_data(i))
        return self

    @override
    def dump(self):
        data = super().dump()
        if self.items:
            data["_items"] = []
            for item in self.items:
                data["_items"].append(item.dump())
        return data

    @property
    @abstractmethod
    def items(self) -> list[NoteLike]: ...

    @items.setter
    @abstractmethod
    def items(self, value: list[NoteLike]): ...


class Note(NoteLike):
    def __init__(
        self, master: Misc, holder: Workspace | None = None, *args, **kwargs
    ) -> None:  # holder:Workspace|NoteGroup|None NoteGroup实现后应该添加上
        super().__init__(master, *args, **kwargs)
        self.pack(side="top", fill="x", expand=True, padx=6, pady=6)

        if holder is None:
            self.holder = holder
        else:
            self.holder = holder

        self._data: NoteData = NoteData(Note)
        self._items: list[NoteLike] = []

        fm = Frame(self)
        fm.pack(fill="x", expand=True)
        Label(fm, text="Title").pack(side="left")
        self.title_input = Entry(
            fm,
        )
        self.title_input.pack(side="left", fill="x", expand=True)

        self.edit_commands: dict[str, Callable[[], Any]] = {}
        self.edit_buttom = FloatMenuButton(fm, text="edit", bootstyle = (OUTLINE, WARNING))
        self.edit_buttom.pack(side="right", padx=2, pady=2)

        fm = Frame(self)
        fm.pack(fill="x", expand=True)
        Label(fm, text="Time").pack(side="left")
        self.ring_switch_var = IntVar(self)
        self.ring_switch = Checkbutton(fm, text="ring", variable=self.ring_switch_var)
        self.ring_switch.pack(
            side="right",
        )

        self.time_setting_list = TimeSettingList(self)

        self.note_text = Text(self, height=3)
        self.note_text.pack()
        
        self.note_text.bind("<Return>", self.text_check)
        self.note_text.bind("<KeyRelease-BackSpace>", self.text_check)
        
    
    def text_check(self, event:Event|None = None):
        text = self.note_text.get("1.0", END)
        line = text.count("\n")
        if line <= 2:
            self.note_text.config(height=3)
        else:
            self.note_text.config(height=line+1)


    def bind_edit_button(self, commands: dict[str, Callable[[], Any]]):
        self.edit_commands = commands
        self.edit_buttom.add_commands([("delete", self.edit_commands["delete"])])

    @property
    @override
    def data(self) -> NoteData:
        self._data.time = self.time_setting_list.get()
        self._data.title = self.title_input.get()
        self._data.note = self.note_text.get("1.0", END)
        self._data.ringable = bool(self.ring_switch_var.get())
        return self._data

    @data.setter
    @override
    def data(self, value: NoteData):
        self._data = value

        self.time_setting_list.set(value.time)

        self.title_input.delete(0, END)
        self.title_input.insert(0, self._data.title)

        self.note_text.delete("1.0", END)
        self.note_text.insert("1.0", self._data.note)
        self.text_check()

        self.ring_switch_var.set(self._data.ringable)


class NoteGroup(NoteHolder):
    def __init__(self, master: Misc, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.pack(fill="x", expand=True)

        self._data: NoteData = NoteData(NoteGroup, title="")
        self._items: list[NoteLike] = []

    @property
    @override
    def data(self) -> NoteData:
        return self._data

    @data.setter
    @override
    def data(self, value: NoteData):
        self._data = value

    @property
    @override
    def items(self) -> list[NoteLike]:
        return self._items

    @items.setter
    @override
    def items(self, value: list[NoteLike]):
        self._items = value


class Workspace(NoteHolder):
    def __init__(self, master: Misc, app: App, title: str = "", *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.pack(side="top", fill="x", expand=True)

        self._app = app

        self._data: NoteData = NoteData(Workspace, title=title)
        self._items: list[NoteLike] = []

        fm = Frame(self)
        fm.pack(side="top", fill="x", expand=True, padx=4, pady=4)
        self.title_label = Label(fm)
        self.title_label.pack(side="left", fill="x", expand=True)
        FloatMenuButton(
            fm,
            text="Edit",
            command=self.rename,
            bootstyle = (OUTLINE, WARNING)
        ).add_commands(
            [
                ("rename", self.rename),
                ("delete", self.close),
            ]
        ).pack(side="right")

    @override
    def add(self, item_type: type[NoteLike], /, *args, **kwarg):
        item = super().add(item_type, *args, **kwarg)
        if isinstance(item, Note):
            item.bind_edit_button({"delete": self.build_remove_func(item)})
        return item

    def build_remove_func(self, widget: NoteLike):
        def remove():
            self.items.remove(widget)
            widget.destroy()

        return remove

    def save_to_file(self):
        while self.data.title == "":
            self.rename(prompt="title can not be empty")
        self.save()

    def close(self):
        self.destroy()

    def safe_close(self):
        self.save_to_file()
        self.close()

    def rename(self, title: str | None = None, prompt: str = "import new title"):
        if title is None:
            new_title = ask_toplevel(
                self._app,
                title="Rename workspace",
                prompt=prompt,
                default=self.data.title,
            )
        else:
            new_title = title

        if new_title is not None:
            self.config_data(title=new_title)

    @property
    @override
    def data(self) -> NoteData:
        return self._data

    @data.setter
    @override
    def data(self, value: NoteData):
        self._data = value
        self.title_label.config(text=self._data.title)

    @property
    @override
    def items(self) -> list[NoteLike]:
        return self._items

    @items.setter
    @override
    def items(self, value: list[NoteLike]):
        self._items = value


class ScrollFrame(Frame):
    def __init__(self, master: Misc, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)
        self.pack(fill="both", expand=True)
        # Canvas 提供滚动功能
        self.canvas = Canvas(self)
        self.scrollbar = Scrollbar(self, orient="vertical", command=self.canvas.yview)

        # Frame 作为内容容器放在 Canvas 中
        content_frame: Frame = Frame(self.canvas)
        content_frame.pack(fill="both", expand=True)

        # 将 Frame 放入 Canvas，并设置填充和扩展
        window_id = self.canvas.create_window(
            (0, 0),
            window=content_frame,
            anchor="nw",
            width=self.canvas.winfo_reqwidth(),
        )

        # 配置 Canvas 滚动
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        content_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        self.canvas.bind(
            "<Configure>",
            lambda event: self.canvas.itemconfig(
                window_id, width=self.canvas.winfo_width()
            ),
        )

        master.bind("<MouseWheel>", self.on_mousewheel)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.content_frame: Frame = content_frame
        self.items: list[NoteLike] = []
        
        # 占位使得笔记可以额外向上滚动一段空间
        Label(self.content_frame, text="\n"*5+r"ヾ(≧▽≦*)o").pack(side="bottom")

    def on_mousewheel(self, event: Event):
        self.canvas.yview_scroll(-event.delta // 120, "units")

    def add(self, widget: type[T_NoteLike], *args, **kwargs) -> T_NoteLike:
        # if len(self.items) > 0:
        #     sep_frame = self.split_widget()
        widget_obj = widget(master=self.content_frame, *args, **kwargs)
        self.items.append(widget_obj)
        return widget_obj


class FloatMenuButton(Button):
    def __init__(
        self,
        master: Misc,
        menu_anchor: Literal[
            "nw", "n", "ne", "w", "center", "e", "sw", "s", "se"
        ] = "nw",
        menu_reverse: bool = False,
        mouse_buttom: Literal["1", "2", "3", "4", "5"] | int = "3",
        # press: bool = False,
        *args,
        **kwargs,
    ):
        super().__init__(master, *args, **kwargs)
        self.menu_reverse = menu_reverse
        self.menu_post_anchor = menu_anchor
        # self.press = press

        self.menu = Menu(self, tearoff=False)

        def menu_post(event: Event):
            x_post, y_post = event.x_root, event.y_root
            menu_width, menu_height = (
                self.menu.winfo_reqwidth(),
                self.menu.winfo_reqheight(),
            )
            if self.menu_post_anchor == "center":
                x_post -= menu_width // 2
                y_post -= menu_height // 2
            else:
                if "e" in self.menu_post_anchor:
                    x_post -= menu_width
                if "s" in self.menu_post_anchor:
                    y_post -= menu_height

            self.menu.post(x_post, y_post)

        # def menu_unpost(event: Event|None = None):
        #     self.menu.unpost()
        #     _logger.debug("unpost")

        self.bind(
            f"<Button-{mouse_buttom}>",
            menu_post,
        )
        # if self.press:
        #     self.bind(
        #         f"<ButtonRelease-{mouse_buttom}>",
        #         menu_unpost,
        #     )
        # 松开鼠标时菜单不会消失

    def add_command(self, label: str, func: Callable[..., Any], accelerator: str = ""):
        self.menu.add_command(label=label, command=func, accelerator=accelerator)

    def add_commands(
        self,
        commands: list[
            tuple[str, Callable[..., Any]] | tuple[str, Callable[..., Any], str]
        ],
    ):
        if self.menu_reverse:
            commands.reverse()
        for i in commands:
            self.add_command(*i)  # pyright: ignore[reportArgumentType]
        return self


class AppMenu(Frame):
    def __init__(self, master: Misc, app: App, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)
        self._app: App = app
        # self.pack(side="bottom")
        self.pack(side="bottom", fill="x")

        Button(self, text="option", command=lambda: print("Button 1")).pack(
            side="left", fill="both", expand=True
        )

        Button(self, text="view", command=lambda: print("Button 2")).pack(
            side="left", fill="both", expand=True
        )

        FloatMenuButton(
            self, text="edit", mouse_buttom=1, menu_anchor="sw", menu_reverse=True
        ).add_commands(
            [("save", self._app.save, "Ctrl+S"), ("open", self._app.open)]
        ).pack(
            side="left", fill="both", expand=True
        )

        FloatMenuButton(
            self, text="new", mouse_buttom=1, menu_anchor="sw", menu_reverse=True
        ).add_commands(
            [
                ("note", lambda: self._app.active_workspace.add(Note)),
                ("group", lambda: self._app.active_workspace.add(NoteGroup)),
                (
                    "workspace",
                    lambda: self._app.new_workspace(),
                ),
            ]
        ).pack(
            side="left", fill="both", expand=True
        )


class App(Window):
    def __init__(self):
        super().__init__("NekoNoteBook")
        self.geometry("460x800")
        self.resizable(width=False, height=True)
        # pywinstyles.apply_style(self, "aero")
        AppMenu(self, self)
        self.note_frame = ScrollFrame(self)

        self._active_workspace: Workspace | None = None
        if not self.load_workspace("Main"):
            self.new_workspace("Main")

        self.bind("<Control-s>", self.save)

        self.style.register_theme(config.APP_THEME)
        self.style.theme_use("sakura_dusk")

    def save(self, event: Event | None = None):
        self.active_workspace.save_to_file()
        showinfo(
            title="save",
            message=f"save '{self.active_workspace.save_file_name()}' successfully",
        )
        _logger.info(f"save '{self.active_workspace.save_file_name()}' successfully")

    def open(self):
        title = ask_toplevel(self, title="open", prompt="Workspace file title")
        if title is None:
            return
        else:
            if not self.load_workspace(title):
                showerror(title="error", message="Failed to open")

    @property
    def active_workspace(self) -> Workspace:
        if self._active_workspace and self._active_workspace.winfo_exists():
            return self._active_workspace
        else:
            return self.new_workspace("")

    @active_workspace.setter
    def active_workspace(self, value: Workspace):
        if self._active_workspace:
            self._active_workspace.close()
            _logger.debug("_active_workspace will be replace")
        self._active_workspace = value

    @overload
    def new_workspace(self, title: None = None) -> Workspace | None: ...

    @overload
    def new_workspace(self, title: str) -> Workspace: ...

    def new_workspace(self, title: str | None = None) -> Workspace | None:
        """
        `name=None`用于需要用户立即指定title的情况, 比如主动创建新的Workspace,
        其他情况应该使用`name=""`保持静默
        """
        if title is None:
            title = ask_toplevel(self, title="New workspace", prompt="title")
        if title is None:
            return None

        if self._active_workspace and self._active_workspace.winfo_exists():
            self._active_workspace.safe_close()

        self._active_workspace = self.note_frame.add(Workspace, app=self)
        self._active_workspace.rename(title)
        return self._active_workspace

    def load_workspace(self, name: str) -> bool:
        path = Workspace.save_file_name_(name)
        _logger.info(f"load Workspace '{path}'")

        if not os.path.exists(path):
            _logger.warning(f"'{path}' not find")
            return False
        else:
            self.new_workspace(name)
            self.active_workspace.load(name)
            _logger.info("Workspace loaded successfully")
            return True

    def dump_workspace(self, fp): ...


NoteLikeStrMapping: dict[str, type] = {
    "Note": Note,
    "NoteGroup": NoteGroup,
    "Workspace": Workspace,
}


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
