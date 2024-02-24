import hashlib

import jsonpickle

from common.constant import AnswerCode
from predefined.answer_item_model import AnswerItem


class Answer:
    def __init__(self, code: AnswerCode, items: list[AnswerItem]):
        self.code: AnswerCode = code
        for i in items:
            i.code = self.ordinal2code(i.ordinal)
        self.sorted_items = items
        self.items: dict[str, AnswerItem] = {i.code: i for i in items}

    def ordinal2code(self, ordinal: int) -> str:
        return f'{self.code.value}:{ordinal}'

    def get_item_by_ordinal(self, ordinal: int) -> AnswerItem:
        return self.items[self.ordinal2code(ordinal)]

    def get_item_by_text(self, text: str) -> AnswerItem:
        for i in self.items.values():
            if i.wording.equals(text):
                return i
        return None

    def json(self) -> (str, str):
        j: str = jsonpickle.encode(self, make_refs=False)
        h: str = hashlib.sha1(j.encode('utf-8')).hexdigest()
        return j, h

    def get_bullets(self) -> str:
        text = ''
        bullet = 'a'
        for i in self.sorted_items:
            s = i.wording.content
            s = s[0].upper() + s[1:]
            text = text + f'  {bullet})  {s}\n'
            bullet = chr(ord(bullet) + 1)
        return text
