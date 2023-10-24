import os
from datetime import datetime
import requests
import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3 as sl
import json
import re
from tabulate import tabulate
import tokens
import keyboards
import sql_query
import schedule
import time
from datetime import datetime, timedelta
import threading
from threading import Thread
con = sl.connect('auction_coins_db.db', check_same_thread=False)
bot = telebot.TeleBot(tokens.token)
group_id = tokens.group_id

###########Личный кабинет Пользователя######################################
@bot.message_handler(commands=['start'])
def start_handler(message):
    args = message.text.split(maxsplit=1)  # разделяем текст на команду и аргументы
    if len(args) > 1:  # если есть аргументы
        lot_id = args[1]  # ожидаем, что аргументом команды /start будет id лота
        # чтобы получить информацию о лоте, используя lot_id
        with con:
            lot_info = con.execute(f"""SELECT * FROM lots WHERE id = {lot_id}""").fetchone()
        if lot_info is not None:
            lot_message = f'Лот №{lot_info[0]}\nЦена: {lot_info[2]}$\n' \
                          f'Продавец: {lot_info[3]}\nГеолокация: {lot_info[4]}\n' \
                          f'Описание: {lot_info[5]}\nВремя начала: {lot_info[6]}\n' \
                          f'Время окончания: {lot_info[7]}\n'
            # Получаем url изображения лота из таблицы 'images'
            image_info = con.execute(f"""SELECT * FROM images WHERE lot_id = {lot_id}""").fetchone()
            if image_info is not None:  # Если есть изображение
                image_path = image_info[2]  # используем путь из таблицы напрямую
                with open(image_path, 'rb') as photo:  # открываем файл изображения
                    bot.send_photo(chat_id=message.chat.id, photo=photo, caption=lot_message,
                                   reply_markup=bid_keyboard(lot_id))
            else:  # Если изображения нет
                bot.send_message(message.chat.id, lot_message, reply_markup=bid_keyboard(lot_id))
        else:
            bot.send_message(message.chat.id, 'Не удалось найти выбранный лот.')
    else:
        bot.send_message(message.chat.id, text=keyboards.welcome_text, reply_markup=keyboards.user_lk_keyboard)



def bid_keyboard(lot_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton('Поставить $10', callback_data=f'bid_10_{lot_id}'),
        InlineKeyboardButton('Поставить $50', callback_data=f'bid_50_{lot_id}'),
        InlineKeyboardButton('Поставить $100', callback_data=f'bid_100_{lot_id}')
    )
    return keyboard

############################################################################


##################Вход в Админ панели#######################################
def request_admin_credentials(message):
    msg = bot.send_message(message.chat.id, "Введите ваш логин:")
    bot.register_next_step_handler(msg, process_admin_login)
def process_admin_login(message):
    login = message.text
    msg = bot.send_message(message.chat.id, "Введите ваш пароль:")
    bot.register_next_step_handler(msg, lambda message: process_admin_password(message, login))

active_admins = {}
def process_admin_password(message, login):
    password = message.text
    user_id = message.chat.id
    user = check_admin_credentials(login, password)
    if user:
        active_admins[message.chat.id] = login
        if user[2] == 'admin':
            bot.send_message(user_id, text='Личный кабинет администратора:', reply_markup=keyboards.admin_lk_keyboard)
        elif user[2] == 'super_admin':
            bot.send_message(user_id, text='Личный кабинет супер_администратора:', reply_markup=keyboards.super_admin_lk_keyboard)
    else:
        bot.send_message(message.chat.id, "Неверные учетные данные. Пожалуйста, попробуйте еще раз.")



@bot.message_handler(commands=['admin'])
def admin_command(message):
    request_admin_credentials(message)

def check_admin_credentials(login, password):
    with con:
        result_admin = con.execute(sql_query.SELECT_ADMINS_QUERY, (login, password)).fetchone()
        result_manager = con.execute(sql_query.SELECT_SUPERADMINS_QUERY, (login, password)).fetchone()
    if result_admin:
        return result_admin[0], result_admin[1], 'admin'
    elif result_manager:
        return result_manager[0], result_manager[1], 'super_admin'

    return None
