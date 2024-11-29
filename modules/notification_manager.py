import smtplib
from email.mime.text import MIMEText

from data_manager import DataManager

from modules import logger


class NotificationManager:
    def __init__(self, smtp_settings):
        self.smtp_settings = smtp_settings
        self.data_manager = DataManager()  # 싱글톤 인스턴스를 가져옴

    def notify(self, updates, mode="initial"):
        keyword = self.data_manager.data["keyword"]  # 싱글톤 인스턴스 사용
        subject = None
        text = f"<h2><a href='https://www.algumon.com/search/{keyword}'>전체 검색 결과</a></h2>"
        logger.info(f"알림 모드: {mode}")
        if mode == "initial":
            if updates:
                text += f"<p><a href='{updates['link']}'>{updates['title']} ({updates['price']})</a></p>"
            subject = f"[{keyword}] 핫딜 알림 등록 완료"
            self.send_email(subject=subject, body=text, is_html=True)
        elif mode == "updates":
            subject = f"[{keyword}] 새로운 핫딜 등장!"
            text = "".join(
                [
                    f"<p><a href='{product['link']}'>{product['title']}</a> - {product['price']}</p>"
                    for product in updates
                ]
            )
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
            msg["From"] = self.smtp_settings["email"]
            msg["To"] = self.smtp_settings["email"]

            with smtplib.SMTP_SSL(
                self.smtp_settings["server"], int(self.smtp_settings["port"])
            ) as server:
                server.login(
                    self.smtp_settings["email"], self.smtp_settings["password"]
                )
                server.sendmail(
                    self.smtp_settings["email"],
                    self.smtp_settings["email"],
                    msg.as_string(),
                )

            logger.info("메일 전송 완료!")
        except Exception as e:
            logger.error(f"메일 전송 실패: {e}")
