import random

SETTINGS_FN = 'settings.txt'

with open(SETTINGS_FN, 'r') as setF:
    filename = setF.readline().strip()


def code(str_):
    str_ = str_.replace('##', '1ä')
    str_ = str_.replace('#a', '2ä')

    str_ = str_.replace('#A', 'Ä')
    str_ = str_.replace('#o', 'ö')
    str_ = str_.replace('#O', 'Ö')
    str_ = str_.replace('#u', 'ü')
    str_ = str_.replace('#U', 'Ü')
    str_ = str_.replace('#s', 'ß')
    str_ = str_.replace('#S', 'ẞ')

    str_ = str_.replace('1ä', '#')
    str_ = str_.replace('2ä', 'ä')
    return str_


class Note(object):
    # self.wrd - слово
    # self.tr - список переводов
    # self.dsc - список доп. информации
    # self.count_t - количество переводов
    # self.count_d - количество записей с доп. информацией
    # self.fav - избранное
    # self.all_tries - количество всех попыток
    # self.correct_tries - количество удачных попыток
    # self.percent - процент удачных попыток
    # self.last_tries - количество последних неудачных попыток (-1 - значит ещё не было попыток)
    def __init__(self, wrd_, tr_, dsc_=None, fav_=False, all_tries_=0, correct_tries_=0, last_tries_=-1):
        self.wrd = wrd_
        self.forms = {}
        self.tr = tr_ if type(tr_) == list else [tr_]
        if dsc_ == None:
            self.dsc = []
        elif type(dsc_) == list:
            self.dsc = dsc_
        else:
            self.dsc = [dsc_]
        self.count_t = len(self.tr)
        self.count_d = len(self.dsc)
        self.fav = fav_
        self.all_tries = all_tries_
        self.correct_tries = correct_tries_
        if all_tries_:
            self.percent = correct_tries_ / all_tries_
        else:
            self.percent = 0
        self.last_tries = last_tries_

    """ Напечатать перевод """
    def print_tr(self, end_='\n'):
        is_first = True
        for tr_wrd in self.tr:
            if is_first:
                is_first = False
            else:
                print(', ', end='')
            print(code(tr_wrd), end='')
        print(end_, end='')

    """ Напечатать описание """
    def print_dsc(self, tab_=0):
        for dsc_ in self.dsc:
            print(' ' * tab_ + '> ' + code(dsc_))

    """ Напечатать запись - кратко """
    def print_briefly(self):
        if self.fav:
            print('(*)', end=' ')
        else:
            print('   ', end=' ')
        if self.last_tries == -1:
            print('[-:  0%]', end=' ')
        else:
            p_ = '{:.0%}'.format(self.percent)
            print(f'[{self.last_tries}:' + (' ' * (4 - len(p_))) + p_ + ']', end=' ')
        print(code(self.wrd) + ': ', end='')
        self.print_tr()
        self.print_dsc(tab_=13)

    """ Напечатать запись - слово со статистикой """
    def print_wrd_with_stat(self):
        print(self.wrd, end='')
        p_ = '{:.0%}'.format(self.percent)
        print(f' [{self.last_tries}:' + (' ' * (4 - len(p_))) + p_ + ']')

    """ Напечатать запись - перевод со статистикой """
    def print_tr_with_stat(self):
        self.print_tr(end_='')
        p_ = '{:.0%}'.format(self.percent)
        print(f' [{self.last_tries}:' + (' ' * (4 - len(p_))) + p_ + ']')

    """ Напечатать запись со всей редактируемой информацией """
    def print_edit(self):
        print(f'       Слово: {self.wrd}')
        print('     Перевод: ', end='')
        self.print_tr(end_='\n      Сноски: ')
        if len(self.dsc) == 0:
            print('-')
        else:
            print('> ' + code(self.dsc[0]))
            for i in range(1, len(self.dsc)):
                print('              > ' + code(self.dsc[i]))
        print(f'   Избранное: {self.fav}')

    """ Напечатать запись со всей информацией """
    def print_all(self):
        print(f'       Слово: {self.wrd}')
        print('     Перевод: ', end='')
        self.print_tr(end_='\n      Сноски: ')
        if len(self.dsc) == 0:
            print('-')
        else:
            print('> ' + code(self.dsc[0]))
            for i in range(1, len(self.dsc)):
                print('              > ' + code(self.dsc[i]))
        print(f'   Избранное: {self.fav}')
        print(f'  Статистика: 1) Последних неверных ответов {self.last_tries}\n'
              f'              2) Доля верных ответов {self.correct_tries}/{self.all_tries} = ' + '{:.0%}'.format(self.percent))

    """ Добавить перевод """
    def add_tr(self, new_tr_, show_msg_=True):
        if new_tr_ not in self.tr:
            self.tr += [new_tr_]
            self.count_t += 1
        elif show_msg_:
            print(f'У этого слова уже есть такой перевод')

    """ Добавить информацию """
    def add_dsc(self, new_dsc_):
        self.dsc += [new_dsc_]
        self.count_d += 1

    """ Добавить статистику """
    def add_stat(self, all_tries_, correct_tries_, last_tries_):
        self.all_tries = all_tries_
        self.correct_tries = correct_tries_
        if all_tries_:
            self.percent = correct_tries_ / all_tries_
        else:
            self.percent = 0
        self.last_tries = last_tries_

    """ Объединить статистику при объединении двух записей """
    def merge_stat(self, all_tries_, correct_tries_, last_tries_):
        self.all_tries += all_tries_
        self.correct_tries += correct_tries_
        if self.all_tries:
            self.percent = self.correct_tries / self.all_tries
        else:
            self.percent = 0
        self.last_tries += last_tries_

    """ Обнулить счётчик, если верная попытка """
    def correct_try(self):
        self.all_tries += 1
        self.correct_tries += 1
        self.percent = self.correct_tries / self.all_tries
        self.last_tries = 0

    """ Увеличить счётчик, если неверная попытка """
    def incorrect_try(self):
        self.all_tries += 1
        if self.last_tries == -1:
            self.last_tries = 0
        self.percent = self.correct_tries / self.all_tries
        self.last_tries += 1

    """ Удалить перевод по его номеру """
    def remove_tr_i(self, index_):
        try:
            self.tr.pop(index_)
            self.count_t -= 1
        except IndexError:
            print(f'Неверный номер варианта "{index_}"')

    """ Удалить информацию по её номеру """
    def remove_dsc_i(self, index_):
        try:
            self.dsc.pop(index_)
            self.count_d -= 1
        except IndexError:
            print(f'Неверный номер варианта "{index_}"')

    """ Удалить перевод """
    def remove_tr(self):
        print('Выберите одно из предложенного:')
        for i in range(self.count_t):
            print(f'{i}. {self.tr[i]}')
        index_ = input('Введите номер варианта: ')
        try:
            index_ = int(index_)
        except ValueError:
            print(f'Неверный номер варианта "{index_}"')
        self.remove_tr_i(index_)

    """ Удалить информацию """
    def remove_dsc(self):
        print('Выберите одно из предложенного:')
        for i in range(self.count_d):
            print(f'{i}. {self.dsc[i]}')
        index_ = input('Введите номер варианта: ')
        try:
            index_ = int(index_)
        except ValueError:
            print(f'Неверный номер варианта "{index_}"')
        self.remove_dsc_i(index_)


