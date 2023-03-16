import os
import shutil
import aneno_constants as anc
from aneno_dct import frm_key_to_str_for_save, read_frm_key

""" Обновление ресурсов """


# Обновить структуру папки с ресурсами
def upgrade_resources():
    old_local_settings_dir = 'local_settings'
    old_local_settings_path = os.path.join(anc.RESOURCES_PATH, old_local_settings_dir)
    # Удаляем лишние папки, если они есть
    for dir_or_filename in os.listdir(anc.SAVES_PATH):
        path = os.path.join(anc.SAVES_PATH, dir_or_filename)
        if os.path.isdir(path):
            shutil.rmtree(path)
    # Перемещаем файлы
    for filename in os.listdir(anc.SAVES_PATH):
        base_name, ext = os.path.splitext(filename)
        if ext == '.txt':
            dir_name = os.path.join(anc.SAVES_PATH, base_name)
            # Создаём папку сохранения
            os.mkdir(dir_name)
            # Перемещаем в неё файл с сохранением словаря
            os.replace(os.path.join(anc.SAVES_PATH, filename),
                       os.path.join(dir_name, anc.DICTIONARY_SAVE_FN))
            # Перемещаем в неё файл с локальными настройками
            if old_local_settings_dir in os.listdir(anc.RESOURCES_PATH):
                if filename in os.listdir(old_local_settings_path):
                    os.replace(os.path.join(old_local_settings_path, filename),
                               os.path.join(dir_name, anc.LOCAL_SETTINGS_FN))
    # Удаляем старую папку локальных настроек
    if old_local_settings_dir in os.listdir(anc.RESOURCES_PATH):
        shutil.rmtree(old_local_settings_path)


""" Обновления тем """


