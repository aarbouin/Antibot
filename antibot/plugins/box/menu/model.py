from enum import Enum
from typing import List, Optional, Iterator

from autovalue import autovalue


class BoxType(Enum):
    CHAUDE = 'Box Chaude'
    PATES = 'Box Pâtes'
    VEGE = 'Box Chaude Végétarienne'
    FROIDE = 'Box Froide'
    SALADE = 'Box Salade'
    UNKNOWN = 'Box ???'


@autovalue
class Box:
    def __init__(self, box_type: BoxType, name: str, price: float):
        self.box_type = box_type
        self.name = name
        self.price = price

    def __str__(self):
        return '{} : {}'.format(self.box_type.value, self.name, self.price)


@autovalue
class Soup:
    def __init__(self, name: str, price: float):
        self.name = name
        self.price = price

    def __str__(self):
        return '{} : {}'.format('Soupe', self.name, self.price)


@autovalue
class Salad:
    def __init__(self, price: float):
        self.price = price

    def __str__(self):
        return '{} - {}€'.format('Salade Verte', self.price)


@autovalue
class Cheese:
    def __init__(self, name: str, price: float):
        self.name = name
        self.price = price


@autovalue
class DessertWithFlavor:
    def __init__(self, name: str, flavor: Optional[str], price: float):
        self.name = name
        self.flavor = flavor
        self.price = price

    def __str__(self):
        if self.flavor is None:
            return self.name
        else:
            return '{} {}'.format(self.name, self.flavor)


@autovalue
class Dessert:
    def __init__(self, name: str, flavors: List[str], price: float):
        self.name = name
        self.flavors = flavors
        self.price = price

    def with_flavor(self, flavor: Optional[str]):
        return DessertWithFlavor(self.name, flavor, self.price)

    def iter_flavors(self) -> Iterator[DessertWithFlavor]:
        for flavor in self.flavors:
            yield self.with_flavor(flavor)


@autovalue
class Drink:
    def __init__(self, name: str, price: float):
        self.name = name
        self.price = price

    def __str__(self):
        return self.name


@autovalue
class Menu:
    def __init__(self, boxes: List[Box], soup: Optional[Soup], salad: Optional[Salad], cheeses: List[Cheese],
                 desserts: List[Dessert], drinks: List[Drink]):
        self.boxes = boxes
        self.soup = soup
        self.salad = salad
        self.cheeses = cheeses
        self.desserts = desserts
        self.drinks = drinks

    def all_desserts(self) -> Iterator[DessertWithFlavor]:
        for dessert in self.desserts:
            if len(dessert.flavors) > 0:
                yield from dessert.iter_flavors()
            else:
                yield dessert.with_flavor(None)


class MenuBuilder:
    def __init__(self):
        self.boxes = []
        self.soup = None
        self.salad = None
        self.cheeses = []
        self.desserts = []
        self.drinks = []

    def add_box(self, box: Box):
        self.boxes.append(box)

    def set_soup(self, soup: Soup):
        self.soup = soup

    def set_salad(self, salad: Salad):
        self.salad = salad

    def add_cheese(self, cheese: Cheese):
        self.cheeses.append(cheese)

    def add_dessert(self, dessert: Dessert):
        self.desserts.append(dessert)

    def add_drink(self, drink: Drink):
        self.drinks.append(drink)

    def build(self) -> Menu:
        return Menu(self.boxes, self.soup, self.salad, self.cheeses, self.desserts, self.drinks)