###########################Конец Панель входа Админ################################

###########################Добавление нового администратора########################
admin_dict = {
    "login": "Введите логин:",
    "password": "Введите пароль:",
    "balance": "Введите баланс:",
}

new_admin = {}
def ask_next_admin_question(telegram_id):
    try:
        question, prompt = next(new_admin[telegram_id]['questions'])
        new_admin[telegram_id]['next_question'] = question
        bot.send_message(chat_id=telegram_id, text=prompt)
    except StopIteration:
        bot.send_message(chat_id=telegram_id, text='Новый администратор успешно создан.')
        add_admin_in_db(new_admin.pop(telegram_id))

def add_admin_in_db(admin_data):
    login = admin_data.get('login')
    password = admin_data.get('password')
    balance = admin_data.get('balance')
    add_admin(login, password, balance)

@bot.message_handler(func=lambda message: message.chat.id in new_admin)
def save_admin_answer(message):
    answer = message.text
    telegram_id = message.chat.id
    question = new_admin[telegram_id]['next_question']
    new_admin[telegram_id][question] = answer
    ask_next_admin_question(telegram_id)

def admin_exists(login):  # Проверяет существование администратора в БД
    with con:
        result = con.execute(sql_query.SELECT_ADMIN_BY_LOGIN_QUERY , (login,)).fetchone()
    return result is not None

def add_admin(login, password, balance):  # Сохранение нового администратора в БД
    with con:
        con.execute(sql_query.INSERT_ADMIN_QUERY, (login, password, balance))
        con.commit()

###################################################################

#####################Создание лота#################################
lot_dict = {
    "login":"Введите ваш логин",
    "start_price": "Введите начальную цену:",
    "seller_link": "Введите ссылку на продавца:",
    "geolocation": "Введите геолокацию:",
    "description": "Введите описание:",
    "start_time": "Введите время начала (в формате YYYY-MM-DD HH:MM:SS):",
    "end_time": "Введите время окончания (в формате YYYY-MM-DD HH:MM:SS):",
    "image": "Введите название файла изображения (с расширением, например: image.jpg):"
}

new_lot = {}

def start_new_lot(call):
    telegram_id = call.message.chat.id
    new_lot[telegram_id] = {'questions': iter(lot_dict.items())}
    ask_next_lot_question(telegram_id)

def ask_next_lot_question(telegram_id):
    try:
        question, prompt = next(new_lot[telegram_id]['questions'])
        new_lot[telegram_id]['next_question'] = question
        bot.send_message(chat_id=telegram_id, text=prompt)
    except StopIteration:
        bot.send_message(chat_id=telegram_id, text='Лот успешно создан.')
        add_lot_in_db(new_lot.pop(telegram_id))

def add_lot_in_db(lot_data):
    login = lot_data.get('login')
    start_price = lot_data.get('start_price')
    seller_link = lot_data.get('seller_link')
    geolocation = lot_data.get('geolocation')
    description = lot_data.get('description')
    start_time = lot_data.get('start_time')
    end_time = lot_data.get('end_time')
    image = lot_data.get('image')
    lot_id = add_lot(login, start_price, seller_link, geolocation, description, start_time, end_time)
    image_path = f"picture\{image}"
    add_image_in_db(lot_id, image_path)
    start_time = datetime.strptime(lot_data.get('start_time'), '%Y-%m-%d %H:%M:%S')
    end_time = datetime.strptime(lot_data.get('end_time'), '%Y-%m-%d %H:%M:%S')
    lot_duration = (end_time - start_time).total_seconds()
    schedule.every(lot_duration).seconds.do(end_auction, lot_id)
    return lot_id

