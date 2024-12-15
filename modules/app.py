from datetime import datetime
from typing import List

from models.keyword_data import KeywordData
from modules import logger
from modules.base_crawler import BaseCrawler
from modules.crawler import Crawler
from modules.crawlers.algumon import AlgumonCrawler
from modules.crawlers.fmkorea import FMKoreaCrawler
from modules.data_manager import DataManager
from modules.notification_manager import NotificationManager
from modules.proxy_manager import ProxyManager


class App:
    def __init__(self):
        self.data_manager: DataManager = DataManager()
        self.notification_manager: NotificationManager = NotificationManager()

    def run(self):
        # 프록시 초기화
        proxy_manager = ProxyManager()
        proxy_manager.fetch_proxies()

        # 검색할 키워드 갱신
        self.data_manager.data = self.data_manager.file_load()

        # 크롤링 작업
        keywords = self.data_manager.data.keyword
        if not keywords:
            logger.warning("키워드가 없습니다.")
            return
        for keyword in keywords:
            algumon_crawler: BaseCrawler = AlgumonCrawler(keyword=keyword)
            self.excute(
                crwaler=algumon_crawler,
                keyword=keyword,
                sitename="Algumon",
            )

            fmkorea_crawler: BaseCrawler = FMKoreaCrawler(keyword=keyword)
            self.excute(
                crwaler=fmkorea_crawler,
                keyword=keyword,
                sitename="FMKorea",
            )

        # 마무리 작업
        self.data_manager.data_cleaner(keywords)
        proxy_manager.reset_proxies()

    def excute(
        self,
        crwaler: BaseCrawler,
        keyword: str,
        sitename: str,
    ):
        # 크롤링 실행
        products: List[KeywordData] = crwaler.fetchparse()

        # 기존 사이트 - 키워드 데이터 로드
        keyword_data: KeywordData = self.data_manager.load_keyword_data(
            keyword=keyword, sitename=sitename
        )

        if not products:
            logger.warning(f"[{keyword}] {sitename} 크롤링 결과가 없습니다.")
            # 이미 검색을 했었다는 사실을 currnent_id의 None 여부로 판단하기 때문에 current_id를 1로 업데이트
            self.data_manager.update_keyword_data(
                keyword=keyword,
                keyword_data=KeywordData(current_id="1"),
                sitename=sitename,
            )
            del crwaler
            return

        new_keyword_data: KeywordData = products[0]

        # 사이트 데이터 저장
        mode = "initial"
        updates = []
        # 최초 실행인 경우
        if not keyword_data.current_id:
            logger.info(f"[{keyword}] 검색된 상품이 있고, 최초 알림임")
            mode = "initial"
            updates = products
        # 최초 실행이 아니고 갱신된 내용이 없는 경우
        elif keyword_data.current_id == new_keyword_data.current_id:
            logger.info(f"[{keyword}] 갱신된 내용 없음")
            # 갱신된 내용 없음
            return
        # 최초 실행이 아니고 갱신된 내용이 있는 경우
        else:
            mode = "updates"
            logger.info(f"[{keyword}] 갱신된 내용 있음")
            # 갱신된 내용 처리
            for product in products:
                if product["id"] == keyword_data.current_id:
                    break
                logger.info(f"[{keyword}] 새로운 상품: {product['title']}")
                updates.append(product)

        # 첫 번째 데이터로 JSON 갱신
        self.data_manager.update_keyword_data(
            keyword=keyword,
            keyword_data=new_keyword_data,
            sitename=sitename,
        )

        # 알림 출력
        self.notification_manager.notify(
            updates=updates,
            keyword=keyword,
            mode=mode,
        )

        # 메모리 초기화
        del crwaler
