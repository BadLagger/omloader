import tkinter as tk
import serial
import serial.tools.list_ports
from tkinter import ttk
from threading import Thread
from time import sleep

class PortElement:
    def __init__(self, title="Port", row_num=0, fw_update_cmd=None):
        self.__lbl = tk.Label(text=title);
        self.__lbl.grid(row=row_num, column=0, sticky=tk.W, padx=5, pady=3)
        self.__list = ttk.Combobox(state=tk.DISABLED)
        self.__list.grid(row=row_num, column=1, sticky="we", pady=3)
        #self.__emmc_var = tk.IntVar()
        #self.__emmc_var.set(1)
        #self.__check_emmc = tk.Checkbutton(text="EMMC", variable=self.__emmc_var, state=tk.DISABLED)
        #self.__check_emmc.grid(row=row_num, column=2, sticky="we", pady=3)
        self.__erase_var = tk.IntVar()
        self.__check = tk.Checkbutton(text="Со стиранием", variable=self.__erase_var, command=self.__erase_cmd)
        self.__check.grid(row=row_num, column=2, sticky="we", pady=3)
        self.__btn = tk.Button(text='Прошить', state=tk.DISABLED, command=fw_update_cmd)
        self.__btn.grid(row=row_num, column=4, columnspan=2, sticky="we", padx=5, pady=3)
        self.__esc_f = None
        self.__dbg_foo = False

    def enable_update(self):
        self.__btn['state'] = tk.NORMAL

    def disable_update(self):
        self.__btn['state'] = tk.DISABLED

    def get_erase(self):
        return self.__erase_var.get()

    def try_erase(self, esc_f=None, prg_f=None):
        #port = self.__list.get()
        #print(port)
        self.__esc_f = esc_f
        self.__dbg_foo = prg_f
        self.__dbg('Открытие порта: %s' % self.__list.get())
        self.__wait_th = Thread(target=self.__wait_port)
        self.__wait_th.start()
        self.__wait_th.join()
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

    def __wait_port(self):
        uboot_wait = False
        mmc_cmds = [b'mmc dev 0 1\n', b'mmc erase 0 0x2000\n', b'mmc dev 0 2\n', b'mmc erase 0 0x2000\n', b'reset\n']
        mmc_state = 0
        with serial.Serial(self.__list.get(), 115200, timeout=1) as ser:
            count = 0
            line = ""
            while ser.is_open:
                if self.__esc_f:
                    if self.__esc_f():
                        break
                #count += 1
                try:
                    if ser.in_waiting:
                        char = ser.read().decode("ascii")
                    else:
                        continue
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
                            self.__dbg('Подключение к Uboot')
                else:
                    if line.find('u-boot=>') != -1:
                        print(line)
                        print("state: %d len: %d" % (mmc_state, len(mmc_cmds)))
                        if mmc_state < len(mmc_cmds):
                            ser.write(mmc_cmds[mmc_state])
                            mmc_state += 1
                            if mmc_state < 2:
                                self.__dbg('Стирание emmc 1')
                            elif mmc_state < 4:
                                self.__dbg('Стирание emmc 2')
                            else:
                                self.__dbg('Перезагрузка')
                        else:
                            print('All cmds send')
                            #return True
                        line = ""
                    else:
                        #print("Not uboot")
                        if line.find('resetting') != -1:
                            print(line)
                            print('Erasing Done!!!')
                            break

    def __dbg(self, txt):
        if self.__dbg_foo:
            self.__dbg_foo(txt)