@bot.message_handler(func=lambda message: message.chat.id in new_lot)
def save_lot_answer(message):
    answer = message.text
    telegram_id = message.chat.id
    question = new_lot[telegram_id]['next_question']
    # Валидация различных полей
    if question == 'start_price' and not valid_float(answer):
        bot.send_message(message.chat.id, "Введите числовое значение для начальной цены:")
        bot.register_next_step_handler(message, save_lot_answer)
    elif question in ['start_time', 'end_time']:  # проверка времени начала и конца
        try:
            datetime.strptime(answer, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            bot.send_message(message.chat.id, "Время должно быть в формате 'YYYY-MM-DD HH:MM:SS':")
            bot.register_next_step_handler(message, save_lot_answer)
        else:
            new_lot[telegram_id][question] = answer
            ask_next_lot_question(telegram_id)
    else:  # в других случаях, сохранить ответ без какой-либо обработки
        new_lot[telegram_id][question] = answer
        ask_next_lot_question(telegram_id)

def add_lot(login, start_price, seller_link, geolocation, description, start_time, end_time):  # Сохранение нового лота в БД
    with con:
        c = con.cursor()
        c.execute(sql_query.BUF_INSERT_LOT_QUERY, (login, start_price, seller_link, geolocation, description, start_time, end_time))
        con.commit()
        return c.lastrowid
def add_image_in_db(lot_id, image_path):
    print(f"Checking file in {image_path}")
    if os.path.isfile(image_path):
        print(f"Файл найден , путь добавлен в БД")
        with con:
            con.execute(sql_query.INSERT_IMAGE_QUERY, (lot_id, image_path))
            con.commit()
    else:
        print(f"Файл не найден")

###################################################################

###################Проверка баланса################################
def get_user_balance(login):
    with con:
        result = con.execute(sql_query.SELECT_BALANCE_BY_LOGIN_QUERY, (login,)).fetchone()
    return result[0] if result is not None else None

###################################################################

################Yes or No #########################################
def yes_or_no(message):
    id_lot = message.text
    try:
        id_lot = int(id_lot)
        id_list = []
        with con:
            existing_id = con.execute("""SELECT id FROM buf_lots""")
            existing_id = existing_id.fetchall()
            print(existing_id)
        for i in existing_id:
            id_list.append(i[0])
        if id_lot in id_list:
            bot.send_message(message.chat.id, f"Опубликовать лот c id {id_lot}?", reply_markup=keyboards.choose_yes_or_no(id_lot))
        else:
            bot.send_message(message.chat.id, "id указан неверно, выберите id из таблицы")
            bot.register_next_step_handler(message, yes_or_no)
    except:
        bot.send_message(message.chat.id, "id указан неверно, выберите id из таблицы")
        bot.register_next_step_handler(message, yes_or_no)

#####################################################################################

####################Переход в ЛС бота#############################
def lot_group_keyboard(lot_id):
    participate_url = f'https://t.me/Coins_auction_bot?start={lot_id}'
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton('Участвовать', url=participate_url),
        InlineKeyboardButton('Таймер', callback_data=f'm_{lot_id}'),
        InlineKeyboardButton('Справка', callback_data='и')
    )
    return keyboard
###################################################################

