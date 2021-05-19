import re

import logging
from aiogram import Bot, Dispatcher, executor, types

import myConfig  # файл с данными и настройками
from myDodoRequest import RequestsDodoClass
from myPromoRequest import RequestPromoClass


# создание бота по токену
logging.basicConfig(level=logging.INFO)  # для отправки логов
bot = Bot(token=myConfig.TOKEN)
dp = Dispatcher(bot)
MyDodoRequestObj = RequestsDodoClass()
MyPromoRequestObj = RequestPromoClass()


# выводит описание
@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    if message.text == "/start":
        # в start происходит парсинг додо
        MyDodoRequestObj.MySQLiteObj.remove_objects()
        MyDodoRequestObj.get_request(myConfig.PIZZA_LINK)
        MyDodoRequestObj.soup_find_menu()
    await message.reply(
        "/help для помощи\n"
        "Бот для анализа сайта Додо пицца\n"
        "город - Москва\n"
        "/menu собирает данные и показывает меню сайта додо пицца\n"
        "Может занять 5-10 секунд для сбора,\n"
        "поэтому, данные собираются и обновляются \n"
        "только при вызове /menu и /start\n"
        "/sort asc /sort desc и /sort off для сортировки\n"
        "/top n для вывода только n > 0 объектов,\n"
        "иначе поведение не определено\n"
        "/top all для вывода всех объектов\n"
        "/top не применим к промокодам\n"
        "/promo all выведет все промокоды на додо пиццу,\n"
        "иначе выведет промокоды по поиску\n"
        "Например: /promo Москв выведет промокоды по Москве\n"
        "но /promo не дает более точного описания акций,\n"
        "исходя из эстетических соображений))\n"
        "иногда может работать более 5 секунд \n",
        reply=False)


# выводит промокоды
@dp.message_handler(commands=['promo'])
async def print_promo(message: types.Message):
    if message.text == '/promo all':
        MyPromoRequestObj.promo_all = True
    else:
        MyPromoRequestObj.promo_all = False
    MyPromoRequestObj.get_request(myConfig.PROMO_LINK)
    find_str = re.findall(r'\w+$', message.text)[0]  # ищет последнее слово
    MyPromoRequestObj.soup_find_promo(find_str)
    await message.reply(MyPromoRequestObj.make_menu_str(), reply=False, parse_mode="Markdown")
# почему md:
# https://stackoverflow.com/questions/56030395/how-to-format-bot-send-message-output-so-it-aligns-like-a-table/56040072


# выводит меню
@dp.message_handler(commands=['menu'])
async def menu_message(message: types.Message):
    # в menu происходит парсинг
    MyDodoRequestObj.MySQLiteObj.remove_objects()
    MyDodoRequestObj.get_request(myConfig.PIZZA_LINK)
    MyDodoRequestObj.soup_find_menu()
    await message.reply("Выберите тип меню:\n"
                        "/pizza - для вывода списка пицц\n"
                        "/combo - для вывода списка комбо\n"
                        "/bonus - для вывода дополнительных блюд\n",
                        reply=False)


@dp.message_handler(commands=['pizza'])
async def print_menu_pizza(message: types.Message):
    await message.reply(MyDodoRequestObj.make_menu_str(MyDodoRequestObj.pizza_type), reply=False, parse_mode="Markdown")


@dp.message_handler(commands=['combo'])
async def print_menu_combo(message: types.Message):
    await message.reply(MyDodoRequestObj.make_menu_str(MyDodoRequestObj.combo_type), reply=False, parse_mode="Markdown")


@dp.message_handler(commands=['bonus'])
async def print_menu_bonus(message: types.Message):
    await message.reply(MyDodoRequestObj.make_menu_str(MyDodoRequestObj.bonus_type), reply=False, parse_mode="Markdown")


@dp.message_handler(commands=['sort'])
async def print_sorted(message: types.Message):
    if message.text == '/sort asc':
        MyDodoRequestObj.should_sort_asc = True
        MyDodoRequestObj.should_sort_desc = False
        await message.reply("Отсортированно по возрастанию", reply=False)
    elif message.text == '/sort desc':
        MyDodoRequestObj.should_sort_asc = False
        MyDodoRequestObj.should_sort_desc = True
        await message.reply("Отсортированно по убыванию", reply=False)
    elif message.text == '/sort off':
        MyDodoRequestObj.should_sort_asc = False
        MyDodoRequestObj.should_sort_desc = False
        await message.reply("Рассортированно", reply=False)
    else:
        await message.reply("Неизвестная команда", reply=False)


# выводит только часть элементов
@dp.message_handler(commands=['top'])
async def print_top(message: types.Message):
    if message.text == '/top all':
        await message.reply("Будут выведены все элементы", reply=False)
        MyDodoRequestObj.is_top_all = True
    else:
        number_str = re.findall(r'\w+$', message.text)[0]  # ищет последнее слово
        try:
            if int(number_str) > 0:
                MyDodoRequestObj.top_to_print = int(number_str)
                MyDodoRequestObj.is_top_all = False
                await message.reply(f"Будут выведены top {number_str}", reply=False)
            else:
                await message.reply("Не надо так", reply=False)
        except ValueError:
            await message.reply("Неизвестная команда", reply=False)


# может сказать "Привет"
@dp.message_handler()
async def send_hi(message: types.Message):
    if message.text.lower() == 'привет':
        await message.reply('Привет', reply=False)
    else:
        await message.reply('Неизвестная команда', reply=False)


# запускается поллинг
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
