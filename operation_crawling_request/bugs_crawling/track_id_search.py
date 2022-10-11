import sys
import time
import requests
import pandas as pd
from random import random
from bs4 import BeautifulSoup
pd.set_option('mode.chained_assignment',  None)

HEADERS = [
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"},
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}
]
count = 1

def get_track_id(album_id) -> int:
    """벅스앨범 아이디를 인수로 받아 벅스 크롤링 후 벅스트랙 아이디를 리턴하는 함수"""
    dict = {}
    url = f"https://music.bugs.co.kr/album/{album_id}"
    header = HEADERS[int(random()) * len(HEADERS)]
    res = requests.get(url, headers=header)
    time.sleep(random() + 0.5)
    soup = BeautifulSoup(res.text, 'lxml')
    track_datas = soup.find_all("tr", attrs={'albumid': f'{album_id}'})
    for track_data in track_datas:
        try:
            cd_num = track_data.find('td', attrs={'class': 'check'}).find('input')['disc_id']
            track_seq = track_data.find('p', attrs={'class': 'trackIndex'}).find('em').get_text()
            track_id = track_data['trackid']
            dict[f'{album_id}_{cd_num}_{track_seq}'] = track_id
        except:
            continue
    return dict

def main(xl_read, memo) -> str:
    """벅스앨범 아이디, cd 넘버, 트랙 시퀀스를 가진 엑셀파일에서 벅스트랙 아이디 생성"""
    df = pd.read_excel(f"{xl_read}.xlsx").fillna("")
    df["벅스트랙 아이디"] = ''
    album_id = df["벅스앨범 아이디"]
    for idx, album_id in enumerate(album_id):
        if album_id == "":
            continue
        cd_num = df["CD"][idx]
        track_seq = df["Track"][idx]
        album_id = int(album_id)            #.0 제거
        dict = get_track_id(album_id)       #202020717_1_2 : 1233445
        try:
            track_id = dict[f"{album_id}_{cd_num}_{track_seq}"]
        except KeyError:
            track_id = ""
        finally:
            df["벅스트랙 아이디"][idx] = track_id
    df.to_excel(f"{memo}.xlsx", index=False)


if __name__ == "__main__":
    # print(get_track_id('4411'))
    # excel_file_name = sys.argv[1]
    # memo = sys.argv[2]
    # main(excel_file_name, memo)
    main('비욘드_after_albumid_2', '비욘드_after_trackid_2')
    #main('1', '비욘드_after_trackid')