##################Ставки##########################################
# Обработка запросов ставок
@bot.callback_query_handler(func=lambda call: call.data.startswith("bid_"))
def callback_bid(call):
    _, bid_increase, lot_id = call.data.split('_')
    bid_increase = int(bid_increase)  # преобразуем increment в int
    lot_id = int(lot_id)  # преобразуем id lot к int
    user_id = call.from_user.id  # id пользователя, делающего ставку
    with con:
        try:
            # Получаем текущую ставку пользователя (если она существует)
            current_bid = con.execute(
                "SELECT amount FROM bids WHERE user_id = ? AND lot_id = ?", (user_id, lot_id)).fetchone()
            start_price = con.execute(
                "SELECT start_price FROM lots WHERE id = ?", (lot_id,)).fetchone()[0]
            if current_bid is None:  # Если текущая ставка не существует, создаем новую
                con.execute("INSERT INTO bids (user_id, lot_id, amount) VALUES (?, ?, ?)",
                            (user_id, lot_id, start_price + bid_increase))
            else:  # иначе обновим текущую ставку, добавив новую ставку
                new_bid_amount = current_bid[0] + bid_increase
                con.execute("UPDATE bids SET amount = ? WHERE user_id = ? AND lot_id = ?",
                            (new_bid_amount, user_id, lot_id))
            con.commit()  # Сохраняем изменения
            # Показываем три лучших ставки для данного лота после обновления ставки
            top_bids = con.execute(
                "SELECT user_id, amount FROM bids WHERE lot_id = ? ORDER BY amount DESC LIMIT 3",
                (lot_id, )).fetchall()
            # Создаем ответное сообщение
            response_message = f'Топовые ставки {lot_id}:\n'
            for i, bid in enumerate(top_bids, start=1):
                user_id, amount = bid
                response_message += f'{i}. Пользователь {user_id}: {amount}$\n'
            # отправляем ответное сообщение
            bot.answer_callback_query(call.id, text=response_message)
        except sl.Error as e:
            # Если есть ошибки , отправляем сообщение об ошибке в обратный вызов
            bot.answer_callback_query(call.id, text=f"Произошла ошибка: {e}")



##################################################################

################ TIME ############################################
###
@bot.callback_query_handler(func=lambda call: call.data.startswith("m_"))
def callback_timer(call):
    lot_id = int(call.data.split('_')[1])
    with con:
        # запрашиваем время окончания для данного лота
        end_time_str = con.execute(f"SELECT end_time FROM lots WHERE id = {lot_id}").fetchone()
        if end_time_str is not None:  # если есть запись о времени окончания
            end_time = datetime.strptime(end_time_str[0], '%Y-%m-%d %H:%M:%S')  # парсим время
            current_time = datetime.now()  # берём текущее время
            delta = end_time - current_time  # находим разницу времени до окончания

            if delta > timedelta():  # если время до окончания больше нуля
                # форматируем строку вывода и отсылаем в бота
                message = f"До окончания аукциона осталось {str(delta).split('.', 2)[0]}."
                bot.answer_callback_query(call.id, message)
            else:  # иначе аукцион уже окончен
                bot.answer_callback_query(call.id, "Аукцион уже окончен.")
####
##################################################################


######### Конец аукциона ######################
def end_auction(lot_id):
    with con:
        # Получаем победителя аукциона
        winner_bid = con.execute(
            "SELECT user_id, amount, notified FROM bids WHERE lot_id = ? ORDER BY amount DESC LIMIT 1",
            (lot_id, )).fetchone()
    if winner_bid is not None:  # если есть хоть одна ставка
        winner_id, winner_amount, notified = winner_bid
        if not notified:  # Если уведомление еще не было отправлено
            # Отправляем уведомление победителю
            bot.send_message(winner_id,
                             f'Поздравляем! Вы выиграли аукцион {lot_id}.\nВаша ставка: {winner_amount}\n'
                             f'Для дальнейших действий, пожалуйста, свяжитесь с продавцом.')
            # Обновляем статус `notified` в базе данных, чтобы избежать повторных уведомлений
            con.execute("UPDATE bids SET notified = 1 WHERE user_id = ? AND lot_id = ?",
                        (winner_id, lot_id))
            con.commit()
    else:
        print(f"Аукцион {lot_id} завершился без ставок.")

def run_pending_jobs():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Запускаем проверку задач в отдельном потоке
Thread(target=run_pending_jobs).start()

###############################################

####### Valid ################################
def valid_float(input_string):
    try:
        float(input_string)
        return True
    except ValueError:
        return False
