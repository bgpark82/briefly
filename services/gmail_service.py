import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import base64
from email.mime.text import MIMEText
import logging
from bs4 import BeautifulSoup
from config.settings import GMAIL_SCOPES, GMAIL_TOKEN_FILE, GMAIL_CREDENTIALS_FILE, NEWSLETTER_LABEL

class GmailService:
    def __init__(self):
        # 로거를 서비스 초기화 전에 설정
        self.logger = logging.getLogger(__name__)
        self.service = self._get_gmail_service()

    def _get_gmail_service(self):
        """
        환경에 따라 적절한 인증 방식 선택
        - GitHub Actions: 서비스 계정 사용
        - 로컬 환경: OAuth 사용
        """
        try:
            creds = None
            # GitHub Actions 환경인지 확인
            is_github_actions = os.getenv('GITHUB_ACTIONS') == 'true'

            if is_github_actions:
                # GitHub Actions에서는 서비스 계정 사용
                self.logger.info("Using service account authentication for GitHub Actions")
                creds = service_account.Credentials.from_service_account_file(
                    GMAIL_CREDENTIALS_FILE,
                    scopes=GMAIL_SCOPES
                )
            else:
                # 로컬 환경에서는 OAuth 사용
                self.logger.info("Using OAuth authentication for local environment")
                if os.path.exists(GMAIL_TOKEN_FILE):
                    creds = Credentials.from_authorized_user_file(GMAIL_TOKEN_FILE, GMAIL_SCOPES)
                
                if not creds or not creds.valid:
                    flow = InstalledAppFlow.from_client_secrets_file(GMAIL_CREDENTIALS_FILE, GMAIL_SCOPES)
                    creds = flow.run_local_server(port=0)
                    with open(GMAIL_TOKEN_FILE, 'w') as token:
                        token.write(creds.to_json())

            return build('gmail', 'v1', credentials=creds)
        except Exception as e:
            self.logger.error(f"Error getting Gmail service: {str(e)}")
            raise

    def _html_to_text(self, html_content):
        """HTML 컨텐츠를 일반 텍스트로 변환"""
        soup = BeautifulSoup(html_content, 'html.parser')
        # 스크립트와 스타일 요소 제거
        for script in soup(["script", "style"]):
            script.decompose()
        # 텍스트 추출
        text = soup.get_text(separator='\n', strip=True)
        # 여러 줄의 공백을 하나로 정리
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        return text

    def get_newsletters(self, email_filters):
        """
        이메일 필터 목록을 받아서 각 필터에 해당하는 뉴스레터를 가져옴
        email_filters: 이메일 주소 리스트 ['email1@domain.com', 'email2@domain.com']
        """
        try:
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y/%m/%d')
            messages = []

            for email in email_filters:
                query = f'from:{email} after:{yesterday}'
                
                results = self.service.users().messages().list(
                    userId='me', q=query
                ).execute()

                if 'messages' in results:
                    for message in results['messages']:
                        # Gmail API를 통해 메시지의 전체 내용을 가져옴
                        msg = self.service.users().messages().get(
                            userId='me', id=message['id'], format='full'
                        ).execute()

                        payload = msg['payload']
                        headers = payload['headers']
                        # 메일 제목 추출
                        subject = next(h['value'] for h in headers if h['name'] == 'Subject')
                        
                        # 텍스트와 HTML 컨텐츠를 저장할 변수 초기화
                        text_content = ""
                        html_content = ""
                        
                        if 'parts' in payload:
                            # 멀티파트 메시지인 경우 각 파트를 순회
                            for part in payload['parts']:
                                if part['mimeType'] == 'text/plain':
                                    # 일반 텍스트 형식의 본문 추출
                                    text_content = base64.urlsafe_b64decode(
                                        part['body']['data']
                                    ).decode('utf-8')
                                elif part['mimeType'] == 'text/html':
                                    # HTML 형식의 본문 추출 (백업용)
                                    html_content = base64.urlsafe_b64decode(
                                        part['body']['data']
                                    ).decode('utf-8')
                        else:
                            # 단일 파트 메시지인 경우
                            content = base64.urlsafe_b64decode(
                                payload['body']['data']
                            ).decode('utf-8')
                            # mimeType에 따라 적절한 변수에 저장
                            text_content = content if payload['mimeType'] == 'text/plain' else ""
                            html_content = content if payload['mimeType'] == 'text/html' else ""

                        # text/plain이 있으면 사용하고, 없으면 HTML을 텍스트로 변환
                        final_body = text_content if text_content else self._html_to_text(html_content)

                        messages.append({
                            'subject': subject,
                            'body': final_body,
                            'from': email,
                            'message_id': message['id']
                        })

            return messages
        except Exception as e:
            self.logger.error(f"Error fetching newsletters: {str(e)}")
            return []

    def _get_body_from_parts(self, parts):
        body = ""
        for part in parts:
            if part['mimeType'] == 'text/plain':
                body = base64.urlsafe_b64decode(
                    part['body']['data']
                ).decode('utf-8')
                break
        return body 