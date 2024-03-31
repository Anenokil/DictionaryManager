import os
import shutil
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
import requests
import wget
import zipfile

""" Информация о программе """

PROGRAM_NAME = 'Dictionary Manager'

""" Пути, файлы, ссылки """


MAIN_PATH = os.path.dirname(__file__)  # Папка с установщиком
RESOURCES_DIR = 'resources'
ADDITIONAL_THEMES_DIR = 'themes'

# Название репозитория на GitHub
REPOSITORY_NAME = 'DictionaryManager'

# Ссылки
URL_LAST_VERSION = f'https://raw.githubusercontent.com/Anenokil/{REPOSITORY_NAME}/master/ver'
URL_DOWNLOAD_ZIP = f'https://github.com/Anenokil/{REPOSITORY_NAME}/archive/refs/heads/master.zip'
URL_DOWNLOAD_THEMES_ZIP = f'https://github.com/Anenokil/{REPOSITORY_NAME}/releases/download/v7.1.0/themes_v6.zip'

# Папки и файлы для установки обновлений
DOWNLOADED_PROGRAM_DIR = f'{REPOSITORY_NAME}-master'
DOWNLOADED_PROGRAM_ZIP = f'{DOWNLOADED_PROGRAM_DIR}.zip'
DOWNLOADED_THEMES_DIR = 'themes'
DOWNLOADED_THEMES_ZIP = f'{DOWNLOADED_THEMES_DIR}_v6.zip'

""" Стили """

BG = '#E0E0E0'
BG_BTN = '#EEEEEE'
BG_ENTRY = '#F0F0F0'
BG_RES = '#CDCDCD'
FG = '#000000'

""" Функции и классы """


# Вывести сообщение с предупреждением
def warning(window_parent, msg: str):
    PopupMsgW(window_parent, msg, title='Warning').open()


# Всплывающее окно с сообщением
class PopupMsgW(tk.Toplevel):
    def __init__(self, parent, msg: str, btn_text='Ясно', title=PROGRAM_NAME):
        super().__init__(parent)
        self.title(title)
        self.config(bg=BG)

        self.closed = True  # Закрыто ли окно крестиком

        self.lbl_msg = tk.Label(self, text=msg, justify='center', bg=BG, fg=FG)
        self.btn_ok = tk.Button(self, text=btn_text, command=self.ok, takefocus=False, bg=BG_BTN, fg=FG)

        self.lbl_msg.grid(row=0, column=0, padx=6, pady=4)
        self.btn_ok.grid( row=1, column=0, padx=6, pady=4)

    # Нажатие на кнопку
    def ok(self):
        self.closed = False
        self.destroy()

    # Установить фокус
    def set_focus(self):
        self.focus_set()
        self.bind('<Return>', lambda event=None: self.btn_ok.invoke())
        self.bind('<Escape>', lambda event=None: self.destroy())

    def open(self):
        self.set_focus()

        self.grab_set()
        self.wait_window()

        return self.closed


