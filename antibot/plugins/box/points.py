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
