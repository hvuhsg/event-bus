from typing import Union, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ConsumeConfig:
    offset: Union[int, None] = 0
    from_date: Optional[datetime] = None
