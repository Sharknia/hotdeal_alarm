import json
import os
from datetime import datetime

from modules import logger


# DB 대신 최근 데이터를 JSON 파일로 관리합니다.
class DataManager:
    _instance = None  # 싱글톤 인스턴스 저장

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            logger.info("DataManager 인스턴스 생성")
            cls._instance = super(DataManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, file_path="data.json"):
        if not hasattr(self, "initialized"):  # 초기화 방지
            self.file_path = file_path
            self.data = self.load_data()
            self.initialized = True  # 초기화 상태 표시

    def load_data(self):
        # .env 파일에서 설정값 읽기
        logger.info(f"환경 변수 확인: KEYWORD={os.getenv('KEYWORD')}")
        keyword = os.getenv("KEYWORD", "")
        smtp_server = os.getenv("SMTP_SERVER", "smtp.kakao.com")
        smtp_port = os.getenv("SMTP_PORT", "465")
        smtp_email = os.getenv("SMTP_EMAIL", "")
        smtp_password = os.getenv("SMTP_PASSWORD", "")
        logger.info("환경 변수 로드: %s, %s", keyword, smtp_email)
        # 기존 파일이 없으면 환경 변수 기반 초기 데이터 생성
        if not os.path.exists(self.file_path):
            logger.info("새로운 데이터 파일 생성")
            return {
                "keyword": keyword,
                "current_title": "",
                "current_id": "",
                "current_link": "",
                "current_price": "",
                "current_meta_data": "",
                "wdate": "",
                "smtp_settings": {
                    "server": smtp_server,
                    "port": smtp_port,
                    "email": smtp_email,
                    "password": smtp_password,
                },
            }

        # 파일이 존재하면 JSON 로드
        with open(self.file_path, "r") as f:
            return json.load(f)

    def save_data(self):
        with open(self.file_path, "w") as f:
            json.dump(self.data, f, indent=4)

    def update_data(
        self,
        current_id=None,
        current_title=None,
        current_link=None,
        current_price=None,
        current_meta_data=None,
    ):
        self.data["current_id"] = current_id
        self.data["current_title"] = current_title
        self.data["current_link"] = current_link
        self.data["current_price"] = current_price
        self.data["current_meta_data"] = current_meta_data
        self.data["wdate"] = datetime.now().isoformat()
        self.save_data()
