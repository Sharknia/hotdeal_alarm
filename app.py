import json
import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText

import requests
from bs4 import BeautifulSoup


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
        if not os.path.exists(self.file_path):
            return {
                "keyword": "",
                "current_title": "",
                "current_id": "",
                "current_link": "",
                "current_price": "",
                "current_meta_data": "",
                "wdate": "",
            }
        with open(self.file_path, "r") as f:
            return json.load(f)

    def save_data(self):
        with open(self.file_path, "w") as f:
            json.dump(self.data, f, indent=4)

    def update_data(
        self, current_id, current_title, current_link, current_price, current_meta_data
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
            print(f"HTML 가져오기 실패: {e}")
            return False
        return True

    def parse_products(self):
        if not self.html:
            return []

        soup = BeautifulSoup(self.html, "html.parser")
        product_list = soup.find("ul", class_="product post-list")
        if not product_list:
            print("상품 리스트를 찾을 수 없습니다.")
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

    def notify(self, updates, mode="initial"):
        if mode == "initial":
            print("최초 실행 - 데이터 저장 완료:")
            print(
                f"ID: {updates['id']}, Title: {updates['title']}, Price: {updates['price']}, Meta Data: {updates['meta_data']}"
            )
        elif mode == "updates":
            print("갱신된 내용 발견:")
            for product in updates:
                print(
                    f"ID: {product['id']}, Title: {product['title']}, Price: {product['price']}, Meta Data: {product['meta_data']}"
                )
            self.send_email(updates)

    def send_email(self, updates):
        try:
            subject = "갱신된 상품 알림"
            body = "\n".join(
                [f"{product['title']} - {product['price']}" for product in updates]
            )

            msg = MIMEText(body, "plain")
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

            print("갱신된 내용을 이메일로 전송했습니다.")
        except Exception as e:
            print(f"이메일 전송 실패: {e}")


class App:
    def __init__(
        self,
    ):
        self.data_manager = DataManager()
        self.notification_manager = NotificationManager(
            data_manager.data["smtp_settings"]
        )
        self.crawler = Crawler(self.data_manager.data["keyword"])

    def run(self):
        # 크롤링 수행
        if not self.crawler.fetch_html():
            return

        products = self.crawler.parse_products()
        if not products:
            print("크롤링 결과가 없습니다.")
            return

        # 기존 데이터와 비교
        current_id = self.data_manager.data["current_id"]
        if not current_id:
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
            print("갱신된 내용이 없습니다.")
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


if __name__ == "__main__":
    # DataManager 싱글톤 초기화
    data_manager = DataManager()
    keyword = data_manager.data.get("keyword")
    # 초기화 안되어있는 경우
    if not keyword:
        keyword = input("검색어를 입력하세요: ").strip()
        data_manager.data["keyword"] = keyword
        smtp_server = (
            input("SMTP 서버명을 입력하세요 (기본값: smtp.kakao.com): ").strip()
            or "smtp.kakao.com"
        )
        smtp_port = input("SMTP 포트번호를 입력하세요 (기본값: 465): ").strip() or "465"
        smtp_email = input("SMTP 아이디(이메일)를 입력하세요: ").strip()
        smtp_password = input("SMTP 비밀번호(앱 비밀번호)를 입력하세요: ").strip()

        data_manager.data["smtp_settings"] = {
            "server": smtp_server,
            "port": smtp_port,
            "email": smtp_email,
            "password": smtp_password,
        }
        data_manager.save_data()

    try:
        app = App()
        app.run()
    except ValueError as e:
        print(f"에러: {e}")
