import requests
from config.settings import SLACK_WEBHOOK_URL
import logging
from datetime import datetime

class SlackService:
    def __init__(self):
        self.webhook_url = SLACK_WEBHOOK_URL
        self.logger = logging.getLogger(__name__)

    def create_message_block(self, subject, summary, message_id):
        """단일 뉴스레터에 대한 메시지 블록 생성"""
        gmail_link = f"https://mail.google.com/mail/u/0/#inbox/{message_id}"
        
        return [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📰 {subject}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": summary
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"📧 <{gmail_link}|원문 보기>"
                }
            },
            {
                "type": "divider"
            }
        ]

    def send_daily_digest(self, newsletters):
        """하루치 뉴스레터 모아서 한 번에 전송"""
        try:
            if not newsletters:
                return True

            today = datetime.now().strftime("%Y년 %m월 %d일")
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"📆 {today} 뉴스레터 모음"
                    }
                },
                {
                    "type": "divider"
                }
            ]

            # 각 뉴스레터의 블록을 하나로 합침
            for newsletter in newsletters:
                blocks.extend(
                    self.create_message_block(
                        newsletter['subject'],
                        newsletter['summary'],
                        newsletter['message_id']
                    )
                )

            message = {
                "blocks": blocks
            }
            
            response = requests.post(
                self.webhook_url,
                json=message
            )
            response.raise_for_status()
            return True
        except Exception as e:
            self.logger.error(f"Error sending daily digest to Slack: {str(e)}")
            return False 