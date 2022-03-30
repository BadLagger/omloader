import tkinter as tk
import serial
import serial.tools.list_ports
from tkinter import ttk

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