##############################################

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    flag = call.data[0]  # Берем первый символ из callback_data
    data = call.data[1:]  # Берем все символы начиная со второго
    if call.data == 'new_admin':  # если нажата кнопка "Создать нового администратора"
        msg = bot.send_message(call.message.chat.id, "Введите логин нового администратора:")
        bot.register_next_step_handler(msg, start_new_admin)

    elif call.data == 'lots':
        bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id, text="Управление лотами:",
                         reply_markup=keyboards.admin_lots_keyboard)

    elif call.data == 'balance':
        if call.message.chat.id in active_admins:
            login = active_admins[call.message.chat.id]
            balance = get_user_balance(login)
            bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id, text=f'Ваш баланс: {balance}$', reply_markup=keyboards.back_keyboard)
        else:
            bot.send_message(chat_id=call.message.chat.id,
                             text='Произошла ошибка. Пожалуйста, попробуйте войти заново.')
    elif call.data == 'назад':
        user_type = new_admin.get(call.message.chat.id, {}).get("type")
        if user_type == "admin":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Личный кабинет администратора:", reply_markup=keyboards.admin_lk_keyboard)
        elif user_type == "super_admin":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Личный кабинет суперадминистратора:",
                                  reply_markup=keyboards.super_admin_lk_keyboard)
    elif call.data == 'создать_лот':
        start_new_lot(call)
    elif call.data == 'в_меню':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Личный кабинет администратора:", reply_markup=keyboards.admin_lk_keyboard)
    elif call.data == 'Правила':
        back_keyboard = types.InlineKeyboardMarkup()
        back_button = types.InlineKeyboardButton("Назад", callback_data='to_home')
        back_keyboard.add(back_button)
        bot.answer_callback_query(call.id)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=keyboards.rules_text, reply_markup=back_keyboard)
    elif call.data == 'х_auctions':
        user_id = call.from_user.id  # id пользователя, делающего запрос
        with con:
            # Получаем все аукционы, в которых пользователь был победителем
            won_auctions = con.execute(
                "SELECT lots.id, lots.description, lots.seller_link, bids.amount FROM lots JOIN bids ON lots.id = bids.lot_id WHERE bids.user_id = ? AND bids.notified = 1 ORDER BY bids.amount DESC",
                (user_id,)).fetchall()
            if won_auctions:  # Если есть такие аукционы
                response_message = '\n'.join([
                    f'Вы выиграли аукцион {lot_id}.\n'
                    f'Ваша ставка: {amount}\n'
                    f'Описание: {description}\n'
                    f'на продавца можно перейти по ссылке: {seller_link}\n'
                    for lot_id, description, seller_link, amount in won_auctions
                ])

            else:
                response_message = 'Вы пока не выиграли ни одного аукциона.'
            # Создаем кнопку "Назад"
            back_keyboard = types.InlineKeyboardMarkup()
            back_button = types.InlineKeyboardButton("Назад", callback_data='to_home')
            back_keyboard.add(back_button)
            # Отправляем сообщение
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=response_message, reply_markup=back_keyboard)
    elif call.data == 'show_lots':
        admin_id = active_admins.get(call.message.chat.id)

        if admin_id is not None:
            headers = ['id', 'start_price', 'seller_link', 'geolocation', 'description', 'start_time', 'end_time']
            with con:
                data1 = con.execute(f"SELECT * FROM lots WHERE admin_id='{admin_id}'")
                lots = data1.fetchall()
                if len(lots) != 0:
                    bot.send_message(call.message.chat.id, f'Ваши опубликованные лоты:', parse_mode='HTML')
                    bot.send_message(call.message.chat.id, f'<pre>{tabulate(lots, headers=headers)}</pre>',
                                     parse_mode='HTML')
                else:
                    bot.send_message(call.message.chat.id, 'У вас пока нет опубликованных лотов.')
        else:
            bot.send_message(call.message.chat.id, 'Произошла ошибка. Пожалуйста, попробуйте войти заново.')
    elif call.data == 'delete_lots':
        pass
    elif call.data == 'to_home':
        bot.answer_callback_query(call.id)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=keyboards.welcome_text, reply_markup=keyboards.user_lk_keyboard)
    elif call.data == 'тех_поддержка':
        bot.send_message(chat_id=call.message.chat.id, text='Выберите опцию:', reply_markup=keyboards.sup_keyboard)
    elif call.data == 'упр_лотами':
        headers = ['id', 'login', 'start_price', 'seller_link', 'geolocation', 'description', 'start_time', 'end_time']
        with con:
            data1 = con.execute(f"SELECT * FROM buf_lots")
            lots = data1.fetchall()
            if len(lots) != 0:
                bot.send_message(call.message.chat.id, f'Таблица <b>buf_lots</b>', parse_mode='HTML')
                bot.send_message(call.message.chat.id, f'<pre>{tabulate(lots, headers=headers)}</pre>',
                                 parse_mode='HTML')
                bot.send_message(call.message.chat.id, 'Введите id лота для дальнейшей работы с ним')
                bot.register_next_step_handler(call.message,
                                               yes_or_no)  # регистрация обработчика для следующего действия пользователя
            else:
                bot.send_message(call.message.chat.id, 'В буферной таблице пока нет лотов')
    elif call.data == 'редактироание':
                with con:
                    # получение списка администраторов
                    admins = [
                        (id, login)
                        for id, login, _, _ in con.execute('SELECT * FROM admins').fetchall()
                    ]
                admins_text = '\n'.join(
                    f"ID: {id}, Логин: {login}"
                    for id, login in admins
                )
                msg = bot.send_message(call.message.chat.id,
                                       f'Список админов:\n{admins_text}\nВведите ID администратора для дальнейшей работы.')
                bot.register_next_step_handler(msg, process_admin_id)
    elif call.data.startswith('remove_'):
                admin_id = int(call.data.split('_')[1])
                with con:
                    con.execute('DELETE FROM admins WHERE id = ?', (admin_id,))
                bot.send_message(call.message.chat.id, f'Администратор с ID {admin_id} успешно удален.')
    elif call.data.startswith('change_'):
                admin_id = int(call.data.split('_')[1])
                msg = bot.send_message(call.message.chat.id,
                                       f'Для админа с ID {admin_id} выберите поле для изменения: логин, пароль или баланс.')
                bot.register_next_step_handler(msg, choose_field_to_change, admin_id)
    # elif flag == "и":
    #     bot.answer_callback_query(call.message.chat.id, 'В буферной таблице пока нет лотов')
    if flag == "y":
        data = int(data)
        with con:
            cat_prod_table = con.execute(f"""DELETE FROM buf_lots WHERE id = {data}""")
        bot.send_message(call.message.chat.id, 'Лот удалён!', reply_markup=keyboards.admin_lk_keyboard)
        # После нажатия на кнопку "Опубликовать лот"
    elif flag == "h":
        with con:
            current_info = con.execute(f"""SELECT * FROM buf_lots WHERE id = {int(data)}""")
            current_info_set = current_info.fetchall()
            con.execute(
                """INSERT INTO lots (admin_id, start_price, seller_link, geolocation, description, start_time, end_time) values (?, ?, ?, ?, ?, ?, ?)""",
                (current_info_set[0][1], current_info_set[0][2], current_info_set[0][3],
                 current_info_set[0][4], current_info_set[0][5], current_info_set[0][6], current_info_set[0][7])
            )
            lot_id = current_info_set[0][0]
            con.execute(f"""DELETE FROM buf_lots WHERE id = {int(data)}""")

            # Получаем url изображения лота из таблицы 'images'
            image_info = con.execute(f"""SELECT * FROM images WHERE lot_id = {lot_id}""").fetchone()
            if image_info is not None:  # Если есть изображение
                image_path = image_info[2]  # используем путь из таблицы напрямую
                with open(image_path, 'rb') as photo:  # открываем файл изображения
                    lot_message = f'Лот №{lot_id}\nЦена: {current_info_set[0][2]}$\n' \
                                  f'Продавец: {current_info_set[0][3]}\nГеолокация: {current_info_set[0][4]}\n' \
                                  f'Описание: {current_info_set[0][5]}\nВремя начала: {current_info_set[0][6]}\n' \
                                  f'Время окончания: {current_info_set[0][7]}\n'
                    # Отправляем сообщение в группу с изображением
                    bot.send_photo(chat_id=group_id, photo=photo, caption=lot_message,
                                   reply_markup=lot_group_keyboard(lot_id))
            else:
                bot.send_message(call.message.chat.id, 'Не удалось найти изображение для лота.')


