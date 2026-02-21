from tkinter import *
from tkinter.ttk import *

class AskToplevel:
    def __init__(self, master, title="title", prompt="prompt", default=""):
        self.result:str|None = ""  # 保存用户输入的结果
        
        # 创建顶级窗口
        self.dialog = Toplevel(master)
        self.dialog.title(title)
        self.dialog.transient(master)  # 设置为父窗口的临时窗口
        self.dialog.grab_set()  # 设置焦点，模态效果
        
        # 设置窗口大小和位置
        self.dialog.geometry("300x150")
        
        # 使窗口居中显示
        self.dialog.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() - self.dialog.winfo_width()) // 2
        y = master.winfo_y() + (master.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")
        
        # 关闭按钮的处理
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_cancel)
        
        # 创建界面元素
        self.create_widgets(prompt, default)
        
        # 等待窗口关闭
        master.wait_window(self.dialog)
    
    def create_widgets(self, prompt, default):
        """创建界面元素"""
        # 提示标签
        label = Label(self.dialog, text=prompt)
        label.pack(pady=(20, 10))
        
        # 输入框
        self.entry = Entry(self.dialog, width=30)
        self.entry.pack(pady=(0, 20))
        self.entry.insert(0, default)
        self.entry.focus_set()  # 设置焦点
        
        # 按钮框架
        btn_frame = Frame(self.dialog)
        btn_frame.pack()
        
        # 确认按钮
        ok_btn = Button(btn_frame, text="确定", command=self.on_ok)
        ok_btn.pack(side=LEFT, padx=5)
        
        # 取消按钮
        cancel_btn = Button(btn_frame, text="取消", command=self.on_cancel)
        cancel_btn.pack(side=LEFT, padx=5)
        
        # 绑定回车键到确认按钮
        self.dialog.bind('<Return>', lambda e: self.on_ok())
        # 绑定ESC键到取消按钮
        self.dialog.bind('<Escape>', lambda e: self.on_cancel())
    
    def on_ok(self):
        """确定按钮的处理函数"""
        self.result = self.entry.get()
        self.dialog.destroy()
    
    def on_cancel(self):
        """取消按钮的处理函数"""
        self.result = None
        self.dialog.destroy()


def main():
    root = Tk()
    inp = AskToplevel(root, default="123123")
    root.mainloop()
    print(inp.result)

if __name__ == '__main__':
    main()