from pyckson import no_camel_case


@no_camel_case
class Profile:
    def __init__(self, display_name: str):
        self.display_name = display_name