def process_admin_id(message):
    admin_id = int(message.text)
    with con:  # соединение с базой данных
        # проверка есть ли администратор с введенным ID
        admin_exists = con.execute('SELECT * FROM admins WHERE id = ?', (admin_id,)).fetchone() is not None
    if admin_exists:  # если администратор существует
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Удалить администратора', callback_data=f'remove_{admin_id}'))
        markup.add(types.InlineKeyboardButton('Изменить данные администратора', callback_data=f'change_{admin_id}'))
        bot.send_message(message.chat.id, f'Выберите действие для администратора с ID {admin_id}:\n', reply_markup=markup)
    else:  # если администратор не найден
        bot.send_message(message.chat.id, 'Администратор с указанным ID не найден. Пожалуйста, попробуйте еще раз.')

def choose_field_to_change(message, admin_id):
    if message.text.lower() == 'логин':
        bot.send_message(message.chat.id, text ='Ввведите новый логин')
        bot.register_next_step_handler(message, process_admin_login_change, admin_id)
    elif message.text.lower() == 'пароль':
        bot.send_message(message.chat.id, text='Ввведите новый пароль')
        bot.register_next_step_handler(message, process_admin_password_change, admin_id)
    elif message.text.lower() == 'баланс':
        bot.send_message(message.chat.id, text='Ввведите новый баланс')
        bot.register_next_step_handler(message, process_admin_balance_change, admin_id)

