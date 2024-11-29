import requests
from bs4 import BeautifulSoup

from modules import logger


class Crawler:
    def __init__(self, keyword):
        self.keyword = keyword
        self.base_url = "https://www.algumon.com/search/"
        self.target_url = f"{self.base_url}{keyword}"
        self.html = None
        self.products = []

    def fetch_html(self):
        try:

            proxies = {
                "http": "http://8.219.97.248:80",
                "https": "http://8.219.97.248:80",
            }

            response = requests.get(self.target_url, proxies=proxies, timeout=100)
            response.raise_for_status()
            self.html = response.text
            logger.info("HTML 가져오기 성공: %s", self.target_url)
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
