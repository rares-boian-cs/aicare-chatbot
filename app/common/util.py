import contextvars
import logging.handlers
import os
import sys
import subprocess

from common.config import Config

dev = "--dev" in sys.argv

installation_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

version = subprocess.check_output(['git', '-C', f'{installation_path}', 'describe', '--tags']).strip().decode('utf-8')

config = Config([f'{installation_path}/config/default.ini', f'{installation_path}/config/app.ini'])

log_path = f'{installation_path}/log'
if not os.path.exists(log_path):
    os.mkdir(log_path, 0o700)
log_path += '/aicare.log'

logger = logging.getLogger('app')
logger.setLevel(logging.DEBUG)
logFormatter = logging.Formatter('%(asctime)s:%(threadName)s:%(levelname)s:%(message)s')
fileHandler = logging.handlers.RotatingFileHandler(filename=log_path, encoding='utf-8', mode='a', maxBytes=1024 * 1024 * 200, backupCount=10)
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)

PRCTX: contextvars.ContextVar = contextvars.ContextVar('prctx')

if dev:
    stderrHandler = logging.StreamHandler(sys.stderr)
    stderrHandler.setFormatter(logFormatter)
    logger.addHandler(stderrHandler)


def switch(*args):
    x = args[0]() if callable(args[0]) else args[0]
    a = args[1:]
    els = None
    if len(a) % 2 == 1:
        els = a[-1]
        a = a[:-1]
    for i in range(0, len(a), 2):
        if (callable(a[i]) and a[i](x)) or (not callable(a[i]) and x == a[i]):
            return a[i+1](x) if callable(a[i+1]) else a[i+1]
    return els(x) if callable(els) else els


async def noop():
    pass


def ordinal2string(ordinal: list[int], prefix: str):
    return f'{prefix}:{".".join(str(x) for x in ordinal)}'


def next_ordinal(current: list[int], prefix: str, available: list[str]) -> str:
    def check_descendants(crt: str, n: int) -> str:
        if n == 0:
            return None
        for d in [1, -1]:
            s = f'{crt}.{d}'
            if s in available:
                return s
        for d in [1, -1]:
            s = check_descendants(f'{crt}.{d}', n - 1)
            if s is not None:
                return s
        return None

    depth = 5
    a = current.copy()
    while len(a) > 0:
        y = check_descendants(ordinal2string(a, prefix), depth)
        if y is not None:
            return y
        if a[-1] > 0:
            a[-1] += 1  # sibling
            x = ordinal2string(a, prefix)
            if x in available:
                return x
            y = check_descendants(x, depth)
            if y is not None:
                return y
        a = a[:-1]
        while len(a) > 0 and a[-1] < 0:
            a = a[:-1]
        if len(a) > 0:
            a[-1] += 1
            x = ordinal2string(a, prefix)
            if x in available:
                return x

    return None


def test_next_ordinal():
    for p in [
        [[1], ['c:1.1','c:1.-1','c:1.1.1','c:1.1.1.1','c:1.1.1.1.1','c:1.1.1.1.1.1','c:1.-1.1.-1.1.-1','c:1.1.1.1.1.1.1','c:2','c:2.1','c:2.-1','c:3','c:1.2','c:1.-2','c:2.2','c:2.-2']],
        [[1,-1,1], ['c:1.-1.1.1','c:1.-1.1.-1','c:1.-1.2','c:1.-1.2.1','c:1.-1.2.-1','c:2','c:2.1','c:2.-1','c:1.-1.1.2','c:1.-1.1.-2','c:1.-1.3','c:1.-1.-2','c:1.0','c:1.-2','c:1.1']],
    ]:
        while len(p[1]) > 0:
            print(f'{ordinal2string(p[0], "c")}    {",".join(p[1])}  ->  {next_ordinal(p[0], "c", p[1])}')
            p[1] = p[1][1:]