class Dictionary(object):
    # self.d - сам словарь
    # self.count_w - количество записей в словаре
    # self.count_t - количество переводов в словаре
    def __init__(self):
        self.d = {}
        self.count_w = 0
        self.count_t = 0

    """ Напечатать словарь """
    def print(self):
        for wrd_ in self.d.keys():
            self.d[wrd_].print_briefly()
        print(f'< {self.count_w} сл. | {self.count_t} перев. >')

    """ Напечатать словарь (только избранные слова) """
    def print_fav(self):
        count_w_ = 0
        count_t_ = 0
        for wrd_ in self.d.keys():
            if self.d[wrd_].fav:
                self.d[wrd_].print_briefly()
                count_w_ += 1
                count_t_ += self.d[wrd_].count_t
        print(f'< {count_w_}/{self.count_w} сл. | {count_t_}/{self.count_t} перев. >')

    """ Напечатать запись из словаря со статистикой """
    def print_tr_with_stat(self, wrd_):
        self.d[wrd_].print_tr_with_stat()

    """ Напечатать запись из словаря со статистикой """
    def print_wrd_with_stat(self, wrd_):
        self.d[wrd_].print_wrd_with_stat()

    """ Напечатать запись из словаря со всей редактируемой информацией """
    def print_edit(self, wrd_):
        self.d[wrd_].print_edit()

    """ Напечатать запись из словаря со всей информацией """
    def print_all(self, wrd_):
        self.d[wrd_].print_all()

    """ Подсчитать среднюю долю правильных ответов """
    def count_rating(self):
        sum_num_ = 0
        sum_den_ = 0
        for el_ in self.d.values():
            sum_num_ += el_.correct_tries
            sum_den_ += el_.all_tries
        return sum_num_ / sum_den_

    """ Добавить запись в словарь """
    def add_val(self, wrd_, tr_, show_msg_=True):
        if wrd_ in self.d.keys():
            self.count_t -= self.d[wrd_].count_t
            self.d[wrd_].add_tr(tr_, show_msg_)
            self.count_t += self.d[wrd_].count_t
        else:
            self.d[wrd_] = Note(wrd_, [tr_])
            self.count_w += 1
            self.count_t += 1

    """ Изменить слово """
    def edit_wrd(self, wrd_, new_wrd_):
        if new_wrd_ in self.d.keys():
            self.count_t -= self.d[wrd_].count_t
            self.count_t -= self.d[new_wrd_].count_t
            for tr_ in self.d[wrd_].tr:
                self.d[new_wrd_].add_tr(tr_, False)
            for dsc_ in self.d[wrd_].dsc:
                self.add_dsc(new_wrd_, dsc_)
            self.count_t += self.d[new_wrd_].count_t
            self.count_w -= 1
            if self.d[wrd_].fav:
                self.d[new_wrd_].fav = True
            self.d[new_wrd_].merge_stat(self.d[wrd_].all_tries, self.d[wrd_].correct_tries, self.d[wrd_].last_tries)
        else:
            self.d[new_wrd_] = Note(new_wrd_, self.d[wrd_].tr, self.d[wrd_].dsc, self.d[wrd_].fav, self.d[wrd_].all_tries, self.d[wrd_].correct_tries, self.d[wrd_].last_tries)
        self.d.pop(wrd_)

    """ Добавить перевод к записи в словаре """
    def add_tr(self, wrd_, tr_, show_msg_=True):
        self.count_t -= self.d[wrd_].count_t
        self.d[wrd_].add_tr(tr_, show_msg_)
        self.count_t += self.d[wrd_].count_t

    """ Добавить информацию к записи в словаре """
    def add_dsc(self, wrd_, dsc_):
        self.d[wrd_].add_dsc(dsc_)

    """ Удалить перевод из словаря """
    def remove_tr(self, wrd_):
        self.count_t -= self.d[wrd_].count_t
        self.d[wrd_].remove_tr()
        self.count_t += self.d[wrd_].count_t

    """ Удалить описание из словаря """
    def remove_dsc(self, wrd_):
        self.d[wrd_].remove_dsc()

    """ Удалить запись из словаря """
    def remove_note(self, wrd_):
        self.count_w -= 1
        self.count_t -= self.d[wrd_].count_t
        self.d.pop(wrd_)

    """ Сохранить словарь в файл """
    def save(self, filename_):
        try:
            with open(filename_, 'w') as file_:
                for key_ in self.d.keys():
                    file_.write(f'w {key_}\n')
                    file_.write(f'{str(self.d[key_].all_tries)}\n')
                    file_.write(f'{str(self.d[key_].correct_tries)}\n')
                    file_.write(f'{str(self.d[key_].last_tries)}\n')
                    for val_ in self.d[key_].tr:
                        file_.write(f't {val_}\n')
                    for val_ in self.d[key_].dsc:
                        file_.write(f'd {val_}\n')
                    if self.d[key_].fav:
                        file_.write(f'f\n')
        except FileNotFoundError:
            print(f'Файл "{filename_}" не найден')
            exit(1)

    """ Прочитать словарь из файла """
    def read(self, filename_):
        try:
            with open(filename_, 'r') as file_:
                while True:
                    line_ = file_.readline().strip()
                    if not line_:
                        break
                    elif line_[0] == 'w':
                        wrd_ = line_[2:]
                        all_tries_ = int(file_.readline().strip())
                        correct_tries_ = int(file_.readline().strip())
                        last_tries_ = int(file_.readline().strip())
                    elif line_[0] == 't':
                        self.add_val(wrd_, line_[2:], False)
                        self.d[wrd_].add_stat(all_tries_, correct_tries_, last_tries_)
                    elif line_[0] == 'd':
                        self.add_dsc(wrd_, line_[2:])
                    elif line_[0] == 'f':
                        self.d[wrd_].fav = True
            return True
        except FileNotFoundError:
            print(f'Файл "{filename_}" не найден')
            return False

    """ Изменить запись в словаре """
    def edit_note(self, wrd_):
        has_changes_ = False
        while True:
            print()
            self.print_edit(wrd_)
            print()
            print('Что вы хотите сделать?')
            print('СЛ - изменить СЛово')
            print('П - изменить Перевод')
            print('СН - изменить СНоски')
            if self.d[wrd_].fav:
                print('И - убрать из Избранного')
            else:
                print('И - добавить в Избранное')
            print('У - Удалить запись')
            print('Н - вернуться Назад')
            cmd_ = input().upper()
            if cmd_ in ['СЛ', 'CK']:
                print()
                new_wrd_ = input('Введите слово: ')
                self.edit_wrd(wrd_, new_wrd_)
                wrd_ = new_wrd_
                has_changes_ = True
            elif cmd_ in ['П', 'G']:
                print()
                print('Что вы хотите сделать?')
                print('Д - Добавить перевод')
                print('У - Удалить перевод')
                cmd_ = input().upper()
                if cmd_ in ['Д', 'L']:
                    print()
                    tr_ = input('Введите перевод: ')
                    self.add_tr(wrd_, tr_)
                    has_changes_ = True
                elif cmd_ in ['У', 'E']:
                    print()
                    self.remove_tr(wrd_)
                    has_changes_ = True
                else:
                    print(f'Неизвестная команда: "{cmd_}"')
            elif cmd_ in ['СН', 'CY']:
                print()
                print('Что вы хотите сделать?')
                print('Д - Добавить сноску')
                print('У - Удалить сноску')
                cmd_ = input().upper()
                if cmd_ in ['Д', 'L']:
                    print()
                    dsc_ = input('Введите сноску: ')
                    self.add_dsc(wrd_, dsc_)
                    has_changes_ = True
                elif cmd_ in ['У', 'E']:
                    print()
                    self.remove_dsc(wrd_)
                    has_changes_ = True
                else:
                    print(f'Неизвестная команда: "{cmd_}"')
            elif cmd_ in ['И', 'B']:
                self.d[wrd_].fav = not self.d[wrd_].fav
                has_changes_ = True
            elif cmd_ in ['У', 'E']:
                print()
                cmd_ = input('Вы уверены, что хотите удалить эту запись? (+ или -): ')
                if cmd_ == '+':
                    self.remove_note(wrd_)
                    has_changes_ = True
                    break
            elif cmd_ in ['Н', 'Y']:
                break
            else:
                print(f'Неизвестная команда: "{cmd_}"')
        return has_changes_

    """ Выбор случайного слова с учётом сложности """
    def random_smart(self):
        sum_ = 0
        for el_ in self.d.values():
            sum_ += (100 - round(100 * el_.percent)) * 4 + 1
        r_ = random.randint(1, sum_)

        for wrd_ in self.d.keys():
            r_ -= (100 - round(100 * self.d[wrd_].percent)) * 4 + 1
            if r_ <= 0:
                return wrd_

    """ Учить слова - все """
    def learn(self):
        count_all = 0
        count_correct = 0
        used_words = set()
        while True:
            if len(used_words) == len(self.d):
                print(f'\033[33mВаш результат: {count_correct}/{count_all}\033[38m')
                break
            while True:
                wrd_ = random.choice(list(self.d.keys()))
                if wrd_ not in used_words:
                    break

            print()
            self.print_tr_with_stat(wrd_)
            wrd_ans = input('Введите слово (# - чтобы закончить, @ - чтобы посмотреть сноски): ')
            if wrd_ans == '@':
                self.d[wrd_].print_dsc()
                wrd_ans = input('Введите слово (# - чтобы закончить): ')

            if wrd_ans == wrd_:
                self.d[wrd_].correct_try()
                print('\033[32mВерно\033[38m')
                count_correct += 1
                used_words.add(wrd_)
                if self.d[wrd_].fav:
                    fav_ = input('Убрать слово из избранного? (+ или -): ')
                    if fav_ == '+':
                        self.d[wrd_].fav = False
            elif wrd_ans == '#':
                print(f'\033[33mВаш результат: {count_correct}/{count_all}\033[38m')
                break
            else:
                self.d[wrd_].incorrect_try()
                print(f'\033[31mНеверно. Правильный ответ: "{wrd_}"\033[38m')
                if not self.d[wrd_].fav:
                    fav_ = input('Добавить слово в избранное? (+ или -): ')
                    if fav_ == '+':
                        self.d[wrd_].fav = True
            count_all += 1
        return True

    """ Учить слова - избранные """
    def learn_fav(self):
        count_all = 0
        count_correct = 0
        used_words = set()
        while True:
            while True:
                if len(used_words) == len(self.d):
                    print(f'\033[33mВаш результат: {count_correct}/{count_all}\033[38m')
                    return None
                wrd_ = random.choice(list(self.d.keys()))
                if not self.d[wrd_].fav:
                    used_words.add(wrd_)
                    continue
                if wrd_ not in used_words:
                    break

            print()
            self.print_tr_with_stat(wrd_)
            wrd_ans = input('Введите слово (# - чтобы закончить, @ - чтобы посмотреть сноски): ')
            if wrd_ans == '@':
                self.d[wrd_].print_dsc()
                wrd_ans = input('Введите слово (# - чтобы закончить): ')

            if wrd_ans == wrd_:
                self.d[wrd_].correct_try()
                print('\033[32mВерно\033[38m')
                count_correct += 1
                used_words.add(wrd_)
                if self.d[wrd_].fav:
                    fav_ = input('Убрать слово из избранного? (+ или -): ')
                    if fav_ == '+':
                        self.d[wrd_].fav = False
            elif wrd_ans == '#':
                print(f'\033[33mВаш результат: {count_correct}/{count_all}\033[38m')
                break
            else:
                self.d[wrd_].incorrect_try()
                print(f'\033[31mНеверно. Правильный ответ: "{wrd_}"\033[38m')
                if not self.d[wrd_].fav:
                    fav_ = input('Добавить слово в избранное? (+ или -): ')
                    if fav_ == '+':
                        self.d[wrd_].fav = True
            count_all += 1
        return True

    """ Учить слова - все, сначала сложные """
    def learn_hard(self):
        count_all = 0
        count_correct = 0
        used_words = set()
        while True:
            if len(used_words) == len(self.d):
                print(f'\033[33mВаш результат: {count_correct}/{count_all}\033[38m')
                break
            while True:
                wrd_ = self.random_smart()
                if wrd_ not in used_words:
                    break

            print()
            self.print_tr_with_stat(wrd_)
            wrd_ans = input('Введите слово (# - чтобы закончить, @ - чтобы посмотреть сноски): ')
            if wrd_ans == '@':
                self.d[wrd_].print_dsc()
                wrd_ans = input('Введите слово (# - чтобы закончить): ')

            if wrd_ans == wrd_:
                self.d[wrd_].correct_try()
                print('\033[32mВерно\033[38m')
                count_correct += 1
                used_words.add(wrd_)
                if self.d[wrd_].fav:
                    fav_ = input('Убрать слово из избранного? (+ или -): ')
                    if fav_ == '+':
                        self.d[wrd_].fav = False
            elif wrd_ans == '#':
                print(f'\033[33mВаш результат: {count_correct}/{count_all}\033[38m')
                break
            else:
                self.d[wrd_].incorrect_try()
                print(f'\033[31mНеверно. Правильный ответ: "{wrd_}"\033[38m')
                if not self.d[wrd_].fav:
                    fav_ = input('Добавить слово в избранное? (+ или -): ')
                    if fav_ == '+':
                        self.d[wrd_].fav = True
            count_all += 1
        return True

    """ Учить слова (обр.) - все """
    def learn_t(self):
        count_all = 0
        count_correct = 0
        used_words = set()
        while True:
            if len(used_words) == len(self.d):
                print(f'\033[33mВаш результат: {count_correct}/{count_all}\033[38m')
                break
            while True:
                wrd_ = random.choice(list(self.d.keys()))
                if wrd_ not in used_words:
                    break

            print()
            self.print_wrd_with_stat(wrd_)
            wrd_ans = input('Введите перевод (# - чтобы закончить, @ - чтобы посмотреть сноски): ')
            if wrd_ans == '@':
                self.d[wrd_].print_dsc()
                wrd_ans = input('Введите перевод (# - чтобы закончить): ')

            if wrd_ans in self.d[wrd_].tr:
                self.d[wrd_].correct_try()
                print('\033[32mВерно\033[38m')
                count_correct += 1
                used_words.add(wrd_)
                if self.d[wrd_].fav:
                    fav_ = input('Убрать слово из избранного? (+ или -): ')
                    if fav_ == '+':
                        self.d[wrd_].fav = False
            elif wrd_ans == '#':
                print(f'\033[33mВаш результат: {count_correct}/{count_all}\033[38m')
                break
            else:
                self.d[wrd_].incorrect_try()
                print(f'\033[31mНеверно. Правильный ответ: {self.d[wrd_].tr}\033[38m')
                if not self.d[wrd_].fav:
                    fav_ = input('Добавить слово в избранное? (+ или -): ')
                    if fav_ == '+':
                        self.d[wrd_].fav = True
            count_all += 1
        return True

    """ Учить слова (обр.) - избранные """
    def learn_t_fav(self):
        count_all = 0
        count_correct = 0
        used_words = set()
        while True:
            while True:
                if len(used_words) == len(self.d):
                    print(f'\033[33mВаш результат: {count_correct}/{count_all}\033[38m')
                    return None
                wrd_ = random.choice(list(self.d.keys()))
                if not self.d[wrd_].fav:
                    used_words.add(wrd_)
                    continue
                if wrd_ not in used_words:
                    break

            print()
            self.print_wrd_with_stat(wrd_)
            wrd_ans = input('Введите перевод (# - чтобы закончить, @ - чтобы посмотреть сноски): ')
            if wrd_ans == '@':
                self.d[wrd_].print_dsc()
                wrd_ans = input('Введите перевод (# - чтобы закончить): ')

            if wrd_ans in self.d[wrd_].tr:
                self.d[wrd_].correct_try()
                print('\033[32mВерно\033[38m')
                count_correct += 1
                used_words.add(wrd_)
                if self.d[wrd_].fav:
                    fav_ = input('Убрать слово из избранного? (+ или -): ')
                    if fav_ == '+':
                        self.d[wrd_].fav = False
            elif wrd_ans == '#':
                print(f'\033[33mВаш результат: {count_correct}/{count_all}\033[38m')
                break
            else:
                self.d[wrd_].incorrect_try()
                print(f'\033[31mНеверно. Правильный ответ: {self.d[wrd_].tr}\033[38m')
                if not self.d[wrd_].fav:
                    fav_ = input('Добавить слово в избранное? (+ или -): ')
                    if fav_ == '+':
                        self.d[wrd_].fav = True
            count_all += 1
        return True

    """ Учить слова (обр.) - все, сначала сложные """
    def learn_t_hard(self):
        count_all = 0
        count_correct = 0
        used_words = set()
        while True:
            if len(used_words) == len(self.d):
                print(f'\033[33mВаш результат: {count_correct}/{count_all}\033[38m')
                break
            while True:
                wrd_ = self.random_smart()
                if wrd_ not in used_words:
                    break

            print()
            self.print_wrd_with_stat(wrd_)
            wrd_ans = input('Введите перевод (# - чтобы закончить, @ - чтобы посмотреть сноски): ')
            if wrd_ans == '@':
                self.d[wrd_].print_dsc()
                wrd_ans = input('Введите перевод (# - чтобы закончить): ')

            if wrd_ans in self.d[wrd_].tr:
                self.d[wrd_].correct_try()
                print('\033[32mВерно\033[38m')
                count_correct += 1
                used_words.add(wrd_)
                if self.d[wrd_].fav:
                    fav_ = input('Убрать слово из избранного? (+ или -): ')
                    if fav_ == '+':
                        self.d[wrd_].fav = False
            elif wrd_ans == '#':
                print(f'\033[33mВаш результат: {count_correct}/{count_all}\033[38m')
                break
            else:
                self.d[wrd_].incorrect_try()
                print(f'\033[31mНеверно. Правильный ответ: {self.d[wrd_].tr}\033[38m')
                if not self.d[wrd_].fav:
                    fav_ = input('Добавить слово в избранное? (+ или -): ')
                    if fav_ == '+':
                        self.d[wrd_].fav = True
            count_all += 1
        return True