# Главное окно
class InstallW(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f'{PROGRAM_NAME} [{PROGRAM_VERSION}] - Установщик')
        self.eval('tk::PlaceWindow . center')
        self.resizable(width=False, height=False)
        self.config(bg=BG)

        self.var_path = tk.StringVar(value=MAIN_PATH)
        self.var_dir = tk.StringVar(value=REPOSITORY_NAME)

        self.st = ttk.Style()
        self.st.configure(style='Std.TCheckbutton', background=BG, foreground=FG)

        self.frame_main = tk.Frame(self, relief='solid', bd=1, bg=BG)
        # {
        self.frame_path = tk.Frame(self.frame_main, bd=0, bg=BG)
        # { {
        self.lbl_path = tk.Label(self.frame_path, text='Путь для установки программы:', justify='center', bg=BG, fg=FG)
        self.entry_path = tk.Entry(self.frame_path, textvariable=self.var_path, state='readonly', width=70, bg=BG_ENTRY,
                                   fg=FG)
        self.btn_path = tk.Button(self.frame_path, text='Выбрать', command=self.choose_path, bg=BG_BTN, fg=FG)
        # } }
        self.frame_dir = tk.Frame(self.frame_main, bd=0, bg=BG)
        # { {
        self.lbl_dir = tk.Label(self.frame_dir, text='Название папки с программой:', justify='center', bg=BG, fg=FG)
        self.entry_dir = tk.Entry(self.frame_dir, textvariable=self.var_dir, state='normal', width=40, bg=BG_ENTRY,
                                  fg=FG, validate='key')
        # } }
        self.lbl_res = tk.Label(self.frame_main, text=f'Результирующий путь:\n'
                                                      f'{os.path.join(self.var_path.get(), self.var_dir.get())}',
                                justify='left', bg=BG_RES, fg=FG)
        # }
        self.btn_download_and_install = tk.Button(self, text='Установить', command=self.download_and_install,
                                                  bg=BG_BTN, fg=FG)

        self.frame_main.grid(row=0, column=0, padx=10, pady=(10, 0))
        # {
        self.frame_path.grid(row=0, column=0, padx=10, pady=(10, 0), sticky='W')
        # { {
        self.lbl_path.grid(  row=0, column=0, padx=0,      pady=0)
        self.entry_path.grid(row=1, column=0, padx=(0, 3), pady=0)
        self.btn_path.grid(  row=1, column=1, padx=0,      pady=0)
        # } }
        self.frame_dir.grid(row=1, column=0, padx=10, pady=(10, 0), sticky='W')
        # { {
        self.lbl_dir.grid(  row=2, column=0, padx=0, pady=0, sticky='E')
        self.entry_dir.grid(row=2, column=1, padx=0, pady=0, sticky='W')
        # } }
        self.lbl_res.grid(row=2, column=0, padx=10, pady=10, ipadx=5, sticky='W')
        # }
        self.btn_download_and_install.grid(row=1, column=0, padx=10, pady=10)

        self.vcmd = (self.register(self.validate_dir), '%P')
        self.entry_dir.configure(validatecommand=self.vcmd)

        self.set_focus()

    # Выбрать папку для установки
    def choose_path(self):
        self.var_path.set(filedialog.askdirectory())
        self.refresh_path()

    # Обновить результирующий путь при выборе пути
    def refresh_path(self):
        self.validate_dir(self.var_dir.get())

    # Обновить результирующий путь при выборе папки
    def validate_dir(self, value: str):
        res = f'{self.var_path.get()}\\{value}'.replace('/', '\\')
        self.lbl_res.configure(text=f'Результирующий путь:\n'
                                    f'{res}')
        return True

    # Скачать и установить обновление
    def download_and_install(self):
        root_path = self.var_path.get()
        program_dir = self.var_dir.get()
        if program_dir in os.listdir(root_path):
            warning(self, 'Папка с таким названием уже существует!')
            return
        program_path = os.path.join(root_path, program_dir)  # Папка с программой
        resources_path = os.path.join(program_path, RESOURCES_DIR)  # Папка с ресурсами
        additional_themes_path = os.path.join(resources_path, ADDITIONAL_THEMES_DIR)  # Папка с дополнительными темами
        downloaded_program_path = os.path.join(program_path, DOWNLOADED_PROGRAM_DIR)  # Временная папка с обновлением
        downloaded_program_zip_path = os.path.join(program_path, DOWNLOADED_PROGRAM_ZIP)  # Архив с обновлением
        downloaded_themes_path = os.path.join(program_path, DOWNLOADED_THEMES_DIR)  # Временная папка с темами
        downloaded_themes_zip_path = os.path.join(program_path, DOWNLOADED_THEMES_ZIP)  # Архив с темами

        os.mkdir(program_path)
        # Загрузка
        try:
            # Загружаем архивы обновления
            print('Загрузка архивов...', end='')
            wget.download(URL_DOWNLOAD_ZIP, out=program_path)
            wget.download(URL_DOWNLOAD_THEMES_ZIP, out=program_path)
        except Exception as exc:
            print(f'\nНе удалось скачать программу!\n'
                  f'{exc}')
            warning(self, f'Не удалось скачать программу!\n'
                          f'{exc}')
            return
        # Установка
        try:
            # Распаковываем архивы во временные папки
            print('\nРаспаковка архивов...')
            with zipfile.ZipFile(downloaded_program_zip_path, 'r') as zip_file:
                zip_file.extractall(program_path)
            with zipfile.ZipFile(downloaded_themes_zip_path, 'r') as zip_file:
                zip_file.extractall(program_path)
            # Удаляем архивы
            print('Удаление архивов...')
            os.remove(downloaded_program_zip_path)
            os.remove(downloaded_themes_zip_path)
            # Из временной папки достаём файлы новой версии
            print('Установка новых файлов...')
            shutil.copytree(os.path.join(downloaded_program_path, RESOURCES_DIR),
                            os.path.join(program_path, RESOURCES_DIR))
            shutil.copytree(downloaded_themes_path, additional_themes_path)
            for filename in ['aneno_dct.py', 'aneno_constants.py', 'aneno_upgrades.py', 'main.py']:
                os.replace(os.path.join(downloaded_program_path, filename),
                           os.path.join(program_path, filename))
            # Удаляем временные папки
            print('Удаление временных папок...')
            shutil.rmtree(downloaded_program_path)
            shutil.rmtree(downloaded_themes_path)
        except Exception as exc:
            print(f'Не удалось установить программу!\n'
                  f'{exc}')
            warning(self, f'Не удалось установить программу!\n'
                          f'{exc}')
            return
        else:
            print('Готово!')
            PopupMsgW(self, 'Программа успешно установлена!').open()
            exit(777)

    # Установить фокус
    def set_focus(self):
        self.focus_set()
        self.entry_dir.focus_set()

        self.bind('<Return>', lambda event=None: self.btn_download_and_install.invoke())


""" Выполнение программы """

try:
    PROGRAM_VERSION = requests.get(URL_LAST_VERSION, verify=False).text
except:
    PROGRAM_VERSION = 'v7.x.x'
InstallW().mainloop()