def process_admin_change(message, admin_id):
    try:
        login, password = message.text.split(maxsplit=1)
    except ValueError:  # если данные введены некорректно
        bot.send_message(message.chat.id, 'Ошибка! Вы ввели данные некорректно. Попробуйте еще раз.')
        return
    with con:
        # обновление данных администратора
        con.execute('UPDATE admins SET login = ?, password = ? WHERE id = ?', (login, password, admin_id,))
    bot.send_message(message.chat.id, f'Данные администратора с ID {admin_id} успешно обновлены.')

################
def process_admin_login_change(message, admin_id):
    new_login = message.text
    with con:
        # обновление логина администратора
        con.execute('UPDATE admins SET login = ? WHERE id = ?', (new_login, admin_id,))
    bot.send_message(message.chat.id, f'Логин администратора с ID {admin_id} успешно обновлен.')

def process_admin_password_change(message, admin_id):
    new_password = message.text
    with con:
        # обновление пароля администратора
        con.execute('UPDATE admins SET password = ? WHERE id = ?', (new_password, admin_id,))
    bot.send_message(message.chat.id, f'Пароль администратора с ID {admin_id} успешно обновлен.')

def process_admin_balance_change(message, admin_id):
    try:
        new_balance = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, 'Указан недопустимый баланс. Пожалуйста, укажите число.')
        return
    with con:
        # обновление баланса администратора
        con.execute('UPDATE admins SET balance = ? WHERE id = ?', (new_balance, admin_id,))
    bot.send_message(message.chat.id, f'Баланс администратора с ID {admin_id} успешно обновлен.')
################
def start_new_admin(message):
    telegram_id = message.chat.id
    login = message.text
    if not admin_exists(login): # здесь проверим существует ли уже администратор с таким логином
        # Создаем нового администратора без запроса логина, так как мы только что проверили его
        new_admin[telegram_id] = {'login': login, 'questions': iter({k: v for k, v in admin_dict.items() if k != "login"}.items())} #создает новый словарь, который включает все пары ключ-значение из исходного словаря admin_dict, за исключением тех, где ключ равен "login".
        ask_next_admin_question(telegram_id)
    else:
        msg = bot.send_message(chat_id=telegram_id, text=f"Администратор с логином {login} уже существует. Введите другой логин:")
        bot.register_next_step_handler(msg, start_new_admin)

print('Ready')
bot.infinity_polling(skip_pending=True)
