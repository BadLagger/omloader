import tkinter as tk
from tkinter import ttk
import json
from pathchoose import PathChooseElement

import serial
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

    def get_erase(self):
        return self.__erase_var.get()

    def try_erase(self, esc_f=None, prg_f=None):
        port = self.__list.get()
        print(port)
        interval_sec = 1
        uboot_wait = False
        mmc_cmds = [b'mmc dev 0 1\n', b'mmc erase 0 0x2000\n', b'mmc dev 0 2\n', b'mmc erase 0 0x2000\n', b'reset\n']
        mmc_state = 0
        prg_f('Открытие порта: %s' % port)
        with serial.Serial(port, 115200, timeout=interval_sec) as ser:
            count = 0
            line = ""
            while ser.is_open:
                if esc_f:
                    if esc_f():
                        break
                #count += 1
                try:
                    char = ser.read().decode("ascii")
                except:
                    char = ''
                #print(char,end='')
                line += char
                if uboot_wait == False:
                    if char == '\n':
                        line = ""
                    else:
                        if line.find('Hit any key to stop autoboot: ') != -1:
                            ser.write(b' ')
                            line = ""
                            uboot_wait = True
                        else:
                            if prg_f:
                                prg_f('Подключение к Uboot')
                else:
                    if line.find('u-boot=>') != -1:
                        print(line)
                        print("state: %d len: %d" % (mmc_state, len(mmc_cmds)))
                        if mmc_state < len(mmc_cmds):
                            ser.write(mmc_cmds[mmc_state])
                            mmc_state += 1
                            if mmc_state < 2:
                                if prg_f:
                                    prg_f('Стирание emmc 1')
                            elif mmc_state < 4:
                                if prg_f:
                                    prg_f('Стирание emmc 2')
                            else:
                                if prg_f:
                                    prg_f('Перезагрузка')
                        else:
                            print('All cmds send')
                            #return True
                        line = ""
                    else:
                        #print("Not uboot")
                        if line.find('resetting') != -1:
                            print(line)
                            print('Erasing Done!!!')
                            return True
        print('Close port')
        return False

    def change_btn_text(self, txt):
        self.__btn['text'] = txt

    def __erase_cmd(self):
        if self.__erase_var.get():
            self.__list["state"] = tk.NORMAL
            port_values = []
            ports = serial.tools.list_ports.comports()
            for port, desc, hwid in sorted(ports):
                #print("{}: {} [{}]".format(port, desc, hwid))
                port_values.append(port)
            self.__list["values"] = port_values
            if len(port_values) != 0:
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
        self.__style.configure('text.Horizontal.TProgressbar', text='No Conection')
        self.__bar = ttk.Progressbar(style="text.Horizontal.TProgressbar", length=100)
        self.__bar.grid(row=row_num, column=0, columnspan=max_col, sticky="we", padx=5, pady=8)

    def set_text(self, txt):
        self.__style.configure('text.Horizontal.TProgressbar', text=txt)

    def set_val(self, val):
        self.__bar["value"] = val

import subprocess
import os
import time
from subroute import Subroute
from threading import Thread
import platform
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
        # Internal flags
        self.__update_start = False
        self.__update_th = None
        self.__stop_update = False

    def go(self):
        self.__w.mainloop()

    def update_fw(self):
        if self.__update_start == False:
            self.__update_start = True
            self.__port.change_btn_text("Остановить")
            self.__update_th = Thread(target=self.__update_thread)
            self.__update_th.start()
        else:
            self.__update_start = False
            self.__stop_update = True
            self.__update_th.join()
            self.__bar.set_text('Обновление отменено')
            self.__port.change_btn_text("Прошить")

    def __update_thread(self):
        print('Update thread bng')
        self.__bar.set_text('Обновление')
        if self.__port.get_erase():
            print('Try erase')
            if self.__port.try_erase(esc_f=self.__stop_update, prg_f=self.__bar.set_text) == False:
                print('Canceled')
        if self.__stop_update == False:
            if path.isfile("./cmdoutput.txt"):
                os.remove("./cmdoutput.txt")
            pr = Subroute("sudo %s -b emmc_all %s %s &> cmdoutput.txt" % (self.__uuu.get_path(),
                                                                          self.__loader.get_path(),
                                                                          self.__fw.get_path()))
            l_size = 0
            while pr.is_online():
                if self.__stop_update == True:
                    pr.stop()
                    break
                else:
                    if path.isfile("./cmdoutput.txt"):
                        f_size = path.getsize("./cmdoutput.txt")
                        if l_size != f_size:
                            l_size = f_size
                            print("File size: %d" % l_size)
                            with open("./cmdoutput.txt", "br") as f:
                                count = 200
                                if count >= l_size:
                                    count = l_size - 10
                                f.seek(-2, 2)
                                while f.read(1) != b'%':
                                    f.seek(-2, 1)
                                    if count == 0:
                                        break
                                    else:
                                        count -= 1
                                if count:
                                    f.seek(-3, 1)
                                    count = 1
                                    while f.read(1) != b'm':
                                        f.seek(-2, 1)
                                        count += 1
                                    percents = f.read(count).decode('ascii')
                                    print(percents)
                                    self.__bar.set_text('%s %%' % percents)
                                    self.__bar.set_val(int(percents))
        print('Update thread done')
        if self.__stop_update == True:
            self.__stop_update = False
        else:
            self.__update_start = False
            self.__port.change_btn_text("Прошить")
            self.__bar.set_text('Готово!!!')
            self.__bar.set_val(0)
        print('done!!!')

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
        if self.__update_start:
            self.__update_start = False
            self.__stop_update = True
            self.__update_th.join()
            self.__port.change_btn_text("Прошить")

        self.__cfg['win_x'], self.__cfg['win_y'] = self.__w.winfo_x(), self.__w.winfo_y()
        self.__save_cfg()
        self.__w.destroy()
