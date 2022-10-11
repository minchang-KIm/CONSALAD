import os
import sys
import traceback
from pathlib import Path
sys.path.append(str(Path(os.path.abspath(__file__)).parent.parent))
from model.apple_crawler import AppleCrawler
from query_define import *


def main(excel_name, memo):

    # 엑셀읽고 dataframe 가공
    crawler = AppleCrawler()
    df = AppleCrawler.read_excel(excel_name)

    for idx in range(df.shape[0]):
        kor_excel_name_origin = df['국문'][idx].strip()
        eng_excel_name_origin = df['영문'][idx].strip()

        # 콘샐러드에 기존재하는 아티스트 일시 건너뜀
        print(f"{df.iloc[idx].to_list()} 검색시작..")
        df['애플 아이디'][idx] = find_apple_id_from_consalad(kor_excel_name_origin, eng_excel_name_origin)
        if df['애플 아이디'][idx] != None:   #df['애플 아이디'][idx] != ""
            df['비고'][idx] = '기존재'
            print(f"DB 에 기존재하므로 pass : {df['애플 아이디'][idx]}")
            continue

        # 이 이외는 신규 혹은 애플에 기존재하는 아티스트이다.
        df['애플 아이디'][idx] = '신규'
        df['비고'][idx] = artist_create_query(kor_excel_name_origin, eng_excel_name_origin, '신규', memo)

        # 한글 영어 검색하면서 아티스트 아이디값 수집
        artist_apple_ids = list()
        for artist_name in [kor_excel_name_origin, eng_excel_name_origin]:
            artist_apple_ids += crawler.get_artist_id("https://music.apple.com/kr/search?term=", artist_name)
        total_ids = list(set(artist_apple_ids))
        print(f"한글, 영어로 찾은 아이티스트 아이디 리스트 : {total_ids}")

        # 찾은 아티스트 아이디값을 토대로 input data 와 비교
        for artist_apple_id in total_ids:
            print(f"찾을 아티스트 한글명 영문명 이름 = {kor_excel_name_origin}, {eng_excel_name_origin}")
            kor_apple_name, eng_apple_name = crawler.id_to_kor_eng_name(artist_apple_id)
            if AppleCrawler.compare_artist_name(kor_excel_name_origin, eng_excel_name_origin, kor_apple_name,
                                                eng_apple_name) is True:
                df['애플 아이디'][idx] = artist_apple_id
                #df['비고'][idx] = artist_create_query(kor_apple_name, eng_apple_name, artist_apple_id, memo)
                df['비고'][idx] = artist_create_query(kor_excel_name_origin, eng_excel_name_origin, artist_apple_id, memo)
                print(kor_excel_name_origin, eng_excel_name_origin, kor_apple_name, eng_apple_name, '찾음')
                break
            else:
                continue

    df.to_excel(f"{memo}.xlsx", index=False)


if __name__ == "__main__":
    # excel_file_name = sys.argv[1]
    # memo = sys.argv[2]
    # main(excel_file_name, memo)
    main('크롤링요청_비욘드.xlsx', '2020-09-06 비욘드뮤직 대량아티스트 삽입')