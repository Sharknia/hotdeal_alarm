# 컨테이너 이름 정의
CONTAINER_NAME=hotdeal_alarm

# 키워드 조회
view:
	docker exec $(CONTAINER_NAME) python /app/utils/view_keyword.py

# 키워드 추가
append:
	docker exec -i $(CONTAINER_NAME) python /app/utils/append_keyword.py

# 키워드 삭제
delete:
	docker exec -i $(CONTAINER_NAME) python /app/utils/delete_keyword.py

# 컨테이너 로그 확인
log:
	docker logs $(CONTAINER_NAME)

# 이미지 빌드 및 컨테이너 실행
build:
	docker build -t $(CONTAINER_NAME) .
	docker run -d --name $(CONTAINER_NAME) -e TZ=Asia/Seoul $(CONTAINER_NAME)

# 기존 컨테이너 및 이미지 삭제 후 빌드 및 실행 (데이터까지 초기화)
clean-rebuild:
	@echo "Stopping and removing existing container..."
	@docker rm -f $(CONTAINER_NAME) 2>/dev/null || true
	@echo "Removing existing image..."
	@docker rmi $(CONTAINER_NAME) 2>/dev/null || true
	@echo "Building new image..."
	@docker build -t $(CONTAINER_NAME) .
	@echo "Running new container..."
	@docker run -d --name $(CONTAINER_NAME) -e TZ=Asia/Seoul $(CONTAINER_NAME)

# 기존 컨테이너 및 이미지 삭제 후 빌드 및 실행 (데이터 유지)
patch:
	@echo "Data backup in progress..."
	@docker cp $(CONTAINER_NAME):/app/data ./data
	@echo "Stopping and removing existing container..."
	@docker rm -f $(CONTAINER_NAME) 2>/dev/null || true
	@echo "Removing existing image..."
	@docker rmi $(CONTAINER_NAME) 2>/dev/null || true
	@echo "Building new image..."
	@docker build -t $(CONTAINER_NAME) .
	@echo "Running new container..."
	@docker run -d --name $(CONTAINER_NAME) -e TZ=Asia/Seoul $(CONTAINER_NAME)
	@echo "Data restore in progress..."
	@docker cp ./data $(CONTAINER_NAME):/app/data
	@echo "Data restore completed."
	@rm -rf data