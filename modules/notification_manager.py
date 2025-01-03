import smtplib
from email.mime.text import MIMEText
from typing import List

from models.keyword_data import KeywordData
from modules import logger
from modules.data_manager import DataManager


class NotificationManager:
    def __init__(self):
        self.data_manager = DataManager()  # 싱글톤 인스턴스를 가져옴
        self.smtp_settings = self.data_manager.data.smtp_settings  # 속성으로 접근

    def notify(
        self,
        keyword: str,
        updates: List[KeywordData],
        mode="initial",
    ):
        subject = None
        text = f"<h2><a href='https://www.algumon.com/search/{keyword}'>전체 검색 결과</a></h2>"
        logger.info(f"알림 모드: {mode}")
        if mode == "initial":
            if updates:
                text += f"<p><a href='{updates[0].current_link}'>{updates[0].current_title} ({updates[0].current_price})</a></p>"
            subject = f"[{keyword}] 핫딜 알림 등록 완료"
            self.send_email(subject=subject, body=text, is_html=True)
        elif mode == "updates":
            # 업데이트 모드에서 HTML 리스트 생성
            product_list_html = "".join(
                [
                    f"<p><a href='{product.current_link}'>{product.current_title}</a> - {product.current_price}</p>"
                    for product in updates
                ]
            )
            text += product_list_html  # 기존 텍스트에 리스트를 추가
            subject = f"[{keyword}] 새로운 핫딜 등장!"
            self.send_email(subject, text, is_html=True)
        logger.info("알림 완료!")

    def send_email(
        self,
        subject="메일 제목",
        body=None,
        is_html=False,
    ):
        try:
            msg = MIMEText(body, "html" if is_html else "plain")  # HTML 형식 지원
            msg["Subject"] = subject
            msg["From"] = self.smtp_settings.email
            msg["To"] = self.smtp_settings.email

            with smtplib.SMTP_SSL(
                self.smtp_settings.server, int(self.smtp_settings.port)
            ) as server:
                server.login(self.smtp_settings.email, self.smtp_settings.password)
                server.sendmail(
                    self.smtp_settings.email,
                    self.smtp_settings.email,
                    msg.as_string(),
                )

            logger.info("메일 전송 완료!")
        except Exception as e:
            logger.error(f"메일 전송 실패: {e}")
