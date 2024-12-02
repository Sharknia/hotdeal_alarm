# 컨테이너 이름 정의
CONTAINER_NAME=hotdeal_alarm

# 키워드 조회
view:
	docker exec $(CONTAINER_NAME) python /app/utils/view_keyword.py

# 키워드 추가
append:
	@if [ -z "$(KEYWORD)" ]; then \
		echo "Usage: make append_keyword KEYWORD=\"<keyword>\""; \
	else \
		docker exec $(CONTAINER_NAME) python /app/utils/append_keyword.py "$(KEYWORD)"; \
	fi

# 키워드 삭제
delete:
	@if [ -z "$(KEYWORD)" ]; then \
		echo "Usage: make delete_keyword KEYWORD=\"<keyword>\""; \
	else \
		docker exec $(CONTAINER_NAME) python /app/utils/delete_keyword.py "$(KEYWORD)"; \
	fi
