import os
import sys
import pandas as pd
from pathlib import Path
sys.path.append(str(Path(os.path.abspath(__file__)).parent.parent))
from model import bugs_crawler
pd.set_option('mode.chained_assignment',  None)

def main(excel_name, memo, dir_name):
    """ 앨범코드 cd번호 track_seq번호 엑셀파일 입력"""
    bugs = bugs_crawler.BugsCrawler()
    sheet2 = pd.read_excel(f'{excel_name}.xlsx').fillna("")      #output.xlsx
    sheet2['트랙명'] = ''
    sheet2['가사'] = ''
    sheet2['아티스트명'] = ''
    sheet2['재생시간'] = ''
    sheet2['19금 여부'] = ''
    sheet2['서비스 여부'] = ''
    sheet2['엑셀 벅스 트랙 일치 여부'] = ''
    sheet2['장르값'] = ''
    sheet2['재생시간'] = ''
    sheet2['오디오언어'] = ''
    sheet2['트랙명 정확도'] = ''
    count = 1
    sheet2_count = sheet2["벅스앨범 아이디"].value_counts()              #벅스앨범 아이디
    for idx, track_id in enumerate(sheet2['벅스트랙 아이디']):           #트랙 아이디
        print(f"{count}/{sheet2.shape[0]}")     #카운트
        count += 1
        try:
            if track_id == "":
                print('트랙 아이디 미존재')
                raise Exception
            album_id = sheet2['벅스앨범 아이디'][idx]                    #벅스앨범 아이디
            url = f"https://music.bugs.co.kr/track/{int(track_id)}"
            url_list = []
            url_list.append(url)
            print(url_list)
            sheet2['트랙명'][idx] = bugs.get_track_name_url(url_list)[-1]
            sheet2['가사'][idx] = bugs.get_lyric(url_list)[-1]
            sheet2['아티스트명'][idx] = bugs.get_artist(url_list)[-1]
            sheet2['19금 여부'][idx] = bugs.check_age_limit(url_list)[-1]
            sheet2['서비스 여부'][idx] = bugs.check_service_available(url_list)[-1]
            sheet2['엑셀 벅스 트랙 일치 여부'][idx] = bugs.count_bugs_track_number(album_id, sheet2_count)
            sheet2['장르값'][idx] = bugs.get_genre(album_id)
            sheet2['재생시간'][idx] = bugs.get_playtime(url_list)
            sheet2['오디오언어'][idx] = bugs.find_audio_language(sheet2['가사'][idx])
            sheet2['트랙명 정확도'][idx] = bugs.get_trackname_accuracy(sheet2['곡명'][idx], sheet2['트랙명'][idx])
            bugs.album_image_download(int(album_id), dir_name)  # 함수 안에 중복 제외 있음
        except Exception as e:
            sheet2['트랙명'][idx] = ''
            sheet2['가사'][idx] = ''
            sheet2['아티스트명'][idx] = ''
            sheet2['19금 여부'][idx] = ''
            sheet2['서비스 여부'][idx] = ''
            sheet2['엑셀 벅스 트랙 일치 여부'][idx] = ''
            sheet2['장르값'][idx] = ''
            sheet2['재생시간'][idx] = ''
            sheet2['오디오언어'][idx] = ''
            sheet2['트랙명 정확도'][idx] = ''
            print("트랙 사이트가 비어있음", e)

    sheet2.to_excel(f"{memo}.xlsx", index=False)       #album_track_info.xlsx


if __name__ == "__main__":
    # excel_file_name = sys.argv[1]
    # memo = sys.argv[2]
    # dir_name = sys.argv[3]
    # main(excel_file_name, memo, dir_name)

    main('비욘드_after_trackid_2', '비욘드_after_trackinfo_2', '비욘드 앨범커버파일')