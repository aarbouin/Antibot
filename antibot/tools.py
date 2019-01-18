from inspect import signature


def updater(cls):
    attributes = [name for name in signature(cls.__init__).parameters.keys() if name != 'self']

    def update(self, **kwargs) -> cls:
        cls_args = {attr: getattr(self, attr) for attr in attributes}
        for k, v in kwargs.items():
            cls_args[k] = v
        return cls(**cls_args)

    setattr(cls, 'update', update)

    return cls
