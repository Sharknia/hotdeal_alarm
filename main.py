import time
from datetime import datetime

from modules import logger
from modules.app import App


def job():
    try:
        app = App()
        app.run()
    except ValueError as e:
        logger.error(f"에러: {e}")


def run_scheduled_tasks():
    global first_run
    now = datetime.now()

    # 최초 실행 시 작업
    if first_run:
        logger.info(f"최초 실행 작업 실행: {now}")
        job()
        first_run = False  # 최초 실행 이후 플래그 변경
        return

    # 매시 정시와 30분에 작업 실행
    elif now.minute % 30 <= 5:
        logger.info(f"정기 작업 실행: {now}")
        job()


if __name__ == "__main__":
    first_run = True  # 최초 실행 플래그
    logger.info("프로그램 시작")
    while True:
        run_scheduled_tasks()
        time.sleep(300)  # 5분마다 확인
