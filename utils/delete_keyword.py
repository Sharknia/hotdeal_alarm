import json
import sys

# JSON 파일 경로
json_file_path = "/app/data.json"


def delete_keyword(target_keyword):
    try:
        # JSON 파일 읽기
        with open(json_file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        # "keyword" 리스트에서 대상 키워드 제거
        if "keyword" in data and isinstance(data["keyword"], list):
            if target_keyword in data["keyword"]:
                data["keyword"].remove(target_keyword)
                print(f"Keyword '{target_keyword}' removed successfully.")
            else:
                print(f"Keyword '{target_keyword}' not found in the list.")
        else:
            print("No keywords found or 'keyword' is not a list.")
            return

        # JSON 파일 저장
        with open(json_file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    except FileNotFoundError:
        print(f"Error: File {json_file_path} not found.")
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON.")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python delete_keyword.py <keyword>")
    else:
        delete_keyword(sys.argv[1])
