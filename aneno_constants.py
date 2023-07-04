import os

""" Информация о программе """

PROGRAM_NAME = 'Dictionary Manager'
PROGRAM_VERSION = 'v7.1.35'
PROGRAM_DATE = '4.7.2023'
PROGRAM_TIME = '14:20 (UTC+3)'

""" Версии ресурсов """

SAVES_VERSION = 8  # Актуальная версия сохранений словарей
LOCAL_SETTINGS_VERSION = 8  # Актуальная версия локальных настроек
LOCAL_AUTO_SETTINGS_VERSION = 4  # Актуальная версия автосохраняемых локальных настроек
GLOBAL_SETTINGS_VERSION = 3  # Актуальная версия глобальных настроек
REQUIRED_THEME_VERSION = 7  # Актуальная версия тем

""" Варианты для Combobox`ов """

LEARN_VALUES_METHOD = ('Угадывать слово по переводу', 'Угадывать перевод по слову',
                       'Угадывать фразу по переводу', 'Угадывать перевод по фразе',
                       'Der-Die-Das (для немецкого)')  # Варианты метода учёбы
LEARN_VALUES_WORDS = ('Все', 'Больше избранных (рекоменд.)', 'Только избранные', 'Только неотвеченные',
                      '10 случайных', '10 случайных из избранных')  # Варианты подбора слов для учёбы
LEARN_VALUES_FORMS = ('Только начальная форма', 'По одной случайной словоформе', 'Все формы, кроме начальной',
                      'Все словоформы')  # Варианты подбора словоформ
LEARN_VALUES_ORDER = ('Случайный порядок', 'В первую очередь сложные')  # Варианты порядка следования слов при учёбе
PRINT_VALUES_ORDER = ('Сначала старые', 'Сначала новые',
                      'Сначала сложные', 'Сначала простые',
                      'Сначала сложные (2)', 'Сначала простые (2)',
                      'Сначала давно отвеченные', 'Сначала недавно отвеченные',
                      'По алфавиту', 'По алфавиту (обр.)',
                      'Сначала короткие', 'Сначала длинные')  # Варианты сортировки статей

""" Масштаб """

SCALE_MIN = 8
SCALE_MAX = 16
SCALE_DEF = 10

SCALE_DEFAULT_FRAME_WIDTH      = (532, 604, 682, 757, 757, 832, 907, 980, 1057)
SCALE_DEFAULT_FRAME_HEIGHT     = (400, 430, 460, 490, 520, 550, 580, 610,  640)
SCALE_SMALL_FRAME_WIDTH        = (250, 284, 318, 353, 354, 390, 424, 460,  495)
SCALE_SMALL_FRAME_HEIGHT_SHORT = (120, 130, 140, 150, 160, 170, 180, 190,  200)
SCALE_SMALL_FRAME_HEIGHT_TALL  = (220, 230, 240, 250, 260, 270, 280, 290,  300)
SCALE_FRAME_HEIGHT_ONE_LINE    = ( 21,  23,  24,  26,  28,  29,  31,  33,   34)
SCALE_CUSTOM_THEME_FRAME_WIDTH = (410, 440, 455, 495, 517, 543, 590, 615,  643)
SCALE_CUSTOM_THEME_COMBO_WIDTH = ( 16,  16,  14,  12,  11,  11,  10,   9,    8)

""" Пути, файлы, ссылки """

MAIN_PATH = os.path.dirname(__file__)  # Папка с программой
RESOURCES_DIR = 'resources'  # Папка с ресурсами
RESOURCES_PATH = os.path.join(MAIN_PATH, RESOURCES_DIR)
SAVES_DIR = 'saves'  # Папка с сохранениями
SAVES_PATH = os.path.join(RESOURCES_PATH, SAVES_DIR)
# {
DICTIONARY_SAVE_FN = 'dct.txt'  # Файл с сохранением словаря
LOCAL_SETTINGS_FN = 'local_settings.txt'  # Файл с локальными настройками (настройки словаря)
LOCAL_AUTO_SETTINGS_FN = 'local_settings_auto.txt'  # Файл с автоматически сохраняющимися, локальными настройками
# }
GLOBAL_SETTINGS_FN = 'global_settings.txt'  # Файл с глобальными настройками (настройки программы)
GLOBAL_SETTINGS_PATH = os.path.join(RESOURCES_PATH, GLOBAL_SETTINGS_FN)
ADDITIONAL_THEMES_DIR = 'themes'  # Папка с дополнительными темами
ADDITIONAL_THEMES_PATH = os.path.join(RESOURCES_PATH, ADDITIONAL_THEMES_DIR)
CUSTOM_THEME_DIR = 'custom_theme'  # Папка с пользовательской темой
CUSTOM_THEME_PATH = os.path.join(RESOURCES_PATH, CUSTOM_THEME_DIR)
IMAGES_DIR = 'images'  # Папка с изображениями
IMAGES_PATH = os.path.join(RESOURCES_PATH, IMAGES_DIR)
TMP_FN = 'tmp.txt'  # Временный файл (для обновления словарей)
TMP_PATH = os.path.join(RESOURCES_PATH, TMP_FN)
ICON_FN = 'icon.png'  # Файл с изображением иконки
ICON_PATH = os.path.join(RESOURCES_PATH, ICON_FN)

