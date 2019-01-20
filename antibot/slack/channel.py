from autovalue import autovalue


@autovalue
class Channel:
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name
