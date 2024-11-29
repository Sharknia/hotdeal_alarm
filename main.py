import os
import time
from datetime import datetime

from dotenv import load_dotenv

from modules import logger
from modules.app import App


# 컨테이너 환경 감지
def is_running_in_container():
    return os.path.exists("/.dockerenv")


# 로컬 환경일 경우 .env 파일 로드
if not is_running_in_container():
    logger.info("로컬 환경: .env 파일 로드")
    load_dotenv()
else:
    logger.info("컨테이너 환경: .env 파일 무시")


def job():
    try:
        app = App()
        app.run()
    except ValueError as e:
        logger.error(f"에러: {e}")


def run_scheduled_tasks(first_run):
    now = datetime.now()

    # 최초 실행 시 작업
    if first_run:
        logger.info(f"최초 실행 작업 실행: {now}")
        job()
        return False  # 최초 실행 이후 플래그 변경

    # 매시 정시와 30분에 작업 실행
    elif now.minute % 30 <= 5:
        logger.info(f"정기 작업 실행: {now}")
        job()

    return first_run


if __name__ == "__main__":
    first_run = True  # 최초 실행 플래그
    logger.info("프로그램 시작")
    while True:
        first_run = run_scheduled_tasks(first_run)
        time.sleep(300)  # 5분마다 확인
