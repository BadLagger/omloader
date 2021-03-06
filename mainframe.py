import tkinter as tk
import json
from os import path
import subprocess
import os
import time
from subroute import Subroute
from threading import Thread
import platform

from pathchoose import PathChooseElement
from port import PortElement
from progress import ProgressBarElement

class MainFrameEMMC:
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
        self.__bar.set_text('Подождите, идёт обновление...')
        if self.__port.get_erase():
            print('Try erase')
            if self.__port.try_erase(esc_f=lambda : self.__stop_update, prg_f=self.__bar.set_text) == False:
                print('Canceled')
        if self.__stop_update == False:
            if path.isfile("./cmdoutput.txt"):
                os.remove("./cmdoutput.txt")
            cmd_str = ""
            if platform.system() == 'Linux':
                 cmd_str = "sudo %s -b emmc_all %s %s &> cmdoutput.txt"
            else:
                 cmd_str = "%s -b emmc_all %s %s > cmdoutput.txt"
            pr = Subroute(cmd_str % (self.__uuu.get_path(),
                                     self.__loader.get_path(),
                                     self.__fw.get_path()))
            l_size = 0
            self.__bar.set_text('Ожидание подключения USB')
            count = 0
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
                            if l_size > 200:
                                msg = 'Подождите, идёт обновление'
                                if count % 4 == 1:
                                    msg += '.'
                                elif count % 4 == 2:
                                    msg += '..'
                                elif count % 4 == 3:
                                    msg += '...'
                                self.__bar.set_text(msg)
                                count += 1
                            #with open("./cmdoutput.txt", "br") as f:
                            #    count = 200
                            #    if count >= l_size:
                            #        count = l_size - 10
                            #    f.seek(-2, 2)
                            #    while f.read(1) != b'%':
                            #        f.seek(-2, 1)
                            #        if count == 0:
                            #            break
                            #        else:
                            #            count -= 1
                            #    if count:
                            #        f.seek(-3, 1)
                            #        count = 1
                            #        while f.read(1) != b'm':
                            #            f.seek(-2, 1)
                            #            count += 1
                            #        percents = f.read(count).decode('ascii')
                            #        print(percents)
                            #        self.__bar.set_text('%s %%' % percents)
                            #        self.__bar.set_val(int(percents))
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
            with open('emmc.cfg') as f:
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
        with open('emmc.cfg', 'w') as f:
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

#### Form for work with NAND
class MainFrameNAND:
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
        #self.__uuu = PathChooseElement("Путь к UUU:", 0, self.__update_from_entry)
        self.__loader = PathChooseElement("Путь к загрузчику:", 0, self.__update_from_entry)
        self.__kernel = PathChooseElement("Путь к ядру:", 1, self.__update_from_entry)
        self.__dtb = PathChooseElement("Путь к dtb:", 2, self.__update_from_entry)
        self.__rootfs = PathChooseElement("Путь к rootfs:", 3, self.__update_from_entry)
        self.__allow_update = [False, False, False, False]
        # Port element
        self.__port = PortElement("Порты:", 4, self.update_fw)
        # ProgressBar
        self.__bar = ProgressBarElement(5, 7)

    def update_fw(self):
        self.__bar.set_text('Готово!!!')

    def __update_from_entry(self, state, id):
        #print('Entry external callback: %s %d' % (state, id))
        self.__allow_update[id] = state
        if False in self.__allow_update:
            self.__port.disable_update()
        else:
            self.__port.enable_update()
        #if self.__allow_update[0] and self.__allow_update[1] and self.__allow_update[2]:
        #    self.__port.enable_update()
        #else:
        #    self.__port.disable_update()

    def __open_cfg(self):
        cfg = {}
        try:
            with open('nand.cfg') as f:
                cfg = json.load(f)
        except:
            #print("No cfg or corrupted -- use default")
            cfg['width'] = 603
            cfg['height'] = 250
            cfg['win_x'] = 0
            cfg['win_y'] = 0
        return cfg

    def __save_cfg(self):
        #pathes = [self.__uuu.get_path(), self.__loader.get_path(), self.__fw.get_path()]
        pathes = ["", "", ""]
        if path.isfile(pathes[0]):
            self.__cfg['uuu'] = pathes[0]
        if path.isfile(pathes[1]):
            self.__cfg['loader'] = pathes[1]
        if path.isfile(pathes[2]):
            self.__cfg['fw'] = pathes[2]
        with open('nand.cfg', 'w') as f:
            json.dump(self.__cfg, f)

    def __on_clossing_event(self):
        #print('close')
        #if self.__update_start:
        #    self.__update_start = False
        #    self.__stop_update = True
        #    self.__update_th.join()
        #    self.__port.change_btn_text("Прошить")

        self.__cfg['win_x'], self.__cfg['win_y'] = self.__w.winfo_x(), self.__w.winfo_y()
        self.__save_cfg()
        self.__w.destroy()

    def go(self):
        self.__w.mainloop()
