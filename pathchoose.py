import tkinter as tk
from tkinter import filedialog as fd
from os import path

class PathChooseElement:
    def __init__(self, title="Some text", row_num=0, callback=None):
        self.__row_id = row_num
        self.__lbl = tk.Label(text=title);
        self.__lbl.grid(row=row_num, column=0, sticky=tk.W, padx=5, pady=3)
        self.__path_var = tk.StringVar()
        self.__path_var.trace_add('write', lambda *args: self.__validate_entry())
        self.__entry = tk.Entry(width=75, textvariable=self.__path_var)
        self.__entry.grid(row=row_num, column=1, columnspan=4, sticky=tk.W, pady=3)
        self.__btn = tk.Button(text='...', command=self.__dialog_cmd)
        self.__btn.grid(row=row_num, column=5, sticky=tk.W, padx=5, pady=3)
        self.__callback = callback

    def get_path(self):
        return self.__path_var.get()

    def set_path(self, p):
        if path.isfile(p):
            revert_slash_list = p.split('\\')
            if len(revert_slash_list) > 1:
                revert_slash = '/'.join(revert_slash_list)
                self.__path_var.set(revert_slash)
            else:
                self.__path_var.set(p)

    def __validate_entry(self):
        #print('Callback')
        _path = self.__path_var.get()
        if path.isfile(_path):
            revert_slash_list = _path.split('\\')
            #print(revert_slash_list )
            if len(revert_slash_list) > 1:
                revert_slash = '/'.join(revert_slash_list)
                self.__path_var.set(revert_slash)
            if self.__callback:
                self.__callback(True, self.__row_id)
        else:
            if self.__callback:
                self.__callback(False, self.__row_id)

    def __dialog_cmd(self):
        last_path = self.__path_var.get()
        print(last_path)
        if len(last_path):
            last_path_dir = '/'.join(last_path.split('/')[0:-1])
            init_dir = last_path_dir
        else:
            init_dir = '/'
        filename = fd.askopenfilename(title="Выберите файл...", initialdir=init_dir)
        if len(filename):
            self.__path_var.set(filename)
        print(filename, "len : %s" % len(filename))
