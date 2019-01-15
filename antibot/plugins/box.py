import operator
from datetime import datetime
from uuid import uuid4

import arrow
import requests
from bottle import request, abort
from bs4 import BeautifulSoup

from antibot import addon
from antibot.addons.bottle import template, jsify
from antibot.addons.descriptors import ButtonPos
from antibot.client import HipchatClient
from antibot.decorators import room, glance, dialog, button, ws, panel, daily
from antibot.domain.glance import GlanceView, GlanceStatus, GlanceColor
from antibot.domain.plugin import AntibotPlugin
from antibot.domain.room import Room
from antibot.domain.user import User
from antibot.repository.users import UsersRepository
from antibot.storage import StorageFactory
from plugins.tools.menu import MenuParser


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


@addon('Box de Nat', 'box stuff')
@room('Les Box de Nat')
class Box(AntibotPlugin):
    def __init__(self, client: HipchatClient, storage: StorageFactory, users_repository: UsersRepository):
        super().__init__('Box')
        self.users_repository = users_repository
        self.storage = storage.get(self.__class__)
        self.client = client
        orders = self.storage.get('orders', [])
        self.storage.save('orders', orders)
        points = self.storage.get('points', {})
        self.storage.save('points', points)
        prefs = self.storage.get('prefs', {})
        self.storage.save('prefs', prefs)
        history_order = self.storage.get('history_order', {})
        self.storage.save('history_order', history_order)
        history_menu = self.storage.get('history_menu', [])
        self.storage.save('history_menu', history_menu)
        self.menu = None
        self.room = self.client.get_room('Les Box de Nat')

    @glance('Commander une Box', 'box.png')
    def glance_box(self):
        return GlanceView('Menu')

    @dialog('Commander une Box', size=('800px', '90%'))
    @button(ButtonPos.PRIMARY, 'validate', 'Valider')
    def panel_box(self, user: User):
        menu = self.get_menu()
        user_orders = [order for order in self.storage.get('orders') if order['from'] == user.api_id]
        prefs = self.storage.get('prefs').get(str(user.api_id), {'couverts': False})
        return template('box/menu.tpl', menu=jsify(menu), orders=jsify(user_orders), prefs=jsify(prefs))

    def get_menu(self):
        today = arrow.utcnow().format('dddd D', locale='fr_FR').capitalize()
        text = BeautifulSoup(requests.get('https://www.lesboxdenat.com/').text, 'html.parser').get_text().split('\n')
        parser = MenuParser(today)
        parser.parse(text)
        menu = {'boxs': parser.boxes,
                'boissons': parser.boissons,
                'desserts': []}
        for dessert, flavors in parser.desserts:
            menu['desserts'].append({'name': dessert, 'flavors': flavors})
        self.menu = menu
        return menu

    def add_points(self, user, to_add):
        with self.storage['points'] as points:
            user_p = points.get(str(user.api_id), -100)
            user_p += to_add
            points[str(user.api_id)] = user_p

    @ws('/boxs/orders', 'POST')
    def put_order(self, user: User, room: Room):
        order = request.json
        order['from'] = user.api_id
        order['id'] = uuid4().hex
        order['points'] = PointCalculator(self.menu).get(order)
        self.add_points(user, order['points'])
        with self.storage['orders'] as orders:
            orders.append(order)
        with self.storage['prefs'] as prefs:
            for key, value in order['prefs'].items():
                prefs.setdefault(str(user.api_id), {})[key] = value
        self.display_order(order, room, user)
        self.client.update_glance(self.glance_orders, room)
        self.client.update_glance_for_user(self.glance_points, user, room)
        with self.storage['history_order'] as history:
            history.setdefault(str(user.api_id), []).append({'name': user.name, 'date': datetime.now(), 'order': order})

    def display_order(self, order, room: Room, user: User):
        options = []
        for dessert in order['desserts']:
            text = dessert['name']
            if len(dessert['flavors']) > 0:
                flavors = ' > '.join(dessert['flavors'])
                text += ' ' + flavors
            options.append(text)
        for boisson in order['boissons']:
            options.append(boisson)
        options = ['<li>{}</li>'.format(o) for o in options]
        message = '<b>{}</b> : {} points<br/>{}<ul>{}</ul>'.format(user.name, order['points'], order['box'],
                                                                   ''.join(options))
        self.client.send_html_message(room, message)

    @ws('/boxs/orders/<id>', 'DELETE')
    def delete_order(self, id: str, user: User, room: Room):
        matching_orders = [order for order in self.storage.get('orders') if order['id'] == id]
        if len(matching_orders) == 0:
            abort(404)
        order = matching_orders[0]
        if order['from'] != user.api_id:
            abort(401)
        self.add_points(user, -1 * order['points'])
        with self.storage['orders'] as orders:
            orders.remove(order)
        self.client.send_text_message(room, '{} a annulé une commande'.format(user.name))
        self.client.update_glance(self.glance_orders, room)
        self.client.update_glance_for_user(self.glance_points, user, room)

    @glance('Commandes', 'box.png')
    def glance_orders(self):
        nb = len(self.storage.get('orders'))
        color = GlanceColor.success if self.storage.get('called', False) or nb == 0 else GlanceColor.error
        return GlanceView('Commandes', GlanceStatus(color, str(nb)))

    @dialog('Commandes', size=('800px', '90%'))
    @button(ButtonPos.PRIMARY, 'validate', 'J\'ai Appelé')
    @button(ButtonPos.SECONDARY, 'cancel', 'Close')
    def dialog_orders(self):
        orders = self.storage.get('orders')
        couverts = 0
        for order in orders:
            order['user_name'] = self.users_repository.by_id(order['from']).name
        with self.storage['prefs'] as prefs:
            for order in orders:
                if str(order['from']) in prefs and prefs[str(order['from'])].get('couverts', False) is True:
                    couverts += 1
        return template('box/orders.tpl', orders=jsify(orders), couverts=couverts)

    @ws('/boxs/orders', 'GET')
    def get_orders(self):
        orders = self.storage.get('orders')
        for order in orders:
            order['user_name'] = self.users_repository.by_id(order['from']).name
        return {'orders': orders}

    @ws('/boxs/orders-commit', 'POST')
    def call_done(self, user: User, room: Room):
        self.client.send_text_message(room, '@here Et voilà, on a les boites !'.format(user.name))
        self.storage.save('called', True)

    @glance('Points', 'box.png')
    def glance_points(self, user: User):
        for uid, points in self.storage.get('points').items():
            if int(uid) == user.api_id:
                return GlanceView('Points', GlanceStatus(GlanceColor.success, str(points)))
        return GlanceView('Points')

    @panel('Points')
    def panel_points(self):
        return template('box/points.tpl', points=jsify(self.compute_points()))

    @ws('/boxs/points', 'GET')
    def get_points(self):
        return {'points': self.compute_points()}

    @ws('/boxs/freebox', 'POST')
    def freebox(self, room: Room):
        user = None
        points = None
        orders = [o['from'] for o in self.storage.get('orders')]
        for id, p in self.storage.get('points').items():
            if int(id) in orders:
                if points is None or p > points:
                    user = id
                    points = p
        user = self.users_repository.by_id(int(user))
        self.add_points(user, -85)
        self.client.update_glance_for_user(self.glance_points, user, room)
        self.client.send_text_message(room, 'Une box gratuite pour @{}'.format(user.mention))

    def compute_points(self):
        user_points = []
        for id, p in self.storage.get('points').items():
            user = self.users_repository.by_id(int(id))
            if user is not None:
                user_points.append([user.name, p])
        user_points = sorted(user_points, key=operator.itemgetter(1), reverse=True)
        return user_points

    @daily('00:00')
    def reset_daily(self):
        order_users = set([order['from'] for order in self.storage.get('orders')])
        self.storage.save('orders', [])
        self.storage.save('called', False)
        for user in order_users:
            user = self.users_repository.by_id(user)
            self.client.update_glance_for_user(self.glance_orders, user, self.room)
        with self.storage['history_menu'] as history:
            history.append(self.menu)

    @daily('10:00')
    def ping_daily(self):
        if len(self.storage.get('orders')) > 0:
            self.client.send_text_message(self.room, '@here pensez à passer commande !')
