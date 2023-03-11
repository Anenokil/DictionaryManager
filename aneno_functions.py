from aneno_constants import CATEGORY_SEPARATOR


# Преобразовать кортеж в строку (для сохранения значений категории в файл локальных настроек)
def frm_key_to_str_for_save(input_tuple: tuple | list, separator=CATEGORY_SEPARATOR):
    if not input_tuple:  # input_tuple == () или input_tuple == ('')
        return ''
    res = input_tuple[0]
    for i in range(1, len(input_tuple)):
        res += f'{separator}{input_tuple[i]}'
    return res


# Преобразовать строку в кортеж (для чтения значений категории из файла локальных настроек)
def read_frm_key(line: str):
    return tuple(line.split(CATEGORY_SEPARATOR))
