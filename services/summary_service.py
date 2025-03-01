import openai
from config.settings import OPENAI_API_KEY
import logging

class SummaryService:
    def __init__(self):
        openai.api_key = OPENAI_API_KEY
        self.logger = logging.getLogger(__name__)

    def translate_title(self, title):
        """영문 제목을 한글로 번역"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "영어 텍스트를 한국어로 번역해주세요."},
                    {"role": "user", "content": title}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"Error translating title: {str(e)}")
            return title

    def create_summary(self, text):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "다음 텍스트를 한국어로 번역하고, 주요 내용들을 순서대로 나열해주세요. 각 내용은 '•' 기호로 시작하고 줄바꿈으로 구분해주세요."},
                    {"role": "user", "content": text}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"Error creating summary: {str(e)}")
            return "요약 생성 중 오류가 발생했습니다." 