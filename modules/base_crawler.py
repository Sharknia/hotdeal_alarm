from abc import ABC, abstractmethod

import requests

from modules import logger
from modules.proxy_manager import ProxyManager


class BaseCrawler(ABC):
    """크롤러의 기본 추상 클래스."""

    def __init__(
        self,
        keyword: str,
    ):
        self.keyword = keyword
        self.proxy_manager: ProxyManager = ProxyManager()
        self.results = []

    @property
    @abstractmethod
    def url(
        self,
    ) -> str:
        """크롤링 대상 URL (하위 클래스에서 구현 필수)."""
        pass

    @abstractmethod
    def parse(
        self,
        html: str,
    ) -> list:
        """파싱 로직 (사이트별 구현 필요)."""
        pass

    def fetch(
        self,
        url: str = None,
        timeout: int = 100,
    ) -> str:
        """HTML 가져오기 (프록시 포함)."""
        target_url = url or self.url  # url이 명시되지 않으면 기본적으로 self.url 사용
        try:
            response = requests.get(
                target_url,
                timeout=timeout,
            )
            if response.status_code == 403:
                logger.warning(
                    f"403 Forbidden: 접근이 차단되었습니다. 프록시로 재시도합니다."
                )
                return self._fetch_with_proxy(target_url, timeout)

            response.raise_for_status()
            return response.text

        except requests.exceptions.RequestException as e:
            logger.error(f"요청 실패: {e}")
            return None

    def _fetch_with_proxy(
        self,
        url: str,
        timeout: int = 100,
    ):
        """프록시를 사용하여 HTML 가져오기."""
        for proxy in self.proxy_manager.proxies:
            try:
                response = requests.get(
                    url,
                    proxies={"http": proxy, "https": proxy},
                    timeout=timeout,
                )
                if response.status_code == 403:
                    logger.warning(f"프록시 {proxy}에서 403 Forbidden 발생")
                    continue  # 다음 프록시로 재시도
                elif response.status_code == 200:
                    logger.info(f"프록시 {proxy}로 요청 성공")
                    return response.text
            except requests.exceptions.RequestException:
                logger.warning(f"프록시 {proxy}로 요청 실패")
        logger.error("모든 프록시를 사용했지만 요청에 실패했습니다.")
        return None

    def crawl(
        self,
    ) -> list:
        """크롤링 실행 (필요 시 오버라이드)."""
        html = self.fetch()
        if html:
            self.results = self.parse(html)
        else:
            logger.error(f"크롤링 실패: {self.url}")
        self.reset_results()
        return self.results

    def reset_results(
        self,
    ):
        """결과 초기화."""
        self.results = []
        logger.info(f"{self.__class__.__name__}의 크롤링 결과 초기화 완료")