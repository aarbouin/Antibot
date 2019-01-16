from pynject import pynject

from antibot.decorators import command
from antibot.domain.message import Message
from antibot.domain.plugin import AntibotPlugin
from antibot.domain.user import User
from antibot.plugins.menu.provider import MenuProvider
from antibot.storage import StorageFactory


class PointCalculator:
    def __init__(self, menu):
        self.menu = menu

    def get(self, picks):
        price = 0
        for box in self.menu['boxs']:
            if picks['box'] == box['name']:
                price += box['price'] * 10
                break
        else:
            raise ValueError('could not find box {} in menu'.format(picks['box']))

        price += len(picks['desserts']) * 10
        price += len(picks['boissons']) * 10
        points = 85 - price
        return int(points)


@pynject
class Box(AntibotPlugin):
    def __init__(self, menu_provider: MenuProvider):
        super().__init__('Box')
        self.menu_provider = menu_provider

    @command('/box/menu')
    def display_menu(self, user: User):
        menu = self.menu_provider.get()
        date = self.menu_provider.date
        text = '*Menu du {}*\n'.format(date)
        for box in menu.boxes:
            text += '* {} : {} - {}€\n'.format(box.box_type.value, box.name, box.price)
        if menu.soup is not None:
            text += '* Soupe : {} - {}€'.format(menu.soup.name, menu.soup.price)
        text += '\n*Desserts :*\n'
        for dessert in menu.desserts:
            if len(dessert.flavors) > 0:
                text += '* {} ({})\n'.format(dessert.name, ', '.join(dessert.flavors))
            else:
                text += '* {}\n'.format(dessert.name)
        return Message(text)
