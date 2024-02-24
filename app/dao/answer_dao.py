import asyncio

import jsonpickle

from predefined.answer_model import Answer
from common.util import PRCTX


class AnswerDao:
    def __init__(self):
        self.cache: dict[str, Answer] = {}
        self.lock = asyncio.Lock()

    async def get_by_hash(self, hash: str) -> Answer:
        if hash is None:
            return None

        async with self.lock:
            if hash in self.cache:
                return self.cache[hash]
            prctx = PRCTX.get()
            json: str = await prctx.connection.fetchval('select obj from answer where hash = $1', hash)
            if json is None:
                return None
            answer: Answer = jsonpickle.decode(json)
            self.cache[hash] = answer
            return answer

    async def store(self, answer: Answer) -> str:
        if answer is None:
            return None
        json, hash = answer.json()
        async with self.lock:
            if hash in self.cache:
                return hash
            prctx = PRCTX.get()
            await prctx.connection.execute('insert into answer (hash, obj) values ($1, $2) on conflict do nothing', hash, json)
            self.cache[hash] = answer
        return hash
