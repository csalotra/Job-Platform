class BaseExtractor:
    source: str

    def run(self) -> list[dict]:
        raise NotImplementedError