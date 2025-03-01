import logging
from services.gmail_service import GmailService
from services.summary_service import SummaryService
from services.slack_service import SlackService
from utils.logger import setup_logger

# 뉴스레터 이메일 리스트 설정
NEWSLETTER_EMAILS = [
    'devocean@sktelecom.com', # SK텔레콤 데보션
    'no-reply@substack.com', # Substack 뉴스레터
    'turingpost@mail.beehiiv.com', # 튜링포스트
    'newsletter@eoeoeo.net', # EO플래닛
    'weekly@console.dev', # 콘솔
]

def main():
    # 로거 설정
    setup_logger()
    logger = logging.getLogger(__name__)
    
    try:
        # 서비스 초기화
        gmail_service = GmailService()
        summary_service = SummaryService()
        slack_service = SlackService()

        # 뉴스레터 가져오기
        newsletters = gmail_service.get_newsletters(NEWSLETTER_EMAILS)
        
        if not newsletters:
            logger.info("No newsletters found for yesterday")
            return

        # 처리된 뉴스레터를 담을 리스트
        processed_newsletters = []

        # 각 뉴스레터 처리
        for newsletter in newsletters:
            try:
                # 영문 제목 번역
                translated_subject = summary_service.translate_title(newsletter['subject'])
                
                # 요약 생성 (본문 번역 포함)
                logger.info(f"Processing newsletter from {newsletter['from']}: {translated_subject}")
                summary = summary_service.create_summary(newsletter['body'])

                # 처리된 뉴스레터 정보 저장
                processed_newsletters.append({
                    'subject': translated_subject,
                    'summary': summary,
                    'message_id': newsletter['message_id']
                })
                
                logger.info(f"Successfully processed newsletter: {translated_subject}")
            except Exception as e:
                logger.error(f"Error processing newsletter: {str(e)}")
                continue

        # 모든 뉴스레터를 한 번에 Slack으로 전송
        if processed_newsletters:
            success = slack_service.send_daily_digest(processed_newsletters)
            if success:
                logger.info("Successfully sent daily digest to Slack")
            else:
                logger.error("Failed to send daily digest to Slack")

    except Exception as e:
        logger.error(f"Error in main process: {str(e)}")

if __name__ == "__main__":
    main() 