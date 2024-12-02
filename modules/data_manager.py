import json
import os
from dataclasses import asdict, is_dataclass
from datetime import datetime
from typing import Optional

from models.data import DataModel, SmtpSettings
from models.keyword_data import KeywordData
from modules import logger


# DB 대신 최근 데이터를 JSON 파일로 관리합니다.
class DataManager:
    _instance = None  # 싱글톤 인스턴스 저장

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            logger.info("DataManager 인스턴스 생성")
            cls._instance = super(DataManager, cls).__new__(cls)
        return cls._instance

    def __init__(
        self,
        file_path="data.json",
    ):
        if not hasattr(self, "initialized"):  # 초기화 방지
            self.file_path = file_path
            self.data = self.load_data()
            self.initialized = True  # 초기화 상태 표시

    # data.json을 다시 읽어서 keyword 데이터를 업데이트합니다.
    def file_load(self):
        # 파일이 존재하면 JSON 로드
        with open(self.file_path, "r") as f:
            loaded_data = json.load(f)
            return DataModel(
                keyword=loaded_data.get("keyword", {}),
                smtp_settings=SmtpSettings(**loaded_data.get("smtp_settings", {})),
            )

    def load_data(self) -> DataModel:
        # .env 파일에서 설정값 읽기
        smtp_settings = SmtpSettings(
            server=os.getenv("SMTP_SERVER", "smtp.kakao.com"),
            port=os.getenv("SMTP_PORT", "465"),
            email=os.getenv("SMTP_EMAIL", ""),
            password=os.getenv("SMTP_PASSWORD", ""),
        )
        logger.info(f"SMTP 설정 완료")
        # 기존 파일이 없으면 초기 데이터 생성
        if not os.path.exists(self.file_path):
            logger.info("새로운 데이터 파일 생성")
            initial_data = {
                "keyword": [],
                "smtp_settings": asdict(smtp_settings),
            }
            with open(self.file_path, "w") as f:
                json.dump(initial_data, f, indent=4)
            return DataModel(smtp_settings=smtp_settings)

        # 파일이 존재하면 JSON 로드
        return self.file_load()

    def update_keyword_data(
        self,
        keyword: str,
        keyword_data: KeywordData = None,
    ) -> KeywordData:
        keyword_data_path = f"{keyword}_data.json"
        data = None
        if os.path.exists(keyword_data_path):
            with open(keyword_data_path, "r") as f:
                existing_data = json.load(f)

            logger.info(f"[{keyword}] 데이터 업데이트: {asdict(keyword_data)}")
            existing_data.update(asdict(keyword_data))
            data = existing_data
        else:
            data = asdict(keyword_data)
            logger.warning(f"[{keyword}] 데이터 파일이 없습니다. 생성합니다. {data}")
            with open(keyword_data_path, "w") as f:
                json.dump(data, f, indent=4)

        # JSON 파일 저장
        with open(keyword_data_path, "w") as f:
            json.dump(data, f, indent=4)

        return keyword_data

    def load_keyword_data(
        self,
        keyword: str,
    ) -> Optional[KeywordData]:
        keyword_data_path = f"{keyword}_data.json"
        if not os.path.exists(keyword_data_path):
            # 빈 형태의 데이터 파일 생성
            empty_data = KeywordData(
                current_id=None,
                current_title=None,
                current_link=None,
                current_price=None,
                current_meta_data=None,
                wdate=datetime.now().isoformat(),
            )
            return self.update_keyword_data(keyword=keyword, keyword_data=empty_data)
        with open(keyword_data_path, "r") as f:
            data = json.load(f)
            return KeywordData(**data)

    def data_cleaner(
        self,
        keywords: list,
    ):
        # 키워드에 존재하지 않는데 존재하는 *_data.json 쓰레기 파일 삭제
        # 현재 경로의 *_data.json 파일 목록 조회
        data_files = [file for file in os.listdir() if file.endswith("_data.json")]
        # 키워드 리스트와 비교
        for data_file in data_files:
            keyword = data_file.replace("_data.json", "")
            if keyword not in keywords:
                logger.info(f"[{keyword}] 데이터 파일 삭제")
                os.remove(data_file)
