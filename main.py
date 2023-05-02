import threading
import time
import customtkinter as ctk
import deepl
import json
from tkinter import *
from tkinterdnd2 import *

auth_key = '2cc789ad-1a69-64b7-e071-f855526d57a4:fx'
translator = deepl.Translator(auth_key)
progress = 0
total = 0
max_threads_num = 100
isRunning = False


def trans_to_chinese(data: str, index, temp) -> str:
    global progress
    result = translator.translate_text(data, target_lang="ZH")
    temp[index] = result
    progress += 1
    update_progress()


def update_progress():
    global progress
    global total
    percent = str(format(progress / total * 100, '.1f'))
    label.configure(text='翻译中\n' + percent + '%')


def translate_srt(path):
    data = ''
    start = time.time()

    x = path.split('/')
    length = len(x)
    file_name = path.replace(x[length - 1], x[length - 1].replace('.srt', '.zh.srt'))
    temp = [None]
    threads = []
    global progress
    global max_threads_num
    global total
    global isRunning
    with open(path, 'r') as my_file:
        lines = my_file.readlines()
        total = len(lines)
        temp = [None] * len(lines)
        for index, line in enumerate(lines):
            if line[0].isdigit():
                temp[index] = line
                progress += 1
                update_progress()
            else:
                t = threading.Thread(target=trans_to_chinese, args=(line, index, temp))
                t.start()
                threads.append(t)
                if len(threads) >= max_threads_num:
                    for thread in threads:
                        thread.join()
                    threads.clear()

    for thread in threads:
        thread.join()
    for line in temp:
        data += str(line)
    end = time.time()
    print(path)
    file = open(file_name, 'w', encoding='utf-8')
    file.write(data)
    duration = format((end - start), '.1f')
    label.configure(text=x[length - 1] + '\n' + '完成' + '\n耗时 ' + str(duration) + ' 秒')
    isRunning = False


def get_path(event):
    global isRunning
    if event.data.endswith('.srt') & isRunning == False:
        url = event.data
        t = threading.Thread(target=translate_srt, args=(url,), daemon=True)
        t.start()
        isRunning = True


# GUI

data = {
    'pos_x': 0,
    'pos_y': 0
}


# Enable dnd in customtkinter
class Tk(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)


class Root(Tk):
    def __init__(self):
        super().__init__()
        self.title('srt')
        self.resizable(0, 0)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        try:
            j = open('./data.json')
        except FileNotFoundError:
            j = open('./data.json', 'w')
            json.dump(data, j)

        self.overrideredirect(1)
        self.wm_attributes('-topmost', 1)
        #
        new_data = json.load(j)
        x = new_data['pos_x']
        y = new_data['pos_y']
        self.geometry(f'200x200+{x}+{y}')
        j.close()


root = Root()
root.configure(fg_color=("white", '#2F4F4F'))
X = IntVar(root, value=0)
Y = IntVar(root, value=0)


def on_left_down(event):
    X.set(event.x)
    Y.set(event.y)


def on_left_move(event):
    new_x = root.winfo_x() + (event.x - X.get())
    new_y = root.winfo_y() + (event.y - Y.get())
    root.geometry(f'200x200+{new_x}+{new_y}')


def on_left_up(event):
    j = open('./data.json', 'w')
    data['pos_x'] = root.winfo_x()
    data['pos_y'] = root.winfo_y()
    json.dump(data,j)
    j.close()


label = ctk.CTkLabel(root, text="空", bg_color=('white', '#2F4F4F'))
label.pack()
label.grid(row=0, column=0)

# pb = ctk.CTkProgressBar(root)
# pb.set(0.2)
# pb.grid(row=1, column=0)

root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', get_path)
root.bind('<Button-1>', on_left_down)
# root.bind('<ButtonRelease-1>', on_left_up)
root.bind('<B1-Motion>', on_left_move)

if __name__ == "__main__":
    root.mainloop()