# Обновить тему с 4 до 6 версии
def upgrade_theme_4_to_6(filepath: str):
    with open(filepath, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write('5\n')
        for i in range(1, 11):
            file.write(lines[i])
        file.write(lines[10])
        file.write(lines[11])
        for i in range(13, 19):
            file.write(lines[i])
        file.write(lines[13])
        file.write(lines[14])
        for i in range(19, 30):
            file.write(lines[i])

    upgrade_theme_5_to_6(filepath)


# Обновить тему с 5 до 6 версии
def upgrade_theme_5_to_6(filepath: str):
    with open(filepath, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write('6\n')
        for i in range(1, 21):
            file.write(lines[i])
        file.write(lines[2])
        file.write(lines[1])
        file.write(lines[1])
        file.write(lines[3])
        file.write(lines[3])
        file.write(lines[3])
        for i in range(21, 32):
            file.write(lines[i])


# Обновить тему старой версии до актуальной версии
def upgrade_theme(filepath: str):
    with open(filepath, 'r', encoding='utf-8') as file:
        first_line = file.readline()
    if first_line[0] == '4':  # Версия 4
        upgrade_theme_4_to_6(filepath)
    elif first_line[0] == '5':  # Версия 5
        upgrade_theme_5_to_6(filepath)


""" Обновления глобальных настроек """


# Обновить глобальные настройки с 0 до 1 версии
def upgrade_global_settings_0_to_1():
    with open(anc.GLOBAL_SETTINGS_PATH, 'r', encoding='utf-8') as global_settings_file:
        lines = global_settings_file.readlines()
    with open(anc.GLOBAL_SETTINGS_PATH, 'w', encoding='utf-8') as global_settings_file:
        global_settings_file.write('v1\n')  # Версия глобальных настроек
        global_settings_file.write(lines[0])  # Название текущего словаря
        global_settings_file.write(lines[1])  # Уведомлять ли о выходе новых версий
        global_settings_file.write('0\n')  # Добавлять ли кнопку "Опечатка" при неверном ответе в учёбе
        global_settings_file.write(lines[2])  # Установленная тема


# Обновить глобальные настройки с 1 до 2 версии
def upgrade_global_settings_1_to_2():
    with open(anc.GLOBAL_SETTINGS_PATH, 'r', encoding='utf-8') as global_settings_file:
        lines = global_settings_file.readlines()
    with open(anc.GLOBAL_SETTINGS_PATH, 'w', encoding='utf-8') as global_settings_file:
        global_settings_file.write('v2\n')  # Версия глобальных настроек
        global_settings_file.write(lines[1])  # Название текущего словаря
        global_settings_file.write(lines[2])  # Уведомлять ли о выходе новых версий
        global_settings_file.write(lines[3])  # Добавлять ли кнопку "Опечатка" при неверном ответе в учёбе
        global_settings_file.write(lines[4].strip())  # Установленная тема
        global_settings_file.write('\n10')  # Размер шрифта


# Обновить глобальные настройки с 2 до 3 версии
def upgrade_global_settings_2_to_3():
    with open(anc.GLOBAL_SETTINGS_PATH, 'r', encoding='utf-8') as global_settings_file:
        lines = global_settings_file.readlines()
    with open(anc.GLOBAL_SETTINGS_PATH, 'w', encoding='utf-8') as global_settings_file:
        global_settings_file.write('v3\n')  # Версия глобальных настроек
        global_settings_file.write('UPGRADE_REQUIRED\n')  # Версия глобальных настроек
        for i in range(1, 6):
            global_settings_file.write(lines[i])


upgrade_global_settings_functions = [upgrade_global_settings_0_to_1,
                                     upgrade_global_settings_1_to_2,
                                     upgrade_global_settings_2_to_3]


# Обновить глобальные настройки старой версии до актуальной версии
def upgrade_global_settings():
    with open(anc.GLOBAL_SETTINGS_PATH, 'r', encoding='utf-8') as global_settings_file:
        lines = global_settings_file.readlines()
    first_line = lines[0].strip()
    if len(lines) == 3:
        current_version = 0
    elif len(first_line) == 2 and first_line[0] == 'v' and first_line[1].isnumeric() and\
         int(first_line[1]) <= anc.GLOBAL_SETTINGS_VERSION:
        current_version = int(first_line[1])
    else:
        print(f'Неизвестная версия глобальных настроек: {first_line}!\n'
              f'Проверьте наличие обновлений программы')
        return
    for i in range(current_version, anc.GLOBAL_SETTINGS_VERSION):
        upgrade_global_settings_functions[i]()


""" Обновления локальных настроек """


# Обновить локальные настройки с 0 до 1 версии
def upgrade_local_settings_0_to_1(local_settings_path: str, _=None):
    with open(local_settings_path, 'r', encoding='utf-8') as local_settings_file:
        lines = local_settings_file.readlines()
    with open(local_settings_path, 'w', encoding='utf-8') as local_settings_file:
        local_settings_file.write('v1\n')
        local_settings_file.write(lines[0])
        local_settings_file.write('\n')
        for i in range(1, len(lines)):
            local_settings_file.write(lines[i])


# Обновить локальные настройки с 1 до 2 версии
def upgrade_local_settings_1_to_2(local_settings_path: str, encode_special_combinations):
    with open(local_settings_path, 'r', encoding='utf-8') as local_settings_file:
        lines = local_settings_file.readlines()
    with open(local_settings_path, 'w', encoding='utf-8') as local_settings_file:
        local_settings_file.write('v2\n')
        local_settings_file.write(lines[1])
        local_settings_file.write(lines[2])
        for i in range(3, len(lines)):
            if i % 2 == 1:
                local_settings_file.write(encode_special_combinations(lines[i]))
            else:
                values = lines[i].strip().split(anc.CATEGORY_SEPARATOR)
                values = [encode_special_combinations(i) for i in values]
                local_settings_file.write(frm_key_to_str_for_save(values, anc.CATEGORY_SEPARATOR) + '\n')


# Обновить локальные настройки со 2 до 3 версии
def upgrade_local_settings_2_to_3(local_settings_path: str, _=None):
    with open(local_settings_path, 'r', encoding='utf-8') as local_settings_file:
        lines = local_settings_file.readlines()
    with open(local_settings_path, 'w', encoding='utf-8') as local_settings_file:
        local_settings_file.write('v3\n')
        local_settings_file.write(lines[1])
        local_settings_file.write(lines[2])
        local_settings_file.write('1\n')
        for i in range(3, len(lines)):
            local_settings_file.write(lines[i])


# Обновить локальные настройки со 3 до 4 версии
def upgrade_local_settings_3_to_4(local_settings_path: str, _=None):
    with open(local_settings_path, 'r', encoding='utf-8') as local_settings_file:
        lines = local_settings_file.readlines()
    with open(local_settings_path, 'w', encoding='utf-8') as local_settings_file:
        local_settings_file.write('v4\n')
        local_settings_file.write(lines[1])
        line = lines[2].strip()
        if line != '':
            line = '#' + '#'.join(line[i:i+2] for i in range(0, len(line), 2))
        local_settings_file.write(f'{line}\n')
        local_settings_file.write(lines[3])
        for i in range(4, len(lines)):
            local_settings_file.write(lines[i])


upgrade_local_settings_functions = [upgrade_local_settings_0_to_1,
                                    upgrade_local_settings_1_to_2,
                                    upgrade_local_settings_2_to_3,
                                    upgrade_local_settings_3_to_4]


# Обновить локальные настройки старой версии до актуальной версии
def upgrade_local_settings(local_settings_path: str, encode_special_combinations):
    with open(local_settings_path, 'r', encoding='utf-8') as local_settings_file:
        first_line = local_settings_file.readline()
    if first_line == '':  # Если сохранение пустое
        return
    line = first_line.strip()
    if first_line[0] != 'v':
        current_version = 0
    elif len(line) == 2 and line[0] == 'v' and line[1].isnumeric() and int(line[1]) <= anc.LOCAL_SETTINGS_VERSION:
        current_version = int(line[1])
    else:
        print(f'Неизвестная версия локальных настроек: {line}!\n'
              f'Проверьте наличие обновлений программы')
        return
    for i in range(current_version, anc.LOCAL_SETTINGS_VERSION):
        upgrade_local_settings_functions[i](local_settings_path, encode_special_combinations)


""" Обновления локальных авто-настроек """


# Обновить локальные авто-настройки с 1 до 2 версии
def upgrade_local_auto_settings_1_to_2(local_auto_settings_path: str):
    with open(local_auto_settings_path, 'r', encoding='utf-8') as local_auto_settings_file:
        lines = local_auto_settings_file.readlines()
    with open(local_auto_settings_path, 'w', encoding='utf-8') as local_auto_settings_file:
        local_auto_settings_file.write('v2\n')
        local_auto_settings_file.write('0\n')
        local_auto_settings_file.write(lines[1])


# Обновить локальные авто-настройки с 2 до 3 версии
def upgrade_local_auto_settings_2_to_3(local_auto_settings_path: str):
    with open(local_auto_settings_path, 'r', encoding='utf-8') as local_auto_settings_file:
        lines = local_auto_settings_file.readlines()
    with open(local_auto_settings_path, 'w', encoding='utf-8') as local_auto_settings_file:
        local_auto_settings_file.write('v3\n')
        local_auto_settings_file.write(lines[1])
        local_auto_settings_file.write('0 1 1 0 0\n')
        local_auto_settings_file.write(lines[2])


upgrade_local_auto_settings_functions = [upgrade_local_auto_settings_1_to_2,
                                         upgrade_local_auto_settings_2_to_3]


# Обновить локальные авто-настройки старой версии до актуальной версии
def upgrade_local_auto_settings(local_auto_settings_path: str):
    with open(local_auto_settings_path, 'r', encoding='utf-8') as local_auto_settings_file:
        first_line = local_auto_settings_file.readline()
    if first_line == '':  # Если сохранение пустое
        return
    line = first_line.strip()
    if len(line) == 2 and line[0] == 'v' and line[1].isnumeric() and\
       1 <= int(line[1]) <= anc.LOCAL_AUTO_SETTINGS_VERSION:
        current_version = int(line[1])
    else:
        print(f'Неизвестная версия локальных авто-настроек: {line}!\n'
              f'Проверьте наличие обновлений программы')
        return
    for i in range(current_version, anc.LOCAL_AUTO_SETTINGS_VERSION):
        upgrade_local_auto_settings_functions[i - 1](local_auto_settings_path)


""" Обновления словаря """


# Обновить сохранение словаря с 0 до 1 версии
def upgrade_dct_save_0_to_1(path: str, _=None):
    with open(path, 'r', encoding='utf-8') as dct_save:
        with open(anc.TMP_PATH, 'w', encoding='utf-8') as dct_save_tmp:
            dct_save_tmp.write('v1\n')
            while True:
                line = dct_save.readline()
                if not line:
                    break
                dct_save_tmp.write(line)
    with open(anc.TMP_PATH, 'r', encoding='utf-8') as dct_save_tmp:
        with open(path, 'w', encoding='utf-8') as dct_save:
            while True:
                line = dct_save_tmp.readline()
                if not line:
                    break
                dct_save.write(line)
    if anc.TMP_FN in os.listdir(anc.RESOURCES_PATH):
        os.remove(anc.TMP_PATH)


# Обновить сохранение словаря с 1 до 2 версии
def upgrade_dct_save_1_to_2(path: str, encode_special_combinations):
    with open(path, 'r', encoding='utf-8') as dct_save:
        with open(anc.TMP_PATH, 'w', encoding='utf-8') as dct_save_tmp:
            dct_save.readline()
            dct_save_tmp.write('v2\n')  # Версия сохранения словаря
            while True:
                line = dct_save.readline()
                if not line:
                    break
                elif line[0] == 'w':
                    dct_save_tmp.write(encode_special_combinations(line))
                    line = dct_save.readline()
                    dct_save_tmp.write(line.replace('#', ':'))
                    line = dct_save.readline()
                    dct_save_tmp.write(encode_special_combinations(line))
                elif line[0] == 't':
                    dct_save_tmp.write(encode_special_combinations(line))
                elif line[0] == 'd':
                    dct_save_tmp.write('n' + encode_special_combinations(line[1:]))
                elif line[0] == 'f':
                    old_frm_key = read_frm_key(line[1:], anc.CATEGORY_SEPARATOR)
                    new_frm_key = [encode_special_combinations(i) for i in old_frm_key]
                    dct_save_tmp.write('f' + frm_key_to_str_for_save(new_frm_key, anc.CATEGORY_SEPARATOR))
                    line = dct_save.readline()
                    dct_save_tmp.write(encode_special_combinations(line))
                elif line[0] == '*':
                    dct_save_tmp.write('*\n')
    with open(anc.TMP_PATH, 'r', encoding='utf-8') as dct_save_tmp:
        with open(path, 'w', encoding='utf-8') as dct_save:
            while True:
                line = dct_save_tmp.readline()
                if not line:
                    break
                dct_save.write(line)
    if anc.TMP_FN in os.listdir(anc.RESOURCES_PATH):
        os.remove(anc.TMP_PATH)


# Обновить сохранение словаря с 2 до 3 версии
def upgrade_dct_save_2_to_3(path: str, _=None):
    with open(path, 'r', encoding='utf-8') as dct_save:
        with open(anc.TMP_PATH, 'w', encoding='utf-8') as dct_save_tmp:
            dct_save.readline()
            dct_save_tmp.write('v3\n')  # Версия сохранения словаря
            while True:
                line = dct_save.readline()
                if not line:
                    break
                elif line[0] == 'w':
                    dct_save_tmp.write(line)
                    line = dct_save.readline()
                    a, b, c = line.strip().split(':')
                    if a == b:
                        dct_save_tmp.write(f'{a}:{b}:{b}\n')
                    elif c == '-1':
                        dct_save_tmp.write(f'{a}:{b}:0\n')
                    elif c == '0':
                        dct_save_tmp.write(f'{a}:{b}:1\n')
                    else:
                        dct_save_tmp.write(f'{a}:{b}:-{c}\n')
                    line = dct_save.readline()
                    dct_save_tmp.write(line)
                elif line[0] == 't':
                    dct_save_tmp.write(line)
                elif line[0] == 'n':
                    dct_save_tmp.write(line)
                elif line[0] == 'f':
                    dct_save_tmp.write(line)
                    line = dct_save.readline()
                    dct_save_tmp.write(line)
                elif line[0] == '*':
                    dct_save_tmp.write(line)
    with open(anc.TMP_PATH, 'r', encoding='utf-8') as dct_save_tmp:
        with open(path, 'w', encoding='utf-8') as dct_save:
            while True:
                line = dct_save_tmp.readline()
                if not line:
                    break
                dct_save.write(line)
    if anc.TMP_FN in os.listdir(anc.RESOURCES_PATH):
        os.remove(anc.TMP_PATH)


# Обновить сохранение словаря с 3 до 4 версии
def upgrade_dct_save_3_to_4(path: str, _=None):
    with open(path, 'r', encoding='utf-8') as dct_save:
        with open(anc.TMP_PATH, 'w', encoding='utf-8') as dct_save_tmp:
            dct_save.readline()
            dct_save_tmp.write('v4\n')  # Версия сохранения словаря
            while True:
                line = dct_save.readline()
                if not line:
                    break
                elif line[0] == 'w':
                    dct_save_tmp.write(line)
                    line = dct_save.readline()
                    dct_save_tmp.write(line)
                    dct_save_tmp.write('0\n')
                    line = dct_save.readline()
                    dct_save_tmp.write(line)
                elif line[0] == 't':
                    dct_save_tmp.write(line)
                elif line[0] == 'n':
                    dct_save_tmp.write(line)
                elif line[0] == 'f':
                    dct_save_tmp.write(line)
                    line = dct_save.readline()
                    dct_save_tmp.write(line)
                elif line[0] == '*':
                    dct_save_tmp.write(line)
    with open(anc.TMP_PATH, 'r', encoding='utf-8') as dct_save_tmp:
        with open(path, 'w', encoding='utf-8') as dct_save:
            while True:
                line = dct_save_tmp.readline()
                if not line:
                    break
                dct_save.write(line)
    if anc.TMP_FN in os.listdir(anc.RESOURCES_PATH):
        os.remove(anc.TMP_PATH)


# Обновить сохранение словаря с 4 до 5 версии
def upgrade_dct_save_4_to_5(path: str, _=None):
    with open(path, 'r', encoding='utf-8') as dct_save:
        with open(anc.TMP_PATH, 'w', encoding='utf-8') as dct_save_tmp:
            dct_save.readline()
            dct_save_tmp.write('v5\n')  # Версия сохранения словаря
            while True:
                line = dct_save.readline()
                if not line:
                    break
                elif line[0] == 'w':
                    dct_save_tmp.write(line)
                    line = dct_save.readline()
                    dct_save_tmp.write(line)
                    line = dct_save.readline()
                    dct_save_tmp.write(f'{line.strip()}:0:0\n')
                    line = dct_save.readline()
                    dct_save_tmp.write(line)
                elif line[0] == 't':
                    dct_save_tmp.write(line)
                elif line[0] == 'n':
                    dct_save_tmp.write(line)
                elif line[0] == 'f':
                    dct_save_tmp.write(line)
                    line = dct_save.readline()
                    dct_save_tmp.write(line)
                elif line[0] == '*':
                    dct_save_tmp.write(line)
    with open(anc.TMP_PATH, 'r', encoding='utf-8') as dct_save_tmp:
        with open(path, 'w', encoding='utf-8') as dct_save:
            while True:
                line = dct_save_tmp.readline()
                if not line:
                    break
                dct_save.write(line)
    if anc.TMP_FN in os.listdir(anc.RESOURCES_PATH):
        os.remove(anc.TMP_PATH)


# Обновить сохранение словаря с 5 до 6 версии
def upgrade_dct_save_5_to_6(path: str, _=None):
    with open(path, 'r', encoding='utf-8') as dct_save:
        with open(anc.TMP_PATH, 'w', encoding='utf-8') as dct_save_tmp:
            dct_save.readline()
            dct_save_tmp.write('v6\n')  # Версия сохранения словаря
            while True:
                line = dct_save.readline()
                if not line:
                    break
                elif line[0] == 'w':
                    dct_save_tmp.write(line)
                    line = dct_save.readline()
                    dct_save_tmp.write(line)
                    line = dct_save.readline()
                    dct_save_tmp.write(line)
                    line = dct_save.readline()
                    dct_save_tmp.write(line)
                elif line[0] == 't':
                    dct_save_tmp.write(line)
                elif line[0] == 'n':
                    dct_save_tmp.write(line)
                elif line[0] == 'f':
                    dct_save_tmp.write(line)
                    line = dct_save.readline()
                    dct_save_tmp.write(line)
                elif line[0] == '*':
                    dct_save_tmp.write('gИзбранное\n')
    with open(anc.TMP_PATH, 'r', encoding='utf-8') as dct_save_tmp:
        with open(path, 'w', encoding='utf-8') as dct_save:
            while True:
                line = dct_save_tmp.readline()
                if not line:
                    break
                dct_save.write(line)
    if anc.TMP_FN in os.listdir(anc.RESOURCES_PATH):
        os.remove(anc.TMP_PATH)


upgrade_dct_save_functions = [upgrade_dct_save_0_to_1,
                              upgrade_dct_save_1_to_2,
                              upgrade_dct_save_2_to_3,
                              upgrade_dct_save_3_to_4,
                              upgrade_dct_save_4_to_5,
                              upgrade_dct_save_5_to_6]


# Обновить сохранение словаря старой версии до актуальной версии
def upgrade_dct_save(dct_save_path: str, encode_special_combinations):
    with open(dct_save_path, 'r', encoding='utf-8') as dct_save:
        first_line = dct_save.readline()
    if first_line == '':  # Если сохранение пустое
        return
    line = first_line.strip()
    if first_line[0] == 'w':
        current_version = 0
    elif len(line) == 2 and line[0] == 'v' and line[1].isnumeric() and int(line[1]) <= anc.SAVES_VERSION:
        current_version = int(line[1])
    else:
        print(f'Неизвестная версия словаря: {line}!\n'
              f'Проверьте наличие обновлений программы')
        return
    for i in range(current_version, anc.SAVES_VERSION):
        upgrade_dct_save_functions[i](dct_save_path, encode_special_combinations)