dct = Dictionary()
if not dct.read(filename):
    open(filename, 'w')
    dct.read(filename)

print('======================================================================================\n')  # Вывод информации о программе
print('                            Anenokil development  presents')
print('                                  Dictionary  v4.0.3')
print('                                   20.12.2022  4:59\n')
print('======================================================================================\n')

print(f'Файл со словарём "{filename}" открыт.')
print('Используйте эти комбинации для немецких букв: #a = ä, #o = ö, #u = ü, #s = ß')

has_changes = False
while True:
    print()
    print('Что вы хотите сделать?')
    print('Н  - Напечатать словарь')
    print('НИ - Напечатать словарь (только Избранные слова)')
    print('Д  - Добавить запись')
    print('И  - Изменить запись')
    print('НС - Найти запись по Слову')
    print('НП - Найти запись по Переводу')
    print('У  - Учить слова')
    print('С  - Сохранить изменения')
    print('О  - Открыть другой словарь')
    print('З  - Завершить работу')
    cmd = input().upper()
    if cmd in ['Н', 'Y']:
        print()
        dct.print()
    elif cmd in ['НИ', 'YB']:
        print()
        dct.print_fav()
    elif cmd in ['Д', 'L']:
        print()
        wrd = input('Введите слово, которое хотите добавить в словарь: ')
        tr = input('Введите перевод слова: ')
        dct.add_val(wrd, tr)

        cmd = input('Хотите добавить сноску? (+ или -): ')
        if cmd == '+':
            dsc = input('Введите сноску: ')
            dct.add_dsc(wrd, dsc)

        fav = input('Хотите добавить слово в избранное (+ или -): ')
        if fav == '+':
            dct.d[wrd].fav = True

        has_changes = True
        dct.edit_note(wrd)
    elif cmd in ['И', 'B']:
        print()
        wrd = input('Введите слово, запись с которым хотите изменить: ')
        if wrd in dct.d.keys():
            has_changes = dct.edit_note(wrd)
        else:
            print(f'Слово "{wrd}" отсутствует в словаре')
    elif cmd in ['НС', 'YC']:
        print()
        wrd = input('Введите слово, которое хотите найти: ')
        if wrd in dct.d.keys():
            dct.print_all(wrd)
        else:
            print(f'Слово "{wrd}" отсутствует в словаре')
    elif cmd in ['НП', 'YG']:
        print()
        tr = input('Введите перевод слова, которое хотите найти: ')
        isFound = False
        for key in dct.d.keys():
            if tr in dct.d[key].tr:
                isFound = True
                dct.print_all(key)
                print()
        if not isFound:
            print(f'Слово с переводом "{tr}" отсутствует в словаре')
    elif cmd in ['У', 'E']:
        print()
        print('Ваша общая доля правильных ответов: {:.2%}'.format(dct.count_rating()))
        print()
        print('Выберите способ')
        print('1 - Угадывать слово по переводу')
        print('2 - Угадывать перевод по слову')
        cmd = input().upper()
        if cmd == '1':
            print()
            print('Выберите способ')
            print('В - Все слова')
            print('С - все слова (в первую очередь Сложные)')
            print('И - только Избранные слова')
            cmd = input().upper()
            if cmd in ['В', 'D']:
                has_changes = dct.learn()
            elif cmd in ['И', 'B']:
                has_changes = dct.learn_fav()
            elif cmd in ['С', 'C']:
                has_changes = dct.learn_hard()
            else:
                print(f'Неизвестная команда: "{cmd}"')
        elif cmd == '2':
            print()
            print('Выберите способ')
            print('В - Все слова')
            print('С - все слова (в первую очередь Сложные)')
            print('И - только Избранные слова')
            cmd = input().upper()
            if cmd in ['В', 'D']:
                has_changes = dct.learn_t()
            elif cmd in ['И', 'B']:
                has_changes = dct.learn_t_fav()
            elif cmd in ['С', 'C']:
                has_changes = dct.learn_t_hard()
            else:
                print(f'Неизвестная команда: "{cmd}"')
        else:
            print(f'Неизвестная команда: "{cmd}"')
    elif cmd in ['С', 'C']:
        dct.save(filename)
        print()
        print('Успешно сохранено')
        has_changes = False
    elif cmd in ['О', 'J']:
        if has_changes:
            cmd = input('Хотите сохранить изменения и свой прогресс? (+ или -): ')
            if cmd == '+':
                dct.save(filename)
        print()
        filename = input('Введите название файла со словарём (если он ещё не существует, то будет создан пустой словарь): ')
        dct = Dictionary()
        if not dct.read(filename):
            open(filename, 'w')
            dct.read(filename)
        with open(SETTINGS_FN, 'w') as setF:
            setF.write(filename)
    elif cmd in ['З', 'P']:
        if has_changes:
            cmd = input('Хотите сохранить изменения и свой прогресс? (+ или -): ')
            if cmd == '+':
                dct.save(filename)
        break
    else:
        print(f'Неизвестная команда: "{cmd}"')
