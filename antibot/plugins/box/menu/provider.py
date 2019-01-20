from typing import List

import arrow
import requests
from bs4 import BeautifulSoup
from pynject import pynject

from antibot.plugins.box.menu.model import Menu
from antibot.plugins.box.menu.parser import MenuParser


@pynject
class MenuProvider:
    def __init__(self, parser: MenuParser):
        self.parser = parser
        self.menu = None
        self.date = None

    def get(self) -> Menu:
        today = arrow.utcnow().format('dddd D', locale='fr_FR').capitalize()
        if today != self.date:
            self.menu = self.parser.parse(self.fetch_text())
            self.date = today
        return self.menu

    def fetch_text(self) -> List[str]:
        return BeautifulSoup(requests.get('https://www.lesboxdenat.com/').text, 'html.parser').get_text().split('\n')


if __name__ == '__main__':
    menu = MenuProvider(MenuParser())
    print(menu.get())
