# 설명

알구몬에서 제공하는 정보를 주기적으로 크롤링해서 메일을 스스로에게 전송합니다.
해당 프로젝트는 학습 목적으로 제작되었습니다.

# .env 생성

```bash
SMTP_SERVER=smtp.kakao.com
SMTP_PORT=465
SMTP_EMAIL=zel@kakao.com
SMTP_PASSWORD=stmp 패스워드
```

# 이미지 굽기

docker build -t hotdeal_alarm .

# 컨테이너 실행

docker run -d --env-file .env --name hotdeal_styler hotdeal_alarm
