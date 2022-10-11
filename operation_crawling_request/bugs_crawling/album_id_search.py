import os
import sys
import pandas as pd
import urllib.parse
from pathlib import Path
sys.path.append(str(Path(os.path.abspath(__file__)).parent.parent))
from model import bugs_crawler
pd.set_option('mode.chained_assignment',  None)

dict = {}           # 인터넷 중복 검색 방지 딕셔너리 조건 : 앨범명, 앨범 아티시트가 같을 때
def main(xl_name, memo):
    """Input = 앨범명 앨범 아티스트명 발매일"""
    bugs = bugs_crawler.BugsCrawler()
    df = pd.read_excel(f"{xl_name}.xlsx")
    df["벅스앨범 아이디"] = ""
    for idx in range(df.shape[0]):
        xl_album_name = df["앨범명"][idx]
        xl_album_name = str(xl_album_name).replace(" OST", "")
        xl_album_artist = df["앨범아티스트"][idx]
        xl_album_release_date = df["앨범공급일"][idx]
        xl_album_release_date = str(xl_album_release_date).split(" ")[0]
        quote_album_name = urllib.parse.quote(string=str(xl_album_name))
        quote_artist_name = urllib.parse.quote(string=str(xl_album_artist))

        if xl_album_name in dict:           #{앨범명 : {앨범 아티스트 : 벅스앨범 아이디}}
            if xl_album_artist in dict[xl_album_name]:
                df["벅스앨범 아이디"][idx] = dict[xl_album_name][xl_album_artist]
                continue
        else:
            print(xl_album_name, xl_album_artist, xl_album_release_date)

        bugs_album_id = bugs.search_by_album_name(quote_album_name, xl_album_release_date, quote_artist_name)
        # if bugs_album_id is None:

        # if bulgs is None:


        if bugs_album_id == "NULL":
            bugs_album_id2 = bugs.search_by_album_name(quote_album_name, xl_album_release_date)
            if bugs_album_id2 == "NULL":
                bugs_album_id3 = bugs.search_by_song_name(quote_album_name, xl_album_release_date, quote_artist_name)
                if bugs_album_id3 == "NULL":
                    df["벅스앨범 아이디"][idx] = ""
                else:
                    df["벅스앨범 아이디"][idx] = bugs_album_id3
                    #딕셔너리에 idx 넣어서 올리기
                    temp_dict = {}
                    temp_dict[xl_album_artist] = bugs_album_id3
                    dict[xl_album_name] = temp_dict
            else:
                df["벅스앨범 아이디"][idx] = bugs_album_id2
                temp_dict = {}
                temp_dict[xl_album_artist] = bugs_album_id2
                dict[xl_album_name] = temp_dict
        else:
            df["벅스앨범 아이디"][idx] = bugs_album_id
            temp_dict = {}
            temp_dict[xl_album_artist] = bugs_album_id
            dict[xl_album_name] = temp_dict
    df.to_excel(f"{memo}.xlsx", index=False)


if __name__ == "__main__":
    # xl_name = sys.argv[1]
    # memo = sys.argv[2]
    # main(xl_name, memo)
    main("크롤링요청_비욘드", "비욘드_after_albumid_2")