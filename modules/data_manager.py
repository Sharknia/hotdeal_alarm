import json
import os
from dataclasses import asdict
from datetime import datetime
from typing import Dict

from models.data import DataModel, SmtpSettings
from models.keyword_data import KeywordData
from modules import logger


class DataManager:
    _instance = None  # 싱글톤 인스턴스 저장

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            logger.info("DataManager 인스턴스 생성")
            cls._instance = super(DataManager, cls).__new__(cls)
        return cls._instance

    def __init__(
        self,
        file_path="data/data.json",
    ):
        self.keyword_data_by_site: Dict[str, KeywordData] = {}
        if not hasattr(self, "initialized"):  # 초기화 방지
            self.file_path = file_path
            self.ensure_data_folder()  # 폴더 확인 및 생성
            self.data = self.load_data()
            self.initialized = True  # 초기화 상태 표시

    # data.json 파일 저장 경로의 폴더가 없으면 생성
    def ensure_data_folder(self):
        folder = os.path.dirname(self.file_path)  # 파일 경로에서 폴더 추출
        if not os.path.exists(folder):
            logger.info(f"데이터 폴더가 존재하지 않아 생성: {folder}")
            os.makedirs(folder)

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
        sitename: str,
        keyword_data: KeywordData = None,
    ) -> KeywordData:
        keyword_data_path = f"data/{keyword}_data.json"
        data = {}

        # 기존 데이터 로드
        if os.path.exists(keyword_data_path):
            with open(keyword_data_path, "r") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    logger.error(
                        f"[{keyword}] 데이터 파일이 손상되었습니다. 새로 생성합니다."
                    )
                    data = {}

        # sitename 기반 데이터 업데이트
        data[sitename] = asdict(keyword_data)
        logger.info(f"[{keyword}] 데이터 업데이트 - {sitename}: {data[sitename]}")

        # JSON 파일 저장
        with open(keyword_data_path, "w") as f:
            json.dump(data, f, indent=4)

        return keyword_data

    def load_keyword_data(
        self,
        keyword: str,
        sitename: str,
    ) -> KeywordData:
        keyword_data_path = f"data/{keyword}_data.json"

        if not os.path.exists(keyword_data_path):
            logger.info(
                f"[{keyword}] 데이터 파일이 존재하지 않습니다: {keyword_data_path}"
            )
            # 빈 데이터 생성
            empty_data = self._create_empty_keyword_data()
            self.keyword_data_by_site[sitename] = empty_data
            return self.update_keyword_data(
                keyword=keyword, keyword_data=empty_data, sitename=sitename
            )

        with open(keyword_data_path, "r") as f:
            data = json.load(f)
            # 파일은 있는데 sitename에 해당하는 데이터가 없는 경우
            if sitename not in data:
                logger.info(
                    f"[{keyword}] {sitename} 데이터가 존재하지 않습니다. 새로 생성합니다."
                )
                empty_data = self._create_empty_keyword_data()
                self.keyword_data_by_site[sitename] = empty_data
                return self.update_keyword_data(
                    keyword=keyword, keyword_data=empty_data, sitename=sitename
                )

            loaded_data = KeywordData(**data[sitename])
            self.keyword_data_by_site[sitename] = loaded_data
            return loaded_data

    def data_cleaner(self, keywords: list):
        # data 폴더 경로 지정
        data_folder = os.path.join(os.getcwd(), "data")

        # data 폴더가 존재하지 않으면 경고 로그를 출력하고 종료
        if not os.path.exists(data_folder):
            logger.warning(f"폴더가 존재하지 않습니다: {data_folder}")
            return

        # data 폴더 내의 *_data.json 파일 목록 조회
        data_files = [
            file for file in os.listdir(data_folder) if file.endswith("_data.json")
        ]

        # 키워드 리스트와 비교하여 불필요한 파일 삭제
        for data_file in data_files:
            keyword = data_file.replace("_data.json", "")
            if keyword not in keywords:
                full_path = os.path.join(data_folder, data_file)
                logger.info(f"[{keyword}] 데이터 파일 삭제: {full_path}")
                os.remove(full_path)

    def _create_empty_keyword_data(self) -> KeywordData:
        """빈 KeywordData 객체를 생성합니다."""
        return KeywordData(
            current_id=None,
            current_title=None,
            current_link=None,
            current_price=None,
            current_meta_data=None,
            wdate=datetime.now().isoformat(),
        )
