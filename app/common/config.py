import configparser


class Config:
    def __init__(self, files: list[str]):
        self.kv: dict[str, str] = {}
        for fn in files:
            parser = configparser.ConfigParser()
            parser.read(fn)
            for section in parser.sections():
                for (key, value) in parser.items(section):
                    self.kv[f'{section}.{key}'] = value

    def get_str(self, section: str, key: str) -> str:
        k = f'{section}.{key}'
        if k not in self.kv:
            return None
        return self.kv[k]

    def get_int(self, section: str, key: str) -> int:
        v = self.get_str(section, key)
        return int(v) if v is not None else None

    def get_float(self, section: str, key: str) -> float:
        v = self.get_str(section, key)
        return float(v) if v is not None else None
