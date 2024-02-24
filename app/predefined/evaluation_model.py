import hashlib

import jsonpickle

from common.constant import EvaluationCode
from common.util import next_ordinal, ordinal2string
from predefined.evaluation_item_model import EvaluationItem


class Evaluation:
    def __init__(self, code: EvaluationCode, nickcodes: list[str], name: str, action: str, items: list[EvaluationItem]):
        self.code: EvaluationCode = code
        self.nickcodes: list[str] = nickcodes
        self.name: str = name
        self.action: str = action
        for i in items:
            i.code = self.ord2code(i.ordinal)
        self.items: dict[str, EvaluationItem] = {i.code: i for i in items}

    def ord2code(self, ordinal: list[int]) -> str:
        return ordinal2string(ordinal, self.code.value)

    def get_item_by_ordinal(self, ordinal: list[int]) -> EvaluationItem:
        return self.items[self.ord2code(ordinal)]

    def json(self) -> (str, str):
        j: str = jsonpickle.encode(self, make_refs=False)
        h: str = hashlib.sha1(j.encode('utf-8')).hexdigest()
        return j, h

    def first_item(self):
        return self.get_item_by_ordinal([1])

    def next_item(self, item: EvaluationItem):
        if item.next is not None:
            o = item.next()
            if o is None:
                return None
            c = self.ord2code(o)
            assert c in self.items
            return self.items[c]

        c = next_ordinal(item.ordinal, self.code.value, list(self.items.keys()))
        if c is None:
            return None
        return self.items[c]

    def get_countable_items(self) -> list[EvaluationItem]:
        return list(filter(lambda i: i.countable, self.items.values()))