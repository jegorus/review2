import unittest

import main
import myConfig


class TestBot(unittest.TestCase):

    def test_token_test(self):
        print(myConfig.TOKEN)
        self.asserEqual(myConfig.TOKEN[1] == '7')  # проверка нахождения токена

    def test_get_request_dodo(self):  # проверка подключения к додо
        link = myConfig.PIZZA_LINK
        main.MyDodoRequestObj.get_request(link)
        self.assertEqual(main.MyDodoRequestObj.response.ok, True)

    def test_get_request_promo(self):  # проверка подключения к додо
        link = myConfig.PROMO_LINK
        main.MyPromoRequestObj.get_request(link)
        self.assertEqual(main.MyPromoRequestObj.response.ok, True)

    def test_soup(self):  # проверка корректности работы soup
        link = 'https://example.com/'
        main.MyDodoRequestObj.get_request(link)
        self.assertEqual(main.MyDodoRequestObj.soup.title.text, 'Example Domain')

    def test_soup_find_menu(self):  # soup_find_menu находит нужные элементы
        main.MyDodoRequestObj.MySQLiteObj.remove_objects()
        main.MyDodoRequestObj.get_request(myConfig.PIZZA_LINK)
        main.MyDodoRequestObj.soup_find_menu()
        counter = 0
        for value in main.MyDodoRequestObj.MySQLiteObj.sql.execute("SELECT * FROM pizza_table"):
            if isinstance(value, tuple):
                counter += 1
        self.assertGreater(counter, 0)

    def test_remove_objects(self):  # таблица очищается при вызове remove_objects
        main.MyDodoRequestObj.MySQLiteObj.remove_objects()
        main.MyDodoRequestObj.get_request(myConfig.PIZZA_LINK)
        main.MyDodoRequestObj.soup_find_menu()
        main.MyDodoRequestObj.MySQLiteObj.remove_objects()
        counter = 0
        for value in main.MyDodoRequestObj.MySQLiteObj.sql.execute("SELECT * FROM pizza_table"):
            if isinstance(value, tuple):
                counter += 1
        self.assertEqual(counter, 0)

    def test_sort(self):
        main.MyDodoRequestObj.MySQLiteObj.remove_objects()
        main.MyDodoRequestObj.get_request(myConfig.PIZZA_LINK)
        main.MyDodoRequestObj.soup_find_menu()

        main.MyDodoRequestObj.should_sort_asc = True
        main.MyDodoRequestObj.should_sort_desc = False
        result = main.MyDodoRequestObj.make_menu_str(main.MyDodoRequestObj.pizza_type)
        self.assertNotEqual(result, "```\n" + "```\n")  # в строку что-то записалось

        sort_arg = ""
        if main.MyDodoRequestObj.should_sort_asc:
            sort_arg = " ORDER by price"
        elif main.MyDodoRequestObj.should_sort_desc:
            sort_arg = " ORDER by price DESC"
        sort_check = 0
        for value in main.MyDodoRequestObj.MySQLiteObj.sql.execute(
                f"SELECT * FROM pizza_table{sort_arg}"
        ):
            self.assertGreaterEqual(value[2], sort_check)  # проверка на отсортированность
            sort_check = value[2]
