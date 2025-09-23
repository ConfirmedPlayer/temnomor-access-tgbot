from dataclasses import asdict, dataclass

import orjson

from core.types import StringifiedUUID, UnixTimeStampInMilliseconds


@dataclass(slots=True)
class XUISettings:
    id: StringifiedUUID
    email: str
    subId: str
    flow: str = 'xtls-rprx-vision'
    limitIp: int = 1
    totalGB: int = 0
    expiryTime: UnixTimeStampInMilliseconds = 0
    enable: bool = True
    tgId: str = ''
    comment: str = ''
    reset: int = 0
    created_at: int = 0
    updated_at: int = 0

    def __str__(self) -> str:
        settings = {
            'clients': [{key: value for key, value in asdict(self).items()}]
        }
        return orjson.dumps(settings).decode()
