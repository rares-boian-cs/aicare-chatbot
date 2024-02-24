from predefined.wording_model import Wording


class AnswerItem:
    def __init__(self, ordinal: int, value: int, wording: Wording):
        self.code: str = None
        self.ordinal: int = ordinal
        self.value: int = value
        self.wording: Wording = wording