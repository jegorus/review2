import requests
from bs4 import BeautifulSoup
import re

import myConfig


class RequestPromoClass:
    response = None
    new_items = None
    promo_all = True
    soup = None  # содержит html додо

    tag_promo = 'div'
    class_promo = 'block block_dv-large block_mv-rounded coupon'
    promos = []

    def __init__(self):
        self.get_request(myConfig.PROMO_LINK)
        self.soup_find_promo('')

    def get_request(self, link):
        session = requests.Session()
        session.headers.update({'User-Agent': myConfig.USER_AGENT})

        self.response = session.get(link)
        self.response.raise_for_status()
        if self.response.ok:
            self.soup = BeautifulSoup(self.response.content, 'html.parser')

    # новая версия: 2024
    def soup_find_promo(self, find_str):
        items = self.soup.find("script", {"id": "vike_pageContext"})
        self.promos = [(promo[1], promo[0]) for promo in re.findall(r'"promoCode":"(\w+)","title":"([^"\\]+)', items.string)]
        if not self.promo_all:
            self.promos = [prom for prom in self.promos if re.search(find_str, prom[0])]

    def make_menu_str(self):
        ret_str = ""
        for promo in self.promos:
            ret_str += f"{promo[0]} :   {promo[1]} \n"
        if not ret_str:
            ret_str = "нет промокодов для данного поиска\n"
        return f"```\n{ret_str} ```\n"  # строка передается для печати
