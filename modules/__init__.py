import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# 공용 로거 생성
logger = logging.getLogger("modules")  # 로거 이름 설정
