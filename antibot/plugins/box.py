from pynject import pynject

from antibot.decorators import command
from antibot.domain.message import Message
from antibot.domain.plugin import AntibotPlugin
from antibot.domain.user import User
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
    def __init__(self, storage: StorageFactory):
        super().__init__('Box')

    @command('/box/menu')
    def display_menu(self, user: User):
        return Message('coucou {}'.format(user.display_name))
