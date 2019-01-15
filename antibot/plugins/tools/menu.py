import re

import arrow
import requests
from bs4 import BeautifulSoup

box_type_pattern = re.compile(r'^(NOUVEAU : )?Box\s+([\w\s]+)\s*:\s*([0-9.]+) ?€', flags=re.IGNORECASE)
box_noprice_pattern = re.compile(r'^Box\s+([\w\s]+)\s*:')
yaourt_pattern = re.compile(r'Yaourts\s+\((.*)\)')
fromage_pattern = re.compile(r'Fromage\sBlanc(.*)\((.*)\)')
box_with_price = re.compile('(.*)\s*:\s*([0-9.]+)€')


class MenuParser:
    def __init__(self, today):
        self.today = today
        self.start = False
        self.stop = False
        self.in_desserts = False
        self.in_boissons = False
        self.in_fromage = False
        self.in_soupe = False
        self.box_type = None
        self.box_price = None
        self.current_box_items = []
        self.boxes = []
        self.desserts = []
        self.boissons = []
        self.fromages = []
        self.soupe = None

    def parse(self, text):
        full_line = ''
        for line in text:
            if self.stop:
                break
            line = line.strip()
            line = line.replace('\xa0', ' ')
            if not self.start:
                self.find_start(line)
                if not self.start:
                    continue
            full_line += line
            if len(line) == 0 and len(full_line) != 0:
                self.parse_line(full_line)
                full_line = ''

    def find_start(self, line: str):
        if line.startswith("Box Chaude"):
            self.start = True

    def parse_line(self, line: str):
        line = re.sub(r'\(([0-9]+)\)', '', line)
        if line.startswith('Allergènes') or line.startswith('Formules'):
            self.stop = True
        elif line.startswith('Desserts'):
            self.save_box()
            self.in_desserts = True
        elif line.startswith('Boissons'):
            self.in_desserts = False
            self.in_boissons = True
        elif line.startswith('Portion de Fromage'):
            self.in_fromage = True
        elif "Soupe" in line:
            self.save_box()
            self.in_soupe = True
        elif self.in_desserts:
            self.find_dessert(line)
        elif self.in_boissons:
            self.find_boissons(line)
        elif self.in_fromage:
            return
        elif self.in_soupe:
            self.find_soupe()
        elif line.startswith('Box') or line.startswith('NOUVEAU : Box') or line.startswith('Nouveau : Box'):
            if len(self.current_box_items) != 0:
                self.save_box()
            m = box_type_pattern.search(line)
            if m:
                box_name = 'Box ' + m.group(2).strip()
                self.box_type = box_name
                self.box_price = float(m.group(3).strip())
                return
            m = box_noprice_pattern.search(line)
            if m:
                box_name = 'Box ' + m.group(1).strip()
                self.box_type = box_name
                self.box_price = 0
        elif line == 'Ou' or line == 'ou':
            self.save_box()
        elif self.box_type is not None:
            self.current_box_items.append(line)

    def save_box(self):
        if self.box_type is None:
            return
        box_name = self.box_type + ' : ' + ' '.join(self.current_box_items)
        box_price = self.box_price
        if box_price == 0:
            m = box_with_price.search(box_name)
            if m:
                box_name = m.group(1).strip()
                box_price = float(m.group(2).strip())
            else:
                box_price = 8.5
        self.boxes.append({'name': box_name, 'price': box_price})
        self.current_box_items = []
        self.box_type = None

    def find_soupe(self, line: str):
        

    def find_dessert(self, line: str):
        if line.startswith('Yaourts'):
            m = yaourt_pattern.match(line)
            if m:
                flavours = m.group(1).split(',')
                flavours = [f.strip() for f in flavours]
                self.desserts.append(('Yaourt', flavours))
        elif line.startswith('Fromage'):
            m = fromage_pattern.match(line)
            if m:
                flavours = m.group(2).split(',')
                flavours = [f.strip() for f in flavours]
                self.desserts.append(('Fromage Blanc', ['Nature', 'Sucre'] + flavours))
        else:
            self.desserts.append((line, []))

    def find_boissons(self, line: str):
        boissons = line.split(', ')
        boissons = [b.strip() for b in boissons]
        boissons = list(filter(lambda b: 'Normal' not in b and 'Light' not in b, boissons))
        self.boissons = boissons + ['Coca Normal', 'Coca Zéro', 'Coca light']


if __name__ == '__main__':
    today = arrow.utcnow().format('dddd D', locale='fr_FR').capitalize()
    text = BeautifulSoup(requests.get('https://www.lesboxdenat.com/').text, 'html.parser').get_text().split('\n')
    parser = MenuParser(today)
    parser.parse(text)
    print('### boxes')
    for b in parser.boxes:
        print('{} - {:.2f}€'.format(b['name'], b['price']))
    print('### dessert')
    for d, f in parser.desserts:
        if len(f) > 0:
            print('{} : {}'.format(d, ', '.join(f)))
        else:
            print(d)
    print('### boissons')
    for b in parser.boissons:
        print(b)
