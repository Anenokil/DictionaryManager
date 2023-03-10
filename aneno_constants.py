import os

""" Информация о программе """

PROGRAM_NAME = 'Dictionary Manager'
PROGRAM_VERSION = 'v7.1.8'
PROGRAM_DATE = '13.3.2023'
PROGRAM_TIME = '19:54 (UTC+3)'

""" Версии ресурсов """

SAVES_VERSION = 5  # Актуальная версия сохранений словарей
LOCAL_SETTINGS_VERSION = 4  # Актуальная версия локальных настроек
LOCAL_AUTO_SETTINGS_VERSION = 3  # Актуальная версия автосохраняемых локальных настроек
GLOBAL_SETTINGS_VERSION = 3  # Актуальная версия глобальных настроек
REQUIRED_THEME_VERSION = 6  # Актуальная версия тем

""" Варианты для Combobox`ов """

LEARN_VALUES_METHOD = ('Угадывать слово по переводу', 'Угадывать перевод по слову',
                       'Der-Die-Das (для немецкого)')  # Варианты метода учёбы
LEARN_VALUES_WORDS = ('Все', 'Больше избранных (рекоменд.)', 'Только избранные', 'Только неотвеченные',
                      '15 случайных', '15 случайных из избранных')  # Варианты подбора слов для учёбы
LEARN_VALUES_FORMS = ('Только начальная форма', 'По одной случайной словоформе', 'Все формы, кроме начальной',
                      'Все словоформы')  # Варианты подбора словоформ
LEARN_VALUES_ORDER = ('Случайный порядок', 'В первую очередь сложные')  # Варианты порядка следования слов при учёбе
PRINT_VALUES_ORDER = ('Сначала старые', 'Сначала новые', 'Сначала сложные', 'Сначала простые',
                      'Сначала давно отвеченные',
                      'Сначала недавно отвеченные')  # Варианты порядка следования слов при учёбе

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
IMG_NAMES = ['about_mgsp', 'about_typo', 'about',
             'ok', 'cancel',
             'add', 'delete', 'edit',
             'print_out',
             'undo', 'redo',
             'arrow_left', 'arrow_right', 'double_arrow_left', 'double_arrow_right']
ICON_NAMES = IMG_NAMES[2:]

img_about_mgsp = os.path.join(IMAGES_PATH, 'about_mgsp.png')
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
img_undo = os.path.join(IMAGES_PATH, 'undo.png')
img_redo = os.path.join(IMAGES_PATH, 'redo.png')
#
img_arrow_left = os.path.join(IMAGES_PATH, 'arrow_left.png')
img_arrow_right = os.path.join(IMAGES_PATH, 'arrow_right.png')
img_double_arrow_left = os.path.join(IMAGES_PATH, 'double_arrow_left.png')
img_double_arrow_right = os.path.join(IMAGES_PATH, 'double_arrow_right.png')

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

""" Другие константы """

# Разделитель для записи значений категории в файл локальных настроек
CATEGORY_SEPARATOR = '@'
# Открывающие символы специальных комбинаций
SPECIAL_COMBINATIONS_OPENING_SYMBOLS = ('^', '~', '`', '\'', '"', '*', '_', ':', '/', '\\', '|', '#', '$', '%', '&')
