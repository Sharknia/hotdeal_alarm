from modules.base_crawler import BaseCrawler


class FMKoreaCrawler(BaseCrawler):
    @property
    def url(self):
        return f"https://www.fmkorea.com/index.php?mid=hotdeal&page="

    def parse(self, html):
        # 파싱 로직
        return []
