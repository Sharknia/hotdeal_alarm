from modules import logger
from modules.crawler import Crawler
from modules.data_manager import DataManager
from modules.notification_manager import NotificationManager


class App:
    def __init__(self):
        self.data_manager = DataManager()
        self.notification_manager = NotificationManager(
            self.data_manager.data["smtp_settings"]
        )
        self.crawler = Crawler(self.data_manager.data["keyword"])

    def run(self):
        # 크롤링 수행
        if not self.crawler.fetch_html():
            return

        wdate = self.data_manager.data["wdate"]
        products = self.crawler.parse_products_algumon()
        if not products:
            # 초기화인 경우에는 크롤링 결과가 없어도 알림
            if not wdate:
                logger.info("최초 실행 알림")
                self.notification_manager.notify(updates=None, mode="initial")
                # wdate 저장
                self.data_manager.update_data()
            logger.warning("상품 정보가 없습니다.")
            return

        # 기존 데이터와 비교
        current_id = self.data_manager.data["current_id"]
        if not wdate:
            logger.info("상품이 있고, 최초 알림임")
            # 최초 실행: 첫 번째 상품 저장
            first_product = products[0]
            self.data_manager.update_data(
                first_product["id"],
                first_product["title"],
                first_product["link"],
                first_product["price"],
                first_product["meta_data"],
            )
            self.notification_manager.notify(first_product, mode="initial")
        elif current_id == products[0]["id"]:
            logger.info("갱신된 내용 없음")
            # 갱신된 내용 없음
            pass
        else:
            logger.info("갱신된 내용 있음")
            # 갱신된 내용 처리
            updates = []
            for product in products:
                if product["id"] == current_id:
                    break
                logger.info(f"새로운 상품: {product['title']}")
                updates.append(product)

            # 첫 번째 데이터로 JSON 갱신
            first_product = products[0]
            self.data_manager.update_data(
                first_product["id"],
                first_product["title"],
                first_product["link"],
                first_product["price"],
                first_product["meta_data"],
            )

            # 알림 출력
            self.notification_manager.notify(updates, mode="updates")
