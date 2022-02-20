import tkinter as tk
from tkinter import filedialog as fd
from tkinter import ttk
import json
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

import serial.tools.list_ports
class PortElement:
    def __init__(self, title="Port", row_num=0, fw_update_cmd=None):
        self.__lbl = tk.Label(text=title);
        self.__lbl.grid(row=row_num, column=0, sticky=tk.W, padx=5, pady=3)
        self.__list = ttk.Combobox(state=tk.DISABLED)
        self.__list.grid(row=row_num, column=1, sticky="we", pady=3)
        self.__emmc_var = tk.IntVar()
        self.__emmc_var.set(1)
        self.__check_emmc = tk.Checkbutton(text="EMMC", variable=self.__emmc_var, state=tk.DISABLED)
        self.__check_emmc.grid(row=row_num, column=2, sticky="we", pady=3)
        self.__erase_var = tk.IntVar()
        self.__check = tk.Checkbutton(text="Со стиранием", variable=self.__erase_var, command=self.__erase_cmd)
        self.__check.grid(row=row_num, column=3, sticky="we", pady=3)
        self.__btn = tk.Button(text='Прошить', state=tk.DISABLED, command=fw_update_cmd)
        self.__btn.grid(row=row_num, column=4, columnspan=2, sticky="we", padx=5, pady=3)

    def enable_update(self):
        self.__btn['state'] = tk.NORMAL

    def disable_update(self):
        self.__btn['state'] = tk.DISABLED

    def __erase_cmd(self):
        if self.__erase_var.get():
            self.__list["state"] = tk.NORMAL
            port_values = []
            ports = serial.tools.list_ports.comports()
            for port, desc, hwid in sorted(ports):
                #print("{}: {} [{}]".format(port, desc, hwid))
                port_values.append(port)
            self.__list["values"] = port_values
            self.__list.current(0)
        else:
            self.__list["values"] = [""]
            self.__list.current(0)
            self.__list["state"] = tk.DISABLED

class ProgressBarElement:
    def __init__(self, row_num=0, max_col=1):
        self.__style = ttk.Style()
        self.__style.layout('text.Horizontal.TProgressbar',
             [('Horizontal.Progressbar.trough',
               {'children': [('Horizontal.Progressbar.pbar',
                              {'side': 'left', 'sticky': 'ns'})],
                'sticky': 'nswe'}),
              ('Horizontal.Progressbar.label', {'sticky': ''})])
        self.__style.configure('text.Horizontal.TProgressbar', text='0 %')
        self.__bar = ttk.Progressbar(style="text.Horizontal.TProgressbar", length=100)
        self.__bar.grid(row=row_num, column=0, columnspan=max_col, sticky="we", padx=5, pady=8)


class MainFrame:
    def __init__(self, title='MainFrame'):
        self.__w = tk.Tk()
        self.__w.title(title)
        self.__cfg = self.__open_cfg()
        self.__w.geometry("%dx%d+%d+%d" % (self.__cfg['width'],
                                            self.__cfg['height'],
                                            self.__cfg['win_x'],
                                            self.__cfg['win_y']))
        self.__w.resizable(False, False)
        self.__w.protocol('WM_DELETE_WINDOW', self.__on_clossing_event)
        # Path elements
        self.__uuu = PathChooseElement("Путь к UUU:", 0, self.__update_from_entry)
        self.__loader = PathChooseElement("Путь к загрузчику:", 1, self.__update_from_entry)
        self.__fw = PathChooseElement("Путь к прошивке:", 2, self.__update_from_entry)
        self.__allow_update = [False, False, False]
        # Port element
        self.__port = PortElement("Порты:", 3, self.update_fw)
        # ProgressBar
        self.__bar = ProgressBarElement(4, 6)
        # Initial states
        if self.__cfg.get('uuu'):
            self.__uuu.set_path(self.__cfg['uuu'])
        if self.__cfg.get('loader'):
            self.__loader.set_path(self.__cfg['loader'])
        if self.__cfg.get('fw'):
            self.__fw.set_path(self.__cfg['fw'])


    def go(self):
        self.__w.mainloop()

    def update_fw(self):
        print('Try update')
        pass

    def __update_from_entry(self, state, id):
        #print('Entry external callback: %s %d' % (state, id))
        self.__allow_update[id] = state
        if self.__allow_update[0] and self.__allow_update[1] and self.__allow_update[2]:
            self.__port.enable_update()
        else:
            self.__port.disable_update()

    def __open_cfg(self):
        cfg = {}
        try:
            with open('oml.cfg') as f:
                cfg = json.load(f)
        except:
            #print("No cfg or corrupted -- use default")
            cfg['width'] = 603
            cfg['height'] = 170
            cfg['win_x'] = 0
            cfg['win_y'] = 0
        return cfg

    def __save_cfg(self):
        pathes = [self.__uuu.get_path(), self.__loader.get_path(), self.__fw.get_path()]
        if path.isfile(pathes[0]):
            self.__cfg['uuu'] = pathes[0]
        if path.isfile(pathes[1]):
            self.__cfg['loader'] = pathes[1]
        if path.isfile(pathes[2]):
            self.__cfg['fw'] = pathes[2]
        with open('oml.cfg', 'w') as f:
            json.dump(self.__cfg, f)

    def __on_clossing_event(self):
        #print('close')
        self.__cfg['win_x'], self.__cfg['win_y'] = self.__w.winfo_x(), self.__w.winfo_y()
        self.__save_cfg()
        self.__w.destroy()
