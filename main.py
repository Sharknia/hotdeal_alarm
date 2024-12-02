import time
from datetime import datetime

from dotenv import load_dotenv

from modules import logger
from modules.app import App

load_dotenv()


def job():
    app = App()
    app.run()


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
