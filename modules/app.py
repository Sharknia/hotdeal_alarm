from datetime import datetime

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
        # 키워드 갱신
        self.data_manager.data = self.data_manager.file_load()

        # 크롤링 작업
        keywords = self.data_manager.data.keyword
        if not keywords:
            logger.warning("키워드가 없습니다.")
            return
        for keyword in keywords:
            # 알구몬 크롤링
            algumon_crawler: AlgumonCrawler = AlgumonCrawler(keyword=keyword)
            algumon_result = algumon_crawler.crawl()
            print(f"algumon_result: {algumon_result}")

            # 알구몬 데이터 저장
            del algumon_crawler

            # FMKorea 크롤링
            fmkorea_crawler: FMKoreaCrawler = FMKoreaCrawler(keyword=keyword)
            fmkorea_result = fmkorea_crawler.crawl()
            print(f"fmkorea_result: {fmkorea_result}")

            # FMKorea 데이터 저장
            del fmkorea_crawler

        # 마무리 작업
        self.data_manager.data_cleaner(keywords)
        proxy_manager.reset_proxies()

    def execute_crawler(
        self,
        keyword: str,
    ):
        crawler: Crawler = Crawler(keyword)
        # 크롤링 수행
        if not crawler.fetch_html():
            logger.error(f"[{keyword}] 크롤링 실패")
            return

        # 알구몬 크롤링 결과 파싱
        products = crawler.parse_products_algumon()

        # 키워드에 해당하는 json 파일 로드
        keyword_data: KeywordData = self.data_manager.load_keyword_data(keyword)
        # 크롤링 결과가 없는 경우
        if not products:
            # 최초 알림인 경우
            if not keyword_data.current_id:
                logger.info(f"[{keyword}] 최초 실행 알림")
                self.notification_manager.notify(
                    updates=None, keyword=keyword, mode="initial"
                )
                self.data_manager.update_keyword_data(keyword=keyword)
                logger.warning(f"[{keyword}] 상품 정보가 없습니다.")
                return

        # 기존 데이터와 비교
        current_id = keyword_data.current_id
        # 첫번째 데이터 내용 저장
        new_keyword_data: KeywordData = KeywordData(
            current_id=products[0]["id"],
            current_title=products[0]["title"],
            current_link=products[0]["link"],
            current_price=products[0]["price"],
            current_meta_data=products[0]["meta_data"],
            wdate=datetime.now().isoformat(),
        )
        # 최초 알림인 경우
        if not current_id:
            logger.info(f"[{keyword}] 검색된 상품이 있고, 최초 알림임")
            # 최초 실행: 첫 번째 상품 저장
            first_product = products[0]
            self.data_manager.update_keyword_data(
                keyword=keyword,
                keyword_data=new_keyword_data,
            )
            self.notification_manager.notify(
                updates=first_product,
                keyword=keyword,
                mode="initial",
            )
        # 최초 실행이 아니고 갱신된 내용이 없는 경우
        elif current_id == products[0]["id"]:
            logger.info(f"[{keyword}] 갱신된 내용 없음")
            # 갱신된 내용 없음
            pass
        # 최초 실행이 아니고 갱신된 내용이 있는 경우
        else:
            logger.info(f"[{keyword}] 갱신된 내용 있음")
            # 갱신된 내용 처리
            updates = []
            for product in products:
                if product["id"] == current_id:
                    break
                logger.info(f"[{keyword}] 새로운 상품: {product['title']}")
                updates.append(product)

            # 첫 번째 데이터로 JSON 갱신
            self.data_manager.update_keyword_data(
                keyword=keyword,
                keyword_data=new_keyword_data,
            )

            # 알림 출력
            self.notification_manager.notify(
                updates=updates,
                keyword=keyword,
                mode="updates",
            )
