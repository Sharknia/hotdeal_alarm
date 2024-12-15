from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional


@dataclass
class KeywordData:
    current_id: Optional[str] = None
    current_title: Optional[str] = None
    current_link: Optional[str] = None
    current_price: Optional[str] = None
    current_meta_data: Optional[str] = None
    wdate: str = datetime.now().isoformat()
