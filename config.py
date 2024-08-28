from enum import Enum


class DitConfig(Enum):
    DIT_URL = "https://atvdit.athtem.eei.ericsson.se/api/documents?q=name="
    RETRIES = 3
