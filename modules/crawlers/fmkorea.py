import random
import re
import time
from datetime import datetime
from typing import List

from bs4 import BeautifulSoup

from models.keyword_data import KeywordData
from modules import logger
from modules.base_crawler import BaseCrawler


class FMKoreaCrawler(BaseCrawler):
    @property
    def url(
        self,
    ) -> str:
        return f"https://www.fmkorea.com/index.php?mid=hotdeal&page="

    def parse(
        self,
        html: str,
    ) -> List[KeywordData]:
        soup = BeautifulSoup(html, "html.parser")
        product_list = soup.find_all("li", class_="li")

        products = []

        for li in product_list:
            # Extract id
            post_id = li.find("a", class_="pc_voted_count")
            post_id = post_id["href"].split("/")[-1] if post_id else None

            # Extract link
            product_link = li.find("h3", class_="title").find("a")
            link = (
                "https://www.fmkorea.com" + product_link["href"]
                if product_link
                else None
            )

            # Extract title
            title = product_link.text.strip() if product_link else None
            if title:
                title = re.sub(
                    r"[\xa0\t]+", " ", title
                ).strip()  # Remove unwanted characters like \xa0, tabs, etc.

            # Extract shop
            shop_info = li.find("div", class_="hotdeal_info")
            shop_name = shop_info.find("a", class_="strong") if shop_info else None
            shop = shop_name.text if shop_name else None

            # Extract price
            price_tag = (
                shop_info.find_all("a", class_="strong")[1] if shop_info else None
            )
            price = price_tag.text if price_tag else None

            # Extract metadata
            delivery_tag = (
                shop_info.find_all("a", class_="strong")[2] if shop_info else None
            )
            delivery = delivery_tag.text if delivery_tag else None

            reg_date = li.find("span", class_="regdate")
            time = reg_date.text.strip() if reg_date else None

            category_tag = li.find("span", class_="category").find("a")
            category = category_tag.text if category_tag else None

            meta_data = {
                "shop": shop,
                "delivery": delivery,
                "time": time,
                "category": category,
            }

            # search_keyword는 self.keyword의 공백을 모두 제거한 것
            search_keyword = self.keyword.replace(" ", "")
            # search_title은 title의 공백을 모두 제거한 것
            search_title = title.replace(" ", "")
            # title에 search_keyword가 포함되어 있는지 확인
            if search_keyword in search_title:
                products.append(
                    KeywordData(
                        current_id=post_id,
                        current_title=title,
                        current_link=link,
                        current_price=price,
                        current_meta_data=str(meta_data),
                        wdate=datetime.now().isoformat(),
                    )
                )

        return products

    def fetchparse(
        self,
    ):
        # 3페이지까지 크롤링
        for page in range(1, 4):
            url = f"{self.url}{page}"
            """크롤링 실행 (필요 시 오버라이드)."""
            html = self.fetch(url=url)
            if html:
                # result에 파싱 결과 추가
                self.results.extend(self.parse(html))
            else:
                logger.error(f"크롤링 실패: {url}")

            # 요청 간 랜덤 대기 시간 설정 (1초에서 3초 사이)
            time.sleep(random.uniform(1, 3))
        return self.results
