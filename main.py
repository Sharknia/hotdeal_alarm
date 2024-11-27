import json
import logging
import os
import smtplib
import time
from datetime import datetime
from email.mime.text import MIMEText

import requests
import schedule
from bs4 import BeautifulSoup
from dotenv import load_dotenv  # .env 파일을 로드하기 위한 라이브러리

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()

# .env 파일 로드
load_dotenv()


def job():
    try:
        app = App()
        app.run()
    except ValueError as e:
        logger.error(f"에러: {e}")


class DataManager:
    _instance = None  # 싱글톤 인스턴스 저장

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DataManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, file_path="data.json"):
        if not hasattr(self, "initialized"):  # 초기화 방지
            self.file_path = file_path
            self.data = self.load_data()
            self.initialized = True  # 초기화 상태 표시

    def load_data(self):
        # .env 파일에서 설정값 읽기
        keyword = os.getenv("KEYWORD", "")
        smtp_server = os.getenv("SMTP_SERVER", "smtp.kakao.com")
        smtp_port = os.getenv("SMTP_PORT", "465")
        smtp_email = os.getenv("SMTP_EMAIL", "")
        smtp_password = os.getenv("SMTP_PASSWORD", "")

        # 기존 파일이 없으면 환경 변수 기반 초기 데이터 생성
        if not os.path.exists(self.file_path):
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


class Crawler:
    def __init__(self, keyword):
        self.keyword = keyword
        self.base_url = "https://www.algumon.com/search/"
        self.target_url = f"{self.base_url}{keyword}"
        self.html = None
        self.products = []

    def fetch_html(self):
        try:
            response = requests.get(self.target_url)
            response.raise_for_status()
            self.html = response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"HTML 가져오기 실패: {e}")
            return False
        return True

    def parse_products(self):
        if not self.html:
            return []

        soup = BeautifulSoup(self.html, "html.parser")
        product_list = soup.find("ul", class_="product post-list")
        if not product_list:
            logger.warning("상품 리스트를 찾을 수 없습니다.")
            return []

        for li in product_list.find_all("li"):
            post_id = li.get("data-post-id")
            action_uri = li.get("data-action-uri")
            product_link = li.find("a", class_="product-link")
            product_price = li.find("small", class_="product-price")
            meta_info = li.find("small", class_="deal-price-meta-info")

            if post_id and action_uri and product_link:
                title = product_link.text.strip()
                full_link = f"https://www.algumon.com{action_uri.strip()}"
                price = product_price.text.strip() if product_price else ""
                meta_data = (
                    meta_info.text.replace("\n", "")
                    .replace("\r", "")
                    .replace(" ", "")
                    .strip()
                    if meta_info
                    else ""
                )

                self.products.append(
                    {
                        "id": post_id,
                        "title": title,
                        "link": full_link,
                        "price": price,
                        "meta_data": meta_data,
                    }
                )
        return self.products


class NotificationManager:
    def __init__(self, smtp_settings):
        self.smtp_settings = smtp_settings
        self.data_manager = DataManager()  # 싱글톤 인스턴스를 가져옴

    def notify(self, updates, mode="initial"):
        keyword = self.data_manager.data["keyword"]  # 싱글톤 인스턴스 사용
        subject = None
        text = f"<h2><a href='https://www.algumon.com/search/{keyword}'>전체 검색 결과</a></h2>"
        if mode == "initial":
            if updates:
                text += f"<p><a href='{updates['link']}'>{updates['title']} ({updates['price']})</a></p>"
            subject = f"[{keyword}] 핫딜 알림 등록 완료"
            self.send_email(subject=subject, body=text, is_html=True)
        elif mode == "updates":
            subject = f"[{keyword}] 새로운 핫딜 등장!"
            text = "".join(
                [
                    f"<p><a href='{product['link']}'>{product['title']}</a> - {product['price']}</p>"
                    for product in updates
                ]
            )
            self.send_email(subject, text, is_html=True)
        logger.info("알림 완료!")

    def send_email(
        self,
        subject="메일 제목",
        body=None,
        is_html=False,
    ):
        try:
            msg = MIMEText(body, "html" if is_html else "plain")  # HTML 형식 지원
            msg["Subject"] = subject
            msg["From"] = self.smtp_settings["email"]
            msg["To"] = self.smtp_settings["email"]

            with smtplib.SMTP_SSL(
                self.smtp_settings["server"], int(self.smtp_settings["port"])
            ) as server:
                server.login(
                    self.smtp_settings["email"], self.smtp_settings["password"]
                )
                server.sendmail(
                    self.smtp_settings["email"],
                    self.smtp_settings["email"],
                    msg.as_string(),
                )

            logger.info("메일 전송 완료!")
        except Exception as e:
            logger.error(f"메일 전송 실패: {e}")


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
        products = self.crawler.parse_products()
        if not products:
            # 초기화인 경우에는 크롤링 결과가 없어도 알림
            if not wdate:
                self.notification_manager.notify(updates=None, mode="initial")
                # wdate 저장
                self.data_manager.update_data()
            return

        # 기존 데이터와 비교
        current_id = self.data_manager.data["current_id"]
        if not wdate:
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
            # 갱신된 내용 없음
            pass
        else:
            # 갱신된 내용 처리
            updates = []
            for product in products:
                if product["id"] == current_id:
                    break
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


def run_scheduled_tasks():
    global first_run
    now = datetime.now()

    # 최초 실행 시 작업
    if first_run:
        logger.info(f"최초 실행 작업 실행: {now}")
        job()
        first_run = False  # 최초 실행 이후 플래그 변경
        return

    # 매시 정시와 30분에 작업 실행
    elif now.minute % 30 <= 5:
        logger.info(f"정기 작업 실행: {now}")
        job()


if __name__ == "__main__":
    first_run = True  # 최초 실행 플래그
    logger.info("프로그램 시작")
    while True:
        run_scheduled_tasks()
        time.sleep(300)  # 5분마다 확인
