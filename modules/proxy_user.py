from typing import List
from dataclasses import dataclass, field


@dataclass
class ProxyUser:
    username: str
    password: str
    access_level: int = field(default=0)
    id: str = field(default=False)


proxy_users: List[ProxyUser] = []
