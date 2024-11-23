import json
import os
from datetime import datetime

import requests
from bs4 import BeautifulSoup


class DataManager:
    def __init__(self, file_path="data.json"):
        self.file_path = file_path
        self.data = self.load_data()

    def load_data(self):
        if not os.path.exists(self.file_path):
            return {"keyword": "", "current_title": "", "current_id": "", "wdate": ""}
        with open(self.file_path, "r") as f:
            return json.load(f)

    def save_data(self):
        with open(self.file_path, "w") as f:
            json.dump(self.data, f, indent=4)

    def update_data(self, current_id, current_title):
        self.data["current_id"] = current_id
        self.data["current_title"] = current_title
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
            product_link = li.find("a", class_="product-link")
            if post_id and product_link:
                title = product_link.text.strip()
                self.products.append({"id": post_id, "title": title})
        return self.products


class App:
    def __init__(self, keyword):
        self.data_manager = DataManager()
        self.crawler = Crawler(keyword)

    def run(self):
        # 데이터 파일에 keyword 저장
        if not self.data_manager.data["keyword"]:
            self.data_manager.data["keyword"] = self.crawler.keyword
            self.data_manager.save_data()

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
            self.data_manager.update_data(products[0]["id"], products[0]["title"])
            print("최초 실행 - 데이터 저장 완료.")
        elif current_id == products[0]["id"]:
            # 갱신된 내용 없음
            print("갱신된 내용이 없습니다.")
        else:
            # 갱신된 내용 처리
            print("갱신된 내용 발견:")
            for product in products:
                if product["id"] == current_id:
                    break
                print(f"ID: {product['id']}, Title: {product['title']}")

            # 첫 번째 데이터로 JSON 갱신
            self.data_manager.update_data(products[0]["id"], products[0]["title"])


if __name__ == "__main__":
    keyword = input("검색어를 입력하세요: ")
    app = App(keyword)
    app.run()
