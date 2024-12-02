import time

import requests
from bs4 import BeautifulSoup

from modules import logger


class Crawler:
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

    def fetch_html(self):
        try:
            # 알구몬 fetch
            self.html_algumon = self.algumon_fetch()

            # fmkorea fetch
        except requests.exceptions.RequestException as e:
            logger.error(f"알구몬 HTML 가져오기 실패: {e}")
            return False
        return True

    # 무료 프록시 사이트에서 HTTPS 프록시 가져오기
    def proxy_setting(self):
        try:
            # 무료 프록시 사이트로부터 HTML 가져오기
            response = requests.get(self.target_url_proxy, timeout=30)
            response.raise_for_status()

            # HTML 파싱
            soup = BeautifulSoup(response.content, "html.parser")
            table = soup.find("table", {"class": "table table-striped table-bordered"})

            if not table:
                logger.warning("프록시 테이블을 찾을 수 없습니다.")
                return
            cnt = 0
            # 테이블에서 HTTPS 지원 프록시 추출
            rows = table.find("tbody").find_all("tr")  # 테이블의 행 가져오기
            proxies = []
            for row in rows[:100]:  # 상위 10개의 항목
                cols = row.find_all("td")
                ip = cols[0].text.strip()  # IP Address
                port = cols[1].text.strip()  # Port
                anonymity = cols[4].text.strip()  # 익명도
                https_support = cols[6].text.strip()  # HTTPS 지원 여부

                if https_support == "yes" and anonymity == "anonymous":
                    proxies.append(f"http://{ip}:{port}")
                    cnt += 1
                if cnt == 10:
                    break

            # 프록시 리스트 업데이트
            if proxies:
                logger.info(f"프록시 설정 완료: {proxies}")
            else:
                logger.warning("HTTPS 지원 및 엘리트가 아닌 프록시를 찾지 못했습니다.")
            return proxies

        except requests.exceptions.RequestException as e:
            logger.error(f"프록시 가져오기 실패: {e}")

        except Exception as e:
            logger.error(f"프록시 설정 중 에러 발생: {e}")

    def algumon_fetch(self):
        try:
            response = requests.get(self.target_url_algumon, timeout=100)
            if response.status_code == 403:
                logger.warning("403 Forbidden: IP 차단, 프록시로 시도")
                proxies = self.proxy_setting()
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
