import random
import re

from common.util import PRCTX


class Wording:
    def __init__(self, content: str, alternatives: list[str]):
        self.content: str = content
        self.alternatives: list[str] = alternatives
        self.all: list[str] = [self.content] + self.alternatives
        self.normalized_content: str = self.normalize(self.content)
        self.normalized_alternatives: list[str] = list(map(lambda s: self.normalize(s), alternatives))
        self.normalized_all: list[str] = [self.normalized_content] + self.normalized_alternatives

    def normalize(self, s: str) -> str:
        return re.sub(r'[ \t]+', ' ', re.sub(r'^[ \t]*|[ \t]*$', '', s)).lower()

    def is_exactly(self, text: str):
        return self.normalize(text) in self.normalized_all

    def appears_in(self, text: str):
        s = self.normalize(text)
        for w in self.normalized_all:
            p = f'\b{w}\b'
            if re.match(p, s):
                return True
        return False

    def format(self, s: str) -> str:
        prctx = PRCTX.get()
        return s.format(**{'topic-score': prctx.topic.score, 'evaluation-code': re.sub("-CO$", "", prctx.topic.evaluation.code.value.upper())})

    def get_random(self) -> str:
        return self.format(random.choice(self.all))

    def get_permuted(self, offset: int, steps: int) -> str:
        n = len(self.all)
        k = (offset + steps * 173) % n
        return self.format(self.all[k])

    def get_random_normalized(self) -> str:
        return self.format(random.choice(self.normalized_all))

    def get_content(self) -> str:
        return self.format(self.content)