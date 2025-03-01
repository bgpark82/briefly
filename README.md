# 데일리 뉴스레터 다이제스트 봇

매일 아침 구독 중인 뉴스레터들을 자동으로 수집하고 요약하여 Slack으로 전송하는 봇입니다.

## 주요 기능

- Gmail API를 통해 지정된 발신자의 뉴스레터 수집
- OpenAI GPT를 활용한 영문 뉴스레터 번역 및 요약
- Slack Webhook을 통한 일일 다이제스트 전송
- GitHub Actions를 통한 자동화된 실행 (매일 오전 9시, 베를린 시간 기준)

## 구독 중인 뉴스레터

- SK텔레콤 데보션 (devocean@sktelecom.com)
- Substack 뉴스레터 (no-reply@substack.com)
- 튜링포스트 (turingpost@mail.beehiiv.com)
- EO플래닛 (newsletter@eoeoeo.net)
- Console (weekly@console.dev)

## 설치 및 설정

1. 필요한 패키지 설치:

```bash
pip install -r requirements.txt
```

2. 환경 변수 설정:

```bash
cp .env.example .env
```

3. 환경 변수 파일 수정:

```bash
nano .env
```

## 사용 방법

```bash
python main.py
```

## 라이센스

이 프로젝트는 MIT 라이센스를 따릅니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참고하세요.
