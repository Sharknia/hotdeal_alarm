import requests
from bs4 import BeautifulSoup

from modules import logger


class Crawler:
    def __init__(
        self,
        keyword: str,
    ):
        self.keyword = keyword
        self.target_url_algumon = f"https://www.algumon.com/search/{keyword}"
        self.target_url_fmkorea = (
            f"https://www.fmkorea.com/index.php?mid=hotdeal&page=1"
        )
        self.html_algumon = None
        self.products = []
        self.proxies = [
            "http://8.219.97.248:80",
        ]

    def fetch_html(self):
        try:
            # 알구몬 fetch
            self.algumon_html = self.algumon_fetch()

            # fmkorea fetch
        except requests.exceptions.RequestException as e:
            logger.error(f"알구몬 HTML 가져오기 실패: {e}")
            return False
        return True

    def algumon_fetch(self):
        try:
            response = requests.get(self.target_url_algumon, timeout=100)
            if response.status_code == 403:
                logger.warning("403 Forbidden: IP 차단, 프록시로 시도")
                for proxy in self.proxies:
                    try:
                        proxies = {"http": proxy, "https": proxy}
                        response = requests.get(
                            self.target_url_algumon, proxies=proxies, timeout=100
                        )
                        if response.status_code == 200:
                            return response.text
                    except requests.exceptions.RequestException as e:
                        logger.error(f"다음 프록시 재시도: {e}")
                        continue
                # while문을 다 돌아도 200이 아니면 결국 가져오기 실패이므로 None 반환
                logger.error("알구몬 프록시로도 가져오기 실패")
                return None
            else:
                logger.info("알구몬 HTML 가져오기 성공: %s", self.target_url_algumon)
                return response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"알구몬 HTML 가져오기 실패: {e}")
            return None

    # 알구몬의 데이터를 정리
    def parse_products_algumon(self):
        if not self.html_algumon:
            return []

        soup = BeautifulSoup(self.html_algumon, "html.parser")
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
