from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton



user_lk_keyboard = types.InlineKeyboardMarkup()
user_lk_keyboard.add(types.InlineKeyboardButton('Мои аукционы',callback_data='х_auctions'))
user_lk_keyboard.add(types.InlineKeyboardButton('Правила',callback_data='Правила'))
user_lk_keyboard.add(types.InlineKeyboardButton('Статистика',callback_data='3'))
user_lk_keyboard.add(types.InlineKeyboardButton('Помощь',callback_data='4'))
user_lk_keyboard.add(types.InlineKeyboardButton('Пожаловаться',callback_data='5'))



rules_text = ("Правила:\n"
              "После окончания торгов, победитель или продавец должны выйти на связь в течении суток!!️\n"
              "Победитель обязан выкупить лот в течении ТРЁХ дней после окончания аукциона🔥\n"
              "НЕ ВЫКУП ЛОТА - ПЕРМАНЕНТНЫЙ БАН ВО ВСЕХ НУМИЗМАТИЧЕСКИХ СООБЩЕСТВАХ И АУКЦИОНАХ🤬\n"
              "Чтобы узнать время окончания аукциона, нажмите на ⏰\n"
              "Антиснайпер - Ставка сделанная за 5 минут до конца, автоматически переносит аукцион на 5 минут вперёд !!️\n"
              "Работают только проверенные продавцы. Дополнительные Фото можно запросить у продавца.\n"
              "Случайно сделал ставку?🤔 Напиши продавцу!!️\n"
              "Отправка почтой, стоимость пересылки зависит от общего веса отправления и страны. Обсуждается с продавцом.\n"
              "Лоты можно копить, экономя при этом на почте.\n"
              "Отправка в течении трех дней после оплаты!!️")

welcome_text = ("Меню пользователя:\n"
                    "Привет, я бот аукционов @Coins_auction_bot\n" 
                    "Я помогу вам следить за выбранными лотами и регулировать ход аукциона.\n"
                    "А также буду следить за вашими накопленными балами.\n"
                    "Удачных торгов 🤝")

lot_text = ("Делая ставку, учасник подтверждает желание и возможность купить товар.")

admin_lk_keyboard = types.InlineKeyboardMarkup()
admin_lk_keyboard.add(types.InlineKeyboardButton('Управление лотами', callback_data='lots'))
admin_lk_keyboard.add(types.InlineKeyboardButton('Просмотр финансов', callback_data='balance'))
admin_lk_keyboard.add(types.InlineKeyboardButton('История торгов', callback_data='3'))
admin_lk_keyboard.add(types.InlineKeyboardButton('Личные данные', callback_data='4'))

admin_lots_keyboard = types.InlineKeyboardMarkup()
admin_lots_keyboard.add(types.InlineKeyboardButton('Создать лот', callback_data='создать_лот'))
admin_lots_keyboard.add(types.InlineKeyboardButton('Просмотреть лоты', callback_data='show_lots'))
admin_lots_keyboard.add(types.InlineKeyboardButton('Удалить лот', callback_data='delete_lots'))
admin_lots_keyboard.add(types.InlineKeyboardButton('Назад', callback_data='в_меню'))

super_admin_lk_keyboard = types.InlineKeyboardMarkup()
super_admin_lk_keyboard.add(types.InlineKeyboardButton('Управление администраторами', callback_data='редактироание'))
super_admin_lk_keyboard.add(types.InlineKeyboardButton('Управление тех поддержкой', callback_data='тех_поддержка'))
super_admin_lk_keyboard.add(types.InlineKeyboardButton('Создать нового администратора', callback_data='new_admin'))

sup_keyboard = types.InlineKeyboardMarkup()
sup_keyboard.add(types.InlineKeyboardButton('Управление лотами', callback_data='упр_лотами'))
sup_keyboard.add(types.InlineKeyboardButton('Жалобы', callback_data='жалобы'))
sup_keyboard.add(types.InlineKeyboardButton('Страйки Администраторов', callback_data='@страйки_админов'))


back_keyboard = types.InlineKeyboardMarkup()
back_keyboard.add(types.InlineKeyboardButton('Назад', callback_data='в_меню'))


yes_or_no_lots_keyboard = types.InlineKeyboardMarkup()
yes_or_no_lots_keyboard.add(types.InlineKeyboardButton('Опубликовать', callback_data='Опубликовать'))
yes_or_no_lots_keyboard.add(types.InlineKeyboardButton('Отклонить ', callback_data='Отклонить'))


def choose_yes_or_no(id_lot):
    keyboard_lot = types.InlineKeyboardMarkup()
    keyboard_lot.add(types.InlineKeyboardButton('Опубликовать', callback_data=f'h{id_lot}'))
    keyboard_lot.add(types.InlineKeyboardButton('Отклонить лот', callback_data=f'y{id_lot}'))
    return keyboard_lot

def create_admin_field_keyboard(admin_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Изменить логин', callback_data=f'change_login_{admin_id}'))
    markup.add(types.InlineKeyboardButton('Изменить пароль', callback_data=f'change_password_{admin_id}'))
    markup.add(types.InlineKeyboardButton('Изменить баланс', callback_data=f'change_balance_{admin_id}'))
    return markup
