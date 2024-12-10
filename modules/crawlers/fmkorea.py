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
    ) -> list:
        # 파싱 로직
        return []

    def crawl(
        self,
    ):
        """크롤링 실행 (필요 시 오버라이드)."""
        html = self.fetch()
        if html:
            self.results = self.parse(html)
        else:
            logger.error(f"크롤링 실패: {self.url}")
        return self.results
