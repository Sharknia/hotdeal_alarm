import json
import os
from dataclasses import asdict, dataclass, field
from typing import Dict, Optional

from models import logger


@dataclass
class SmtpSettings:
    server: str = "smtp.kakao.com"
    port: str = "465"
    email: str = ""
    password: str = ""


@dataclass
class DataModel:
    keyword: Dict[str, dict] = field(default_factory=dict)
    smtp_settings: SmtpSettings = field(default_factory=SmtpSettings)
