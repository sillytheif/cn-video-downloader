"""Chinese CustomTkinter desktop UI."""
import queue
import threading
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
import customtkinter as ctk
from .downloader import DownloadQueue
from .paths import downloads_dir
from .url_parser import parse_urls


class DownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title('国内视频下载器')
        self.geometry('1000x820')
        self.minsize(780, 650)
        self.worker = DownloadQueue()
        self.active = False
        self.closing = False
        self.states = {}
        self.percent = {}
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)
        ctk.CTkLabel(self, text='粘贴视频链接（换行、逗号或空格分隔）', font=('', 18)).grid(row=0, column=0, padx=20, pady=(16, 4), sticky='w')
        self.input = ctk.CTkTextbox(self, height=135)
        self.input.grid(row=1, column=0, padx=20, sticky='ew')
        frame = ctk.CTkFrame(self)
        frame.grid(row=2, column=0, padx=20, pady=8, sticky='ew')
        frame.grid_columnconfigure(1, weight=1)
        ctk.CTkButton(frame, text='从文件导入 (.txt)', command=self.import_file, width=145).grid(row=0, column=0, padx=6, pady=6)
        self.folder = ctk.StringVar(value=str(downloads_dir()))
        ctk.CTkEntry(frame, textvariable=self.folder).grid(row=0, column=1, padx=6, sticky='ew')
        ctk.CTkButton(frame, text='选择保存文件夹', command=self.choose_folder, width=130).grid(row=0, column=2, padx=6)
        buttons = ctk.CTkFrame(self)
        buttons.grid(row=3, column=0, padx=20, sticky='ew')
        self.start_button = ctk.CTkButton(buttons, text='开始下载', command=self.start)
        self.start_button.pack(side='left', padx=6, pady=6)
        self.cancel_button = ctk.CTkButton(buttons, text='取消', command=self.cancel, state='disabled')
        self.cancel_button.pack(side='left', padx=6)
        ctk.CTkButton(buttons, text='清空列表状态', command=self.clear).pack(side='left', padx=6)
        self.summary = ctk.CTkLabel(buttons, text='就绪 · 最多同时下载 2 个视频')
        self.summary.pack(side='right', padx=8)
        self.progress = ctk.CTkProgressBar(self)
        self.progress.grid(row=4, column=0, padx=20, pady=10, sticky='ew')
        self.progress.set(0)
        table = ctk.CTkFrame(self)
        table.grid(row=5, column=0, padx=20, sticky='nsew')
        table.grid_columnconfigure(0, weight=1)
        table.grid_rowconfigure(0, weight=1)
        self.tree = ttk.Treeview(table, columns=('url', 'status', 'message'), show='headings', height=8)
        for key, title, width in [('url', '视频链接', 380), ('status', '状态', 75), ('message', '说明', 370)]:
            self.tree.heading(key, text=title)
            self.tree.column(key, width=width, minwidth=60)
        self.tree.grid(row=0, column=0, sticky='nsew')
        scroll = ttk.Scrollbar(table, command=self.tree.yview)
        scroll.grid(row=0, column=1, sticky='ns')
        self.tree.configure(yscrollcommand=scroll.set)
        ctk.CTkLabel(self, text='日志 · 仅下载网站允许公开访问的内容，不支持 DRM 或会员限制破解').grid(row=6, column=0, padx=20, pady=(8, 0), sticky='w')
        self.log = ctk.CTkTextbox(self, height=170, state='disabled')
        self.log.grid(row=7, column=0, padx=20, pady=(4, 16), sticky='ew')
        self.protocol('WM_DELETE_WINDOW', self.close)
        self.after(100, self.poll)

    def import_file(self):
        name = filedialog.askopenfilename(filetypes=[('文本文件', '*.txt')])
        if name:
            try:
                raw = Path(name).read_bytes()
                try:
                    text = raw.decode('utf-8-sig')
                except UnicodeDecodeError:
                    text = raw.decode('gb18030')
                self.input.insert('end', '\n' + text)
            except (OSError, UnicodeError) as exc:
                messagebox.showerror('导入失败', str(exc))

    def choose_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder.set(folder)

    def start(self):
        if self.active:
            return
        urls = parse_urls(self.input.get('1.0', 'end'))
        if not urls:
            messagebox.showinfo('提示', '请粘贴有效的 http 或 https 视频链接。')
            return
        if not self.folder.get().strip():
            messagebox.showinfo('提示', '请选择保存文件夹。')
            return
        self.clear()
        for index, url in enumerate(urls):
            self.tree.insert('', 'end', iid=str(index), values=(url, '等待', '排队中'))
            self.states[index] = '等待'
            self.percent[index] = 0
        self.active = True
        self.start_button.configure(state='disabled')
        self.cancel_button.configure(state='normal')
        self.worker.start(urls, Path(self.folder.get()).expanduser())

    def clear(self):
        if self.active:
            messagebox.showinfo('提示', '请先取消并等待当前任务结束，再清空列表。')
            return
        self.tree.delete(*self.tree.get_children())
        self.states.clear()
        self.percent.clear()
        self.progress.set(0)
        self.summary.configure(text='就绪 · 最多同时下载 2 个视频')
        self.log.configure(state='normal')
        self.log.delete('1.0', 'end')
        self.log.configure(state='disabled')

    def cancel(self):
        self.cancel_button.configure(state='disabled')
        self.summary.configure(text='正在取消…')
        threading.Thread(target=self.worker.cancel, daemon=True).start()

    def poll(self):
        for _ in range(300):
            try:
                event = self.worker.events.get_nowait()
            except queue.Empty:
                break
            kind, index, *data = event
            if kind == 'log':
                self.log.configure(state='normal')
                self.log.insert('end', f'[{index + 1}] {data[0]}\n')
                if int(self.log.index('end-1c').split('.')[0]) > 1500:
                    self.log.delete('1.0', '200.0')
                self.log.see('end')
                self.log.configure(state='disabled')
            else:
                status, message, progress = data
                self.states[index] = status
                self.percent[index] = progress
                self.tree.set(str(index), 'status', status)
                self.tree.set(str(index), 'message', message)
        if self.active:
            terminal = ('完成', '失败', '已取消')
            done = sum(s in terminal for s in self.states.values())
            total = len(self.states)
            value = sum(1 if s in terminal else self.percent[i] / 100 * .95 for i, s in self.states.items()) / total
            self.progress.set(value)
            self.summary.configure(text=f'已处理 {done}/{total} · 成功 {list(self.states.values()).count("完成")}')
            if done == total:
                self.active = False
                self.start_button.configure(state='normal')
                self.cancel_button.configure(state='disabled')
        if self.closing and not self.active:
            self.destroy()
            return
        self.after(100, self.poll)

    def close(self):
        self.closing = True
        if self.active:
            self.cancel()
        else:
            self.destroy()
