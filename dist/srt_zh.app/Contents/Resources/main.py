import threading
import time
import customtkinter as ctk
import deepl
import json
from tkinter import *
from tkinterdnd2 import *

auth_key = ''
translator = None
progress = 0
total = 0
max_threads_num = 100
isRunning = False
auth_key = None
has_key = False


def trans_to_chinese(data: str, index, temp) -> str:
    global progress
    global translator
    translator = deepl.Translator(auth_key)
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
    with open(path, 'r', encoding="utf-8") as my_file:
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
    global has_key
    if event.data.endswith('.srt') & isRunning is False & has_key:
        url = event.data
        t = threading.Thread(target=translate_srt, args=(url,), daemon=True)
        t.start()
        isRunning = True


# GUI

empty_data = {
    'pos_x': 0,
    'pos_y': 0,
    'key': ''
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
        self.columnconfigure(3, weight=1)
        self.rowconfigure(3, weight=1)

        try:
            j = open('./data.json')
        except FileNotFoundError:
            j = open('./data.json', 'w')
            json.dump(empty_data, j)

        self.overrideredirect(1)
        self.wm_attributes('-topmost', 1)
        #
        data = json.load(j)
        x = data['pos_x']
        y = data['pos_y']
        self.geometry(f'200x200+{x}+{y}')
        global has_key
        global auth_key
        global translator
        auth_key = data['key']
        if auth_key != '':
            try:
                translator_test = deepl.Translator(auth_key)
                translator_test.translate_text("data", target_lang="ZH")
            except:
                print('error: key wrong')
            else:
                has_key = True
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
    j = open('./data.json', 'r')
    data = json.load(j)
    j.close()
    data['pos_x'] = root.winfo_x()
    data['pos_y'] = root.winfo_y()
    f = open('./data.json', 'w')
    json.dump(data, f)
    f.close()


def on_button_click():
    global auth_key
    global has_key
    print(input_field.get())
    auth_key = input_field.get()
    translator_test = deepl.Translator(auth_key)
    try:
        translator_test.translate_text("data", target_lang="ZH")
    except:
        print('error')
    else:
        has_key = True
        j = open('./data.json', 'r')
        data = json.load(j)
        j.close()
        data['key'] = auth_key
        f = open('./data.json', 'w')
        json.dump(data, f)
        f.close()
        label.pack()
        label.configure(padx=100, pady=100)
        button.destroy()
        input_field.destroy()


label = ctk.CTkLabel(root, text="空", bg_color=('white', '#2F4F4F'))
button = ctk.CTkButton(root, text="确认", bg_color=('white', '#2F4F4F'), command=on_button_click)
input_field = ctk.CTkEntry(root, placeholder_text="DeepL api key")


def check_key():
    if has_key:
        label.pack()
        label.configure(padx=100, pady=100)
    else:
        button.pack()
        input_field.pack()
        input_field.place(x=30, y=50)
        button.configure(width=90, height=20, anchor='center')
        button.place(x=55, y=130)


# pb = ctk.CTkProgressBar(root)
# pb.set(0.2)
# pb.grid(row=1, column=0)

root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', get_path)
root.bind('<Button-1>', on_left_down)
root.bind('<ButtonRelease-1>', on_left_up)
root.bind('<B1-Motion>', on_left_move)
check_key()

if __name__ == "__main__":
    root.mainloop()
