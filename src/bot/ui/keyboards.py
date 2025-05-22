from aiogram.types import ReplyKeyboardMarkup , KeyboardButton , InlineKeyboardMarkup , InlineKeyboardButton


# --- Main menu --------------------------------
btnSub = KeyboardButton ('КУПИТЬ VPN')
btn_continue = KeyboardButton ('УПРАВЛЕНИЕ ТАРИФОМ')
btn_uslug = KeyboardButton ('МОЙ ТАРИФ')
btninstr = KeyboardButton ('ИНСТРУКЦИЯ')
btnHelp = KeyboardButton ('ТЕХ.ПОДДЕРЖКА')
mainMenu = ReplyKeyboardMarkup (resize_keyboard = True)
mainMenu.row(btnSub, btn_continue, btn_uslug)
mainMenu.row(btninstr, btnHelp)

# --- User Commands --------------------------------
bnt_usr_main = InlineKeyboardMarkup (row_width = 1)
btn_usr_tarif = InlineKeyboardMarkup (text = "Продлить тариф", callback_data = "resume_tarif")
btn_usr_download = InlineKeyboardMarkup (text = "Скачать конфиг", callback_data = "download_config")
btn_usr_delete = InlineKeyboardMarkup (text = "Удалить конфиг", callback_data = "delete_config")
bnt_usr_main.insert(btn_usr_tarif)
bnt_usr_main.add(btn_usr_download, btn_usr_delete)

# --- Subscribe Inline Buttons ---------------------------------------------------------
sub_inline_markup = InlineKeyboardMarkup (row_width = 1)
btnSubMonth = InlineKeyboardButton (text = "Уверенная соточка - 300 рублей", callback_data = "tarif1")
sub_inline_markup.insert(btnSubMonth)



# --- Instructions --------------------
btn_intsr_android = KeyboardButton('ANDROID')
btn_intsr_ios = KeyboardButton('IOS')
btn_intsr_windows = KeyboardButton('Windows')
btn_intsr_mainmenu = KeyboardButton('ГЛАВНОЕ МЕНЮ')
bnt_intsr_Menu = ReplyKeyboardMarkup (resize_keyboard = True)
bnt_intsr_Menu.row(btn_intsr_android, btn_intsr_ios, btn_intsr_windows)
bnt_intsr_Menu.add(btn_intsr_mainmenu)


# --- Select Servers List #1 --------------------------------
srv1_kb = InlineKeyboardMarkup (row_width = 3)
srv1_rus_1 = InlineKeyboardButton (text = "Россия #1", callback_data = "srv1_rus_1")
srv1_to_srv2 = InlineKeyboardButton (text = "Следующая страница", callback_data = "srv1_to_srv2")
srv_exit = InlineKeyboardButton (text = "Выход", callback_data = 'srv_exit')
srv_back = InlineKeyboardButton (text = "Назад", callback_data = 'srv1_list')
srv1_kb.row(srv1_rus_1, srv1_to_srv2)
srv1_kb.row(srv_exit)


# --- Select Server RUS №1 ----------------------------------------------------------------
srv1_rus_1_kb = InlineKeyboardMarkup (row_width = 1)
srv1_rus_1_add = InlineKeyboardButton (text = "Создать аккаунт", callback_data = "add_srv1_rus_1")

srv1_rus_1_kb.row(srv1_rus_1_add, srv_back)
srv1_rus_1_kb.row(srv_exit)