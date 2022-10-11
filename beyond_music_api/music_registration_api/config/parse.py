import os
import json

paths = ["/home/shr/work/consalad/nas", "Z:", "/Volumes/consaladContentsLive", "/home/ubuntu/consalad/consaladContentsLive"]


def get_config():
    for path in paths:
        if os.path.exists(path):
            with open(f"{path}/consalad/env/config.json", 'r', encoding="utf-8") as j:
                return json.load(j)
    else:
        print("파일을 찾을 수 없습니다.")
        exit(1)


if __name__ == "__main__":
    print(get_config())