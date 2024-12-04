# 설명

알구몬에서 제공하는 정보를 주기적으로 크롤링해서 메일을 스스로에게 전송합니다.
해당 프로젝트는 학습 목적으로 제작되었습니다.

# .env 생성

```bash
SMTP_SERVER=smtp.kakao.com
SMTP_PORT=465
SMTP_EMAIL=zel@kakao.com
SMTP_PASSWORD={stmp 패스워드}
```

# 실행법

## 도커를 사용하지 않을 경우

1. **Python 3.12 이상**과 [Poetry](https://python-poetry.org/)가 설치되어 있어야 합니다.
2. 아래 명령어를 순서대로 실행하세요.

    ```bash
    # Python 3.12을 로컬 환경에서 활성화
    pyenv local 3.12

    # 필요한 의존성 설치
    poetry install

    # 프로그램 실행
    python main.py
    ```

3. 여기까지 마치면 data 폴더 안에 data.json 파일이 생성됩니다. 해당 파일의 keyword 항목에 알림이 필요한 키워드를 리스트 형식으로 집어넣습니다.

## 도커를 사용할 경우

**docker**가 설치되어 있어야 합니다.

1. 이미지 빌드 및 컨테이너 실행
    ```bash
    make build
    ```
2. 키워드 관련 명령어
    1. 현재 등록된 키워드 조회
        ```bash
        make view
        ```
    2. 키워드 추가
        ```bash
        make append
        ```
    3. 특정 키워드 삭제
        ```bash
        make delete
        ```
3. 도커 관련 MAKE 명령어
    1. 컨테이너 로그 확인
        ```bash
        make log
        ```
    2. 패치 후 데이터 유지하며 이미지 재빌드 및 실행
        - 이 명령어는 데이터는 유지하면서 패치를 실행합니다.
        ```bash
        make patch
        ```
    3. 패치 후 데이터도 초기화하고 이미지 재빌드 및 실행
        - 이 명령어는 데이터까지 초기화합니다.
        ```bash
        make clean-rebuild
        ```

## 공통 설명

-   매시 정각, 30분에 알림을 받게 되며, 키워드 추가/삭제의 경우에도 이 시간대에 적용됩니다. 즉, 키워드 추가/삭제는 실시간 반영되지 않습니다.

-   프로그램은 5분마다 작동하게 해 CPU의 부담을 최소화 하였습니다.
