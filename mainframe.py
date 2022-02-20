import tkinter as tk
import json

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

    def go(self):
        self.__w.mainloop()

    def __open_cfg(self):
        cfg = {}
        try:
            with open('oml.cfg') as f:
                cfg = json.load(f)
        except:
            #print("No cfg or corrupted -- use default")
            cfg['width'] = 400
            cfg['height'] = 100
            cfg['win_x'] = 0
            cfg['win_y'] = 0
        return cfg

    def __save_cfg(self):
        with open('oml.cfg', 'w') as f:
            json.dump(self.__cfg, f)

    def __on_clossing_event(self):
        #print('close')
        self.__cfg['win_x'], self.__cfg['win_y'] = self.__w.winfo_x(), self.__w.winfo_y()
        self.__save_cfg()
        self.__w.destroy()
