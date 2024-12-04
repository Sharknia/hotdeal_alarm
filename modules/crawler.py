import time

import requests
from bs4 import BeautifulSoup

from modules import logger


class Crawler:
    proxies = []  # 클래스 속성으로 프록시 리스트 공유

    def __init__(
        self,
        keyword: str,
    ):
        self.keyword = keyword
        # 알구몬 핫딜 리스트
        self.target_url_algumon = f"https://www.algumon.com/search/{keyword}"
        # 펨코 핫딜 리스트
        self.target_url_fmkorea = (
            f"https://www.fmkorea.com/index.php?mid=hotdeal&page=1"
        )
        # 무료 프록시 사이트
        self.target_url_proxy = "https://www.sslproxies.org/"
        self.html_algumon = None
        self.products = []

    @classmethod
    def init_proxies(cls):
        cls.proxies = []  # 클래스 속성을 초기화
        logger.info("프록시 리스트가 초기화되었습니다.")
        return cls.proxies

    def fetch_html(self):
        try:
            # 알구몬 fetch
            self.html_algumon = self.algumon_fetch()
            if not self.html_algumon:
                logger.error(f"알구몬 HTML 가져오기 실패")
                return False
            # fmkorea fetch
        except requests.exceptions.RequestException as e:
            logger.error(f"알구몬 HTML 가져오기 실패: {e}")
            return False
        return True

    # 무료 프록시 사이트에서 HTTPS 프록시 가져오기
    def set_proxy(self):
        if Crawler.proxies:  # 클래스 속성을 참조
            logger.info(f"기존 프록시를 재활용합니다: {Crawler.proxies}")
            return Crawler.proxies

        try:
            response = requests.get(self.target_url_proxy, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")
            table = soup.find("table", {"class": "table table-striped table-bordered"})

            if not table:
                logger.warning("프록시 테이블을 찾을 수 없습니다.")
                return

            cnt = 0
            rows = table.find("tbody").find_all("tr")
            proxies = []
            for row in rows[:100]:
                cols = row.find_all("td")
                ip = cols[0].text.strip()
                port = cols[1].text.strip()
                anonymity = cols[4].text.strip()
                https_support = cols[6].text.strip()

                if https_support.lower() == "yes" and anonymity.lower() == "anonymous":
                    proxies.append(f"http://{ip}:{port}")
                    cnt += 1
                if cnt == 15:
                    break

            Crawler.proxies = proxies  # 클래스 속성에 저장
            if proxies:
                logger.info(f"프록시 설정 완료: {Crawler.proxies}")
            else:
                logger.warning("HTTPS 지원 및 익명 프록시를 찾지 못했습니다.")

            return Crawler.proxies

        except requests.exceptions.RequestException as e:
            logger.error(f"프록시 가져오기 실패: {e}")
        except Exception as e:
            logger.error(f"프록시 설정 중 에러 발생: {e}")

    def algumon_fetch(self):
        try:
            response = requests.get(self.target_url_algumon, timeout=100)
            if response.status_code == 403:
                logger.warning("403 Forbidden: IP 차단, 프록시로 시도")
                proxies = self.set_proxy()
                for proxy in proxies:
                    try:
                        proxies = {"http": proxy, "https": proxy}
                        response = requests.get(
                            self.target_url_algumon, proxies=proxies, timeout=100
                        )
                        if response.status_code == 200:
                            logger.info(f"프록시 : {proxy}로 알구몬 HTML 가져오기 성공")
                            return response.text
                        time.sleep(3)
                    except requests.exceptions.RequestException as e:
                        logger.error(f"프록시 : {proxy}로 가져오기 실패: {e}")
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
