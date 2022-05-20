from tkinter import ttk

class ProgressBarElement:
    def __init__(self, row_num=0, max_col=1):
        self.__style = ttk.Style()
        self.__style.layout('text.Horizontal.TProgressbar',
             [('Horizontal.Progressbar.trough',
               {'children': [('Horizontal.Progressbar.pbar',
                              {'side': 'left', 'sticky': 'ns'})],
                'sticky': 'nswe'}),
              ('Horizontal.Progressbar.label', {'sticky': ''})])
        self.__style.configure('text.Horizontal.TProgressbar', text='Нет соединения')
        self.__bar = ttk.Progressbar(style="text.Horizontal.TProgressbar", length=100)
        self.__bar.grid(row=row_num, column=0, columnspan=max_col, sticky="we", padx=5, pady=8)

    def set_text(self, txt):
        self.__style.configure('text.Horizontal.TProgressbar', text=txt)

    def set_val(self, val):
        self.__bar["value"] = val
