import asyncio

import jsonpickle

from predefined.evaluation_predefined import Evaluations
from predefined.evaluation_model import Evaluation
from predefined.evaluation_item_model import EvaluationItem
from common.util import PRCTX


class EvaluationDao:
    def __init__(self):
        self.cache: dict[str, Evaluation] = {}
        self.lock = asyncio.Lock()

    async def get_by_hash(self, hash: str) -> Evaluation:
        async with self.lock:
            if hash not in self.cache:
                prctx = PRCTX.get()
                json: str = await prctx.connection.fetchval('select obj from evaluation where hash = $1', hash)
                e: Evaluation = jsonpickle.decode(json)
                pe: Evaluation = Evaluations[e.code.name].value
                for ei in e.items.values():
                    pei: EvaluationItem = pe.items[ei.code]
                    ei.action = pei.action
                    ei.next = pei.next
                    ei.nextord = pei.nextord
                self.cache[hash] = e

            return self.cache[hash]

    async def store(self, evaluation: Evaluation):
        json, hash = evaluation.json()
        async with self.lock:
            if hash in self.cache:
                return
            prctx = PRCTX.get()
            await prctx.connection.execute('insert into evaluation (hash, obj) values ($1, $2) on conflict do nothing', hash, json)
            self.cache[hash] = evaluation
