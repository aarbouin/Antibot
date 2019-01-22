import re
from enum import Enum

from pynject import pynject

from antibot.plugins.box.menu.model import BoxType, Box, MenuBuilder, Soup, Salad, Cheese, Dessert, Drink, Menu

box_type_pattern = re.compile(r'^(NOUVEAU : )?Box\s+([\w\s]+)\s*([0-9\(\)]*)?\s*:\s*([0-9.]+) ?€', flags=re.IGNORECASE)
box_soupe_pattern = re.compile(r'Soupe\s*:\s*([0-9.]+) ?€', flags=re.IGNORECASE)
salad_pattern = re.compile(r'Salade Verte\s*:\s*([0-9.]+) ?€', flags=re.IGNORECASE)
allergen_pattern = re.compile(r'(\([0-9]+\))')
fromage_pattern = re.compile(r'Portion de Fromage\s*:\s*([0-9.]+) ?€')
yaourt_pattern = re.compile(r'Yaourts\s+\((.*)\)')
fromage_blanc_pattern = re.compile(r'Fromage\sBlanc(.*)\((.*)\)')
choice_drink = re.compile(r'(.*)\((\w+)\s*ou\s*(\w+)\)')


class ParserState(Enum):
    NONE = 0
    BOX = 1
    SOUP = 2
    SALAD = 3
    FROMAGE = 4
    DESSERT = 5
    DRINK = 6


def iter_lines(text):
    full_line = ''
    for line in text:
        line = line.replace('\xa0', ' ').strip()
        if line == '' and full_line != '':
            yield full_line
            full_line = ''
        elif line != '':
            full_line += line


def cleanup_allergen(name):
    name = re.sub(allergen_pattern, '', name)
    name = re.sub(r' {2,}', ' ', name)
    return name


@pynject
class MenuParser:
    def __init__(self):
        self.menu = MenuBuilder()
        self.state = ParserState.NONE
        self.box_type = None
        self.box_price = 0
        self.full_line = ''
        self.old_full_line = ''

    def reset(self):
        self.menu = MenuBuilder()

    def parse(self, text) -> Menu:
        for line in iter_lines(text):
            if len(line) == 0:
                continue
            if self.compute_state(line):
                continue

            if self.state == ParserState.BOX:
                if line.lower() == 'ou':
                    if self.box_type == BoxType.FROIDE:
                        self.old_full_line = self.full_line
                        self.full_line = ''
                    else:
                        self.update_state(ParserState.BOX)
                    continue
                elif line.lower().startswith('avec') and self.old_full_line != '':
                    self.old_full_line += ' ' + line

            if self.state == ParserState.DESSERT:
                self.process_dessert(line)

            self.full_line += ' ' + line

        return self.menu.build()

    def compute_state(self, line):
        if box_type_pattern.match(line) is not None:
            self.update_state(ParserState.BOX)
            self.compute_box_type(line)
            return True
        if box_soupe_pattern.match(line) is not None:
            self.update_state(ParserState.SOUP)
            self.box_price = float(box_soupe_pattern.match(line).group(1))
            return True
        if salad_pattern.match(line) is not None:
            self.update_state(ParserState.SALAD)
            self.box_price = float(salad_pattern.match(line).group(1))
            return True
        if fromage_pattern.match(line) is not None:
            self.update_state(ParserState.FROMAGE)
            self.box_price = float(fromage_pattern.match(line).group(1))
            return True
        if line.lower().startswith('desserts'):
            self.update_state(ParserState.DESSERT)
            return True
        if line.lower().startswith('boissons'):
            self.update_state(ParserState.DRINK)
            return True
        if line.lower().startswith('formules'):
            self.update_state(ParserState.NONE)
            return True
        return False

    def compute_box_type(self, line):
        match = box_type_pattern.match(line)
        for box_type in BoxType:
            if box_type.value == 'Box ' + match.group(2).strip():
                self.box_type = box_type
                break
        else:
            self.box_type = BoxType.UNKNOWN
        self.box_price = float(match.group(4))

    def update_state(self, new_state):
        if self.state == ParserState.BOX:
            self.add_box(self.full_line)
            if self.box_type == BoxType.FROIDE and self.old_full_line != '':
                self.add_box(self.old_full_line)
        if self.state == ParserState.SOUP:
            self.set_soup(self.full_line)
        if self.state == ParserState.SALAD:
            self.set_salad()
        if self.state == ParserState.FROMAGE:
            self.set_cheese(self.full_line)
        if self.state == ParserState.DRINK:
            self.set_drinks(self.full_line)
        self.state = new_state
        self.full_line = ''

    def add_box(self, name):
        name = cleanup_allergen(name).strip()
        box = Box(self.box_type, name, self.box_price)
        self.menu.add_box(box)

    def set_soup(self, name):
        name = cleanup_allergen(name).strip()
        self.menu.set_soup(Soup(name, self.box_price))

    def set_salad(self):
        self.menu.set_salad(Salad(self.box_price))

    def set_cheese(self, name):
        names = name.split('ou')
        names = map(str.strip, names)
        for name in names:
            self.menu.add_cheese(Cheese(name, self.box_price))

    def process_dessert(self, line):
        line = cleanup_allergen(line).strip()
        if yaourt_pattern.match(line) is not None:
            flavors = yaourt_pattern.match(line).group(1).split(',')
            flavors = map(str.strip, flavors)
            self.menu.add_dessert(Dessert('Yaourt', list(flavors), 1.0))
        elif fromage_blanc_pattern.match(line) is not None:
            flavors = fromage_blanc_pattern.match(line).group(2).split(',')
            flavors = list(map(str.strip, flavors))
            flavors += ['Nature', 'Sucre']
            self.menu.add_dessert(Dessert('Fromage blanc', list(flavors), 1.0))
        else:
            self.menu.add_dessert(Dessert(line, [], 1.0))

    def set_drinks(self, full_line):
        drinks = full_line.split(',')
        for drink in drinks:
            if choice_drink.match(drink):
                match = choice_drink.match(drink)
                name = match.group(1) + match.group(2)
                self.menu.add_drink(Drink(name, 1.0))
                name = match.group(1) + match.group(3)
                self.menu.add_drink(Drink(name, 1.0))
            else:
                self.menu.add_drink(Drink(drink.strip(), 1.0))
