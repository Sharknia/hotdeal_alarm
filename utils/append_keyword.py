import json

# JSON 파일 경로
json_file_path = "/app/data/data.json"


def add_keyword(new_keyword):
    try:
        # JSON 파일 읽기
        with open(json_file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        # "keyword" 리스트에 새 키워드 추가
        if "keyword" in data:
            if not isinstance(data["keyword"], list):
                print("Error: 'keyword' is not a list.")
                return
            if new_keyword not in data["keyword"]:
                data["keyword"].append(new_keyword)
        else:
            # "keyword" 키가 없을 경우 새로 생성
            data["keyword"] = [new_keyword]

        # JSON 파일 저장
        with open(json_file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        print(f"Keyword '{new_keyword}' added successfully.")

    except FileNotFoundError:
        print(f"Error: File {json_file_path} not found.")
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON.")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    while True:
        new_keyword = input("추가할 키워드를 입력하세요: ").strip()  # 공백 제거
        if not new_keyword:  # 빈 문자열 검사
            print("키워드는 비어 있을 수 없습니다. 다시 입력해주세요.")
            continue
        add_keyword(new_keyword)
        break
