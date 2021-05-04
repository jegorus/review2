import re

import requests
from bs4 import BeautifulSoup

import myConfig
from mySQLite import SQLClass


class RequestsDodoClass:
    MySQLiteObj = SQLClass()
    response = None
    HEADERS = {  # Чтобы не сайт не принял за бота
        'User Agent': myConfig.USER_AGENT
    }
    soup = None  # содержит html додо
    obj_items = None  # содержит объекты с полными данными о них: название, цена...
    price_items = None  # нужные строки с ценами
    comp = []  # лист, который отправляется в sql
    pizza_type = 1  # встроенные типы из додо, переменные созданы для удобства
    combo_type = 100  # они на сайте имеют такое же значение
    bonus_type = 6
    len_limit = 25  # предел длины строки, чтобы не выводить слишком длинные объекты
    price_indent = 35  # отступ для вывода цен
    should_sort_asc = False
    should_sort_desc = False
    is_top_all = True
    top_to_print = 3

    # Блок переменных для парсинга
    tag_menu_obj = 'article'
    tag_menu_price = 'span'

    class_menu_obj = 'sc-1x0pa1d-3 jFTBFr'
    class_menu_price = 'money__value'

    def __init__(self):
        self.MySQLiteObj.remove_objects()
        self.get_request(myConfig.PIZZA_LINK)
        self.soup_find_menu()

    def soup_find_name(self, item):
        is_less_than_limit = True  # чтобы не добавлять слишком длинные строки
        result = re.split(r'\"', str(item))
        # поиск названия: через re, т. к. додо не всегда возвращает атрибуты через get
        title_str = ' title='
        for i in range(len(result)):
            if result[i] == title_str:
                if len(result[i + 1]) < self.len_limit:
                    self.comp.append(result[i + 1])
                else:
                    is_less_than_limit = False
                break
        type_str = ' data-type='  # содержит типы: пицца, закуски...
        if is_less_than_limit:
            for i in range(len(result)):
                if result[i] == type_str:
                    self.comp.append(int(result[i + 1]))
                    break
        return is_less_than_limit

    def soup_find_price(self, item):
        self.price_items = item.find(self.tag_menu_price, class_=self.class_menu_price).get_text(strip=True)
        self.comp.append(int(re.sub(r',', '', self.price_items)))  # замена '3,999' -> 3999

    def soup_find_menu(self):
        print("starting to find menu")
        self.obj_items = self.soup.findAll(self.tag_menu_obj, class_=self.class_menu_obj)
        for item in self.obj_items:
            self.comp = []
            is_less = self.soup_find_name(item)
            if is_less:  # если длина названия меньше, чем self.len_limit
                self.soup_find_price(item)
                self.comp[0] = self.comp[0].replace(u'\xa0', u' ')  # поменять кодировку
                self.MySQLiteObj.add_object(self.comp)

    def get_request(self, link):  # получает данные со страницы
        self.response = requests.get(link, headers=self.HEADERS)
        if self.response.ok:
            print("request_get dodo is completed successfully")
            self.soup = BeautifulSoup(self.response.content, 'html.parser')

    def print_request_text(self):  # для печати html страницы
        print(self.response.text)

    def make_menu_str(self, str_type):
        # str_type - тип: пицца, комбо, бонус
        sort_arg = ""
        if self.should_sort_asc:  # заполняется в команде sort
            sort_arg = " ORDER by price"
        elif self.should_sort_desc:
            sort_arg = " ORDER by price DESC"
        ret_str = "```\n"
        counter = 0  # проверяет количество объектов для вывода
        for value in self.MySQLiteObj.sql.execute(f"SELECT * FROM pizza_table{sort_arg}"):
            str_to_format = ":{:>" + str(self.price_indent - len(value[0])) + "}₽"  # для форматирования строки
            if value[1] == str_type:  # выводит только объеты нужного типа, т. к. если вывести все, то строка будет
                # слишком длинной
                ret_str += value[0] + str_to_format.format(value[2]) + '\n'
                counter += 1
            if not self.is_top_all and counter >= self.top_to_print:
                break
        if counter == 0:
            ret_str += "Пропишите /menu\n"
        ret_str += "```\n"
        return ret_str  # эта строка передается для печати с помощью md
