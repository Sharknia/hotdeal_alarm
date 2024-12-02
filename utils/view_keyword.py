import json

# JSON 파일 경로
json_file_path = "/app/data.json"


def view_keywords():
    try:
        # JSON 파일 읽기
        with open(json_file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        # "keyword" 리스트 출력
        if "keyword" in data and isinstance(data["keyword"], list):
            print("Keywords:", ", ".join(data["keyword"]))
        else:
            print("No keywords found or 'keyword' is not a list.")

    except FileNotFoundError:
        print(f"Error: File {json_file_path} not found.")
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON.")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    view_keywords()
