""" Стандартные темы """

THEMES = ('light', 'dark', 'infernal', 'solar')

# Все: bg
# Все, кроме frame: fg
# Все, кроме текста: border
# Frame: relief
# Кнопки: activebackground
# Entry: selectbackground, highlightcolor

ST_BG          = {THEMES[0]: '#EEEEEE', THEMES[1]: '#222222',
                  THEMES[2]: '#DD1515', THEMES[3]: '#FFFFDD'}  # Цвет фона окна
ST_BG_FIELDS   = {THEMES[0]: '#FFFFFF', THEMES[1]: '#171717',
                  THEMES[2]: '#FFAAAA', THEMES[3]: '#EEEECC'}  # Цвет фона полей ввода

ST_BORDER      = {THEMES[0]: '#222222', THEMES[1]: '#111111',
                  THEMES[2]: '#330000', THEMES[3]: '#444422'}  # Цвет рамок
ST_RELIEF      = {THEMES[0]: 'groove',  THEMES[1]: 'solid',
                  THEMES[2]: 'groove',  THEMES[3]: 'groove' }  # Стиль рамок

ST_SELECT      = {THEMES[0]: '#AABBBB', THEMES[1]: '#444444',
                  THEMES[2]: '#FF5500', THEMES[3]: '#CCCCAA'}  # Цвет выделения текста
ST_HIGHLIGHT   = {THEMES[0]: '#00DD00', THEMES[1]: '#007700',
                  THEMES[2]: '#0000FF', THEMES[3]: '#22DD00'}  # Цвет подсветки виджета при фокусе

ST_BTN         = {THEMES[0]: '#D0D0D0', THEMES[1]: '#202020',
                  THEMES[2]: '#DD2020', THEMES[3]: '#E0E0C0'}  # Цвет фона обычных кнопок
ST_BTN_SELECT  = {THEMES[0]: '#BABABA', THEMES[1]: '#272727',
                  THEMES[2]: '#DD5020', THEMES[3]: '#CBCBA9'}  # Цвет фона обычных кнопок при нажатии
ST_BTNY        = {THEMES[0]: '#88DD88', THEMES[1]: '#446F44',
                  THEMES[2]: '#CC6633', THEMES[3]: '#AAEE88'}  # Цвет фона да-кнопок
ST_BTNY_SELECT = {THEMES[0]: '#77CC77', THEMES[1]: '#558055',
                  THEMES[2]: '#CC9633', THEMES[3]: '#99DD77'}  # Цвет фона да-кнопок при нажатии
ST_BTNN        = {THEMES[0]: '#FF6666', THEMES[1]: '#803333',
                  THEMES[2]: '#CD0000', THEMES[3]: '#FF6644'}  # Цвет фона нет-кнопок
ST_BTNN_SELECT = {THEMES[0]: '#EE5555', THEMES[1]: '#904444',
                  THEMES[2]: '#CD3000', THEMES[3]: '#EE5533'}  # Цвет фона нет-кнопок при нажатии

ST_FG_TEXT     = {THEMES[0]: '#222222', THEMES[1]: '#979797',
                  THEMES[2]: '#000000', THEMES[3]: '#444422'}  # Цвет обычного текста
ST_FG_LOGO     = {THEMES[0]: '#FF7200', THEMES[1]: '#803600',
                  THEMES[2]: '#FF7200', THEMES[3]: '#FF8800'}  # Цвет текста логотипа
ST_FG_FOOTER   = {THEMES[0]: '#666666', THEMES[1]: '#666666',
                  THEMES[2]: '#222222', THEMES[3]: '#666644'}  # Цвет текста нижнего колонтитула
ST_FG_WARN     = {THEMES[0]: '#DD2222', THEMES[1]: '#AA0000',
                  THEMES[2]: '#FF9999', THEMES[3]: '#EE4400'}  # Цвет текста нижнего колонтитула
