import math
from aneno_constants import CATEGORY_SEPARATOR


# Вычислить ширину моноширинного поля, в которое должно помещаться каждое из данных значений
def width(values: tuple[str, ...] | list[str], min_width: int, max_width: int):
    assert min_width >= 0
    assert max_width >= 0
    assert max_width >= min_width

    max_len_of_vals = max(len(val) for val in values)
    return min(max(max_len_of_vals, min_width), max_width)


# Вычислить количество строк, необходимых для записи данного текста
# в многострочное текстовое поле при данной длине строки
def height(text: str, len_str: int):
    assert len_str > 0

    segments = text.split('\n')
    return sum(math.ceil(len(segment) / len_str) for segment in segments)


# Разделить строку на слова
def split_line(line: str) -> list[str, str]:
    len_line = len(line)
    res = []

    i = 0
    while i < len_line and not line[i].isalnum():
        i += 1
    if i != 0:
        res += [['', line[0:i]]]

    while i < len_line:
        word = ''
        separator = ''
        while i < len_line and line[i].isalnum():
            word += line[i]
            i += 1
        while i < len_line and not line[i].isalnum():
            separator += line[i]
            i += 1
        res += [[word, separator]]

    return res


# Разделить текст на части, длина которых не превышает заданное значение
def split_text(text: str, max_str_len: int, tab: int = 0, add_right_spaces: bool = True):
    assert max_str_len > 0
    assert tab >= 0
    assert tab < max_str_len

    res = ''
    lines = text.split('\n')  # Строки
    count_lines = len(lines)  # Количество строк
    for i in range(count_lines):
        line = lines[i]
        len_line = len(line)
        # Если ширина строки соответствует требованиям, то просто записываем эту строку
        if len_line <= max_str_len:
            res += line
            # Если нужно, дополняем строку пробелами до максимальной длины
            if add_right_spaces:
                res += ' ' * (max_str_len - len_line)
        else:
            current_len = 0
            tabulate = False
            words = split_line(line)
            for (word, separator) in words:
                len_word = len(word)
                len_separator = len(separator)

                # Если слово превышает максимальную длину строки, то разбиваем его на части
                if len_word > max_str_len or (tabulate and tab + len_word > max_str_len):
                    tmp = max_str_len - current_len
                    res += word[0:tmp]
                    res += ''.join(['\n' + ' ' * tab + word[i:i+max_str_len-tab]
                                    for i in range(tmp, len_word, max_str_len-tab)])
                    current_len = tab + (len_word - tmp) % (max_str_len - tab)
                    tabulate = True
                # Если слово не вмещается в данную строку, но может вместиться в следующую,
                # то записываем его в следующую
                elif len_word + current_len > max_str_len:
                    # Если нужно, дополняем строку пробелами до максимальной длины
                    if add_right_spaces:
                        res += ' ' * (max_str_len - current_len)
                    res += '\n'
                    res += ' ' * tab
                    res += word
                    current_len = tab + len_word
                    tabulate = True
                # Если слово вмещается в данную строку, то просто записываем его
                else:
                    res += word
                    current_len += len_word

                # Если разделитель целиком не вмещается в данную строку, то разделяем его на части
                if current_len + len_separator > max_str_len:
                    tmp = max_str_len - current_len
                    res += separator[0:tmp]
                    res += ''.join(['\n' + ' ' * tab + separator[i:i+max_str_len-tab]
                                    for i in range(tmp, len_separator, max_str_len-tab)])
                    current_len = tab + (len_separator - tmp) % (max_str_len - tab)
                    tabulate = True
                # Если разделитель вмещается в данную строку целиком, то просто записываем его
                else:
                    res += separator
                    current_len += len_separator
            # Если нужно, дополняем строку пробелами до максимальной длины
            if add_right_spaces:
                res += ' ' * (max_str_len - current_len)
        # Если строка не последняя, то добавляем перенос строки
        if i != count_lines - 1:
            res += '\n'
    return res


# Конкатенация строк
def arr_to_str(arr: list[str] | tuple[str, ...]):
    res = ''
    for frag in arr:
        res += frag
    return res


# Преобразовать кортеж в читаемый вид (для вывода на экран)
def tpl(input_tuple: tuple | list):
    res = ''
    is_first = True
    for i in range(len(input_tuple)):
        if input_tuple[i] != '':
            if is_first:  # Перед первым элементом не ставится запятая
                res += f'{input_tuple[i]}'
                is_first = False
            else:  # Перед последующими элементами ставится запятая
                res += f', {input_tuple[i]}'
    return res


# Преобразовать кортеж в строку (для сохранения значений категории в файл локальных настроек)
def decode_tpl(input_tuple: tuple | list, separator=CATEGORY_SEPARATOR):
    if not input_tuple:  # input_tuple == () или input_tuple == ('')
        return ''
    res = input_tuple[0]
    for i in range(1, len(input_tuple)):
        res += f'{separator}{input_tuple[i]}'
    return res


# Преобразовать строку в кортеж (для чтения значений категории из файла локальных настроек)
def encode_tpl(line: str):
    return tuple(line.split(CATEGORY_SEPARATOR))


# Перевести слово в ключ для словаря
def wrd_to_key(wrd: str, num: int):  # При изменении этой функции, не забыть поменять key_to_wrd
    return wrd, num


# Перевести ключ для словаря в слово
def key_to_wrd(key: tuple[str, int]):  # При изменении этой функции, не забыть поменять wrd_to_key
    return key[0]


# Выбрать окончание слова в зависимости от количественного числительного
def set_postfix(n: int, wrd_forms: tuple[str, str, str]):
    if 5 <= (n % 100) <= 20:
        return wrd_forms[2]  # Пример: 5 яблок
    elif n % 10 == 1:
        return wrd_forms[0]  # Пример: 1 яблоко
    elif 1 < n % 10 < 5:
        return wrd_forms[1]  # Пример: 2 яблока
    else:
        return wrd_forms[2]  # Пример: 0 яблок