# Изображения
IMG_NAMES = ['about_typo', 'about',
             'ok', 'cancel',
             'fav', 'unfav', 'add_to_group', 'remove_from_group',
             'edit', 'add', 'delete',
             'select_page', 'unselect_page', 'select_all', 'unselect_all',
             'print_out',
             'redo', 'undo',
             'arrow_left', 'arrow_right', 'double_arrow_left', 'double_arrow_right',
             'trashcan']
ICON_NAMES = IMG_NAMES[1:]

img_about_typo = os.path.join(IMAGES_PATH, 'about_typo.png')
img_about = os.path.join(IMAGES_PATH, 'about.png')
#
img_ok = os.path.join(IMAGES_PATH, 'ok.png')
img_cancel = os.path.join(IMAGES_PATH, 'cancel.png')
#
img_add = os.path.join(IMAGES_PATH, 'add.png')
img_delete = os.path.join(IMAGES_PATH, 'delete.png')
img_edit = os.path.join(IMAGES_PATH, 'edit.png')
#
img_print_out = os.path.join(IMAGES_PATH, 'print_out.png')
#
img_select_page = os.path.join(IMAGES_PATH, 'select_page.png')
img_unselect_page = os.path.join(IMAGES_PATH, 'unselect_page.png')
img_select_all = os.path.join(IMAGES_PATH, 'select_all.png')
img_unselect_all = os.path.join(IMAGES_PATH, 'unselect_all.png')
#
img_fav = os.path.join(IMAGES_PATH, 'fav.png')
img_unfav = os.path.join(IMAGES_PATH, 'unfav.png')
img_add_to_group = os.path.join(IMAGES_PATH, 'add_to_group.png')
img_remove_from_group = os.path.join(IMAGES_PATH, 'remove_from_group.png')
#
img_undo = os.path.join(IMAGES_PATH, 'undo.png')
img_redo = os.path.join(IMAGES_PATH, 'redo.png')
#
img_arrow_left = os.path.join(IMAGES_PATH, 'arrow_left.png')
img_arrow_right = os.path.join(IMAGES_PATH, 'arrow_right.png')
img_double_arrow_left = os.path.join(IMAGES_PATH, 'double_arrow_left.png')
img_double_arrow_right = os.path.join(IMAGES_PATH, 'double_arrow_right.png')
#
img_trashcan = os.path.join(IMAGES_PATH, 'trashcan.png')

# Название репозитория на GitHub
REPOSITORY_NAME = 'DictionaryManager'

# Ссылка на репозиторий программы на GitHub
URL_GITHUB = f'https://github.com/Anenokil/{REPOSITORY_NAME}'
# Ссылка на релизы программы
URL_RELEASES = f'https://github.com/Anenokil/{REPOSITORY_NAME}/releases'
# Ссылка на файл с названием последней версии
URL_LAST_VERSION = f'https://raw.githubusercontent.com/Anenokil/{REPOSITORY_NAME}/master/ver'
# Ссылка на файл со списком обновляемых файлов
URL_UPDATE_FILES = f'https://raw.githubusercontent.com/Anenokil/{REPOSITORY_NAME}/master/update_files'
# Ссылка для установки последней версии
URL_DOWNLOAD_ZIP = f'https://github.com/Anenokil/{REPOSITORY_NAME}/archive/refs/heads/master.zip'

# Папки и файлы для установки обновлений
NEW_VERSION_DIR = f'{REPOSITORY_NAME}-master'
NEW_VERSION_PATH = os.path.join(MAIN_PATH, NEW_VERSION_DIR)  # Временная папка с обновлением
NEW_VERSION_ZIP = f'{NEW_VERSION_DIR}.zip'
NEW_VERSION_ZIP_PATH = os.path.join(MAIN_PATH, NEW_VERSION_ZIP)  # Архив с обновлением

""" Шаблоны сохранений """

# Шаблон файла локальных настроек
DEFAULT_LOCAL_SETTINGS_FILE = f'v{LOCAL_SETTINGS_VERSION}\n' \
                              f'1\n' \
                              f':aä:AÄ:oö:OÖ:uü:UÜ^sß^Sẞ\n' \
                              f'5\n' \
                              f'Число\n' \
                              f'2\nед.ч.\nмн.ч.\n' \
                              f'Род\n' \
                              f'3\nм.р.\nж.р.\nср.р.\n' \
                              f'Падеж\n' \
                              f'4\nим.п.\nрод.п.\nдат.п.\nвин.п.\n' \
                              f'Лицо\n' \
                              f'3\n1 л.\n2 л.\n3 л.\n' \
                              f'Время\n' \
                              f'3\nпр.вр.\nн.вр.\nбуд.вр.\n' \
                              f'0'

# Шаблон файла локальных авто-настроек
DEFAULT_LOCAL_AUTO_SETTINGS_FILE = f'v{LOCAL_AUTO_SETTINGS_VERSION}\n' \
                                   f'0\n' \
                                   f'0 0 1 1 0 0\n' \
                                   f'0 0 1 1 1'

""" Другие константы """

# Показать все группы
ALL_GROUPS = 'Все'
# Открывающие символы специальных комбинаций
SPECIAL_COMBINATIONS_OPENING_SYMBOLS = ('^', '~', '`', '\'', '"', '*', '_', ':',
                                        '/', '\\', '|', '#', '$', '%', '&', '@', '§')
