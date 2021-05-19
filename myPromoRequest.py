import requests
from bs4 import BeautifulSoup

import myConfig


class RequestPromoClass:
    response = None
    new_items = None
    HEADERS = {  # Чтобы не сайт не принял за бота
        'User Agent': myConfig.USER_AGENT
    }
    promo_all = True
    soup = None  # содержит html додо

    tag_promo = 'div'
    class_promo = 'item-tovars'
    class_old_promo = 'tovars tovars-old'
    coupon_class = 'clipboardjs-workaround'
    promos = []

    def __init__(self):
        self.get_request(myConfig.PROMO_LINK)
        self.soup_find_promo('')

    def get_request(self, link):
        self.response = requests.get(link, headers=self.HEADERS)
        if self.response.ok:
            # print("request_get promo is completed successfully")
            self.soup = BeautifulSoup(self.response.content, 'html.parser')

    def soup_find_promo(self, find_str):
        self.promos = []
        # поиск объектов
        all_items = set(self.soup.findAll(self.tag_promo, class_=[f'{self.class_promo}']))
        old_items = set(self.soup.findAll(self.tag_promo, class_=[f'{self.class_old_promo}']))
        self.new_items = all_items - old_items
        for item in self.new_items:
            find_check = -2 + (not self.promo_all)  # если promo_all = True, то -2 != -1, и программа будет считать,
            # что найдено совпадение
            if item.text.find(find_str) != find_check:
                # поиск купона
                coupon_str = item.find(self.tag_promo, class_=self.coupon_class).text
                if coupon_str != '':
                    # выделение названия
                    tag_t = 'a'
                    tag_extra = 'p'
                    class_t = "click-coupon"
                    class_extra = "sales"
                    need_item = set(item.findAll(tag_t, class_=class_t))
                    for promo_title in need_item:  # убран лишний текст
                        if not promo_title.find(tag_extra, class_=class_extra):
                            self.promos.append([promo_title.text, coupon_str])

    def make_menu_str(self):
        ret_str = ""
        for promo in self.promos:
            ret_str += f"{promo[0]} :   {promo[1]} \n"
        if not ret_str:
            ret_str = "нет промокодов для данного поиска\n"
        return f"```\n{ret_str} ```\n"  # строка передается для печати
