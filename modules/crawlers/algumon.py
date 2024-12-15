from datetime import datetime
from typing import List

from bs4 import BeautifulSoup

from models.keyword_data import KeywordData
from modules import logger
from modules.base_crawler import BaseCrawler


class AlgumonCrawler(BaseCrawler):
    @property
    def url(
        self,
    ) -> str:
        return f"https://www.algumon.com/search/{self.keyword}"

    def parse(
        self,
        html: str,
    ) -> List[KeywordData]:
        soup = BeautifulSoup(html, "html.parser")
        product_list = soup.find("ul", class_="product post-list")
        if not product_list:
            logger.warning("알구몬 상품 리스트를 찾을 수 없습니다.")
            return []

        products = []
        for li in product_list.find_all("li"):
            post_id = li.get("data-post-id")
            action_uri = li.get("data-action-uri")
            product_link = li.find("a", class_="product-link")
            product_price = li.find("small", class_="product-price")
            meta_info = li.find("small", class_="deal-price-meta-info")

            if post_id and action_uri and product_link:
                products.append(
                    KeywordData(
                        current_id=post_id,
                        current_title=product_link.text.strip(),
                        current_link=f"https://www.algumon.com{action_uri.strip()}",
                        current_price=(
                            product_price.text.strip() if product_price else None
                        ),
                        current_meta_data=(meta_info.text.strip() if meta_info else "")
                        .replace("\n", "")
                        .replace("\r", "")
                        .replace(" ", ""),
                        wdate=datetime.now().isoformat(),
                    )
                )
        return products
