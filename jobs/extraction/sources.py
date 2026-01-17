from enum import Enum

class ExtractionType(str, Enum):
    SCRAPY = "scrapy"
    THREADED = "threaded"
    ASYNC = "async"

SOURCES = {
    "linkedin": {"type": ExtractionType.SCRAPY},
    "indeed": {"type": ExtractionType.SCRAPY},
    "remoteok": {"type": ExtractionType.THREADED},
}
