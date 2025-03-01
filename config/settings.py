import os
from dotenv import load_dotenv

load_dotenv()

# Gmail API 설정
GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
GMAIL_TOKEN_FILE = 'token.json'
GMAIL_CREDENTIALS_FILE = 'credentials.json'
NEWSLETTER_LABEL = 'Newsletters'

# OpenAI 설정
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Slack 설정
SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')

# 로깅 설정
LOG_FILE = 'newsletter_bot.log' 