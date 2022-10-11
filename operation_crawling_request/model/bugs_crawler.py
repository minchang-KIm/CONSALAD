import re
import os
import time
import langid
import requests
from PIL import Image
from difflib import SequenceMatcher
from urllib import request
import pandas as pd

from random import random
from bs4 import BeautifulSoup


class BugsCrawler():
    def __init__(self):
        self.url_soup_dict = dict()
        self.HEADERS = [
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"},
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}
        ]
        self.count = 0
        self.genre_dict = {}

    def url_to_soup(self, url) -> str:  #500개가 넘어가면 느려진다. 개수 조절 로직을 생각해보자.
        """url을 파라미터로 받아 해당 페이지의 soup를 받아 리턴해주고 중복방지를 위해 딕셔너리에 키 url 밸류 soup로 저장"""
        if url in self.url_soup_dict:
            return self.url_soup_dict[url]
        else:
            header = self.HEADERS[int(random()) * len(self.HEADERS)]
            res = requests.get(url, headers=header)
            time.sleep(random() + 0.5)
            soup = BeautifulSoup(res.text, 'lxml')
            self.url_soup_dict[url] = soup
            return soup

    def search_by_album_name(self, album_name, album_release_date, *artist_name):  # args
        """앨범명, 발매일, *아티스트 이름을 받아서 extract_album_id 함수로 넘기는 함수"""
        url = f"""https://music.bugs.co.kr/search/album?q={album_name}%09{artist_name}&flac_only=false&target=ARTIST_ALBUM&page=1&sort=R"""

        try:
            album_release_date = str(album_release_date).split(' ')[0]
            album_id = self.extract_album_id(url, album_release_date)
            if album_id == None:
                return "NULL"
            return album_id
        except ConnectionError:
            print('연결 문제 있음')
            return 'NULL'

    def extract_album_id(self, url, album_release_date):
        """url, header, 발매일을 받아서 앨범 아이디를 리턴하는 함수"""
        try:
            soup = self.url_to_soup(url)
            albums = soup.select("#container > section > div > ul > li")
            album_ids = []

            # if len(albums) == 1:
            #     album_ids.append(albums[0].find('figure', attrs={'class': 'albumInfo'})['albumid'])
            if len(albums) == 0:
                return 'NULL'

            for album in albums:
                site_album_release_date = str(album.find('time', attrs={'datetime': ''}).get_text()).replace('.', '-')
                if album_release_date == site_album_release_date:
                    print(site_album_release_date, album_release_date)
                    album_id = album.find('figure', attrs={'class': 'albumInfo'})['albumid']
                    album_ids.append(album_id)

            album_ids = list(set(album_ids))
            print(album_ids)

            albumids_to_str = ",".join(album_ids)
            if albumids_to_str == "":
                albumids_to_str = 'NULL'
            else:
                return albumids_to_str
        except ConnectionError:
            print('연결 문제 있음')
            return 'NULL'
        except:
            return 'NULL'

    def search_by_song_name(self, album_name, album_release_date, artist_name):
        """ 트랙 이름, 발매일, 앨범명을 받아서 extract_album_id함수로 넘겨주는 함수"""
        url = f"""https://music.bugs.co.kr/search/track?q={album_name}%09{artist_name}&flac_only=false&target=ARTIST_ALBUM&page=1&sort=R"""
        print(url)
        try:
            album_release_date = str(album_release_date).split(' ')[0]
            album_id = self.extract_album_id_from_song(url, album_release_date)
            print(album_id, album_name, *artist_name)
            if album_id == None:
                return "NULL"
            return album_id
        except ConnectionError:
            print('연결 문제 있음')
            return 'Null'
        except Exception as e:
            print('트랙명으로 찾을 수 없습니다.')
            return 'NULL'

    def extract_album_id_from_song(self, url, album_release_date):
        """url, header, 발매일을 받아서 앨범 아이디를 리턴하는 함수"""
        try:
            soup = self.url_to_soup(url)
            songs = soup.select('#DEFAULT0 > table tbody > tr > td:nth-child(8) > a')
            href_list = []
            for a in songs:  # 곡 에서 앨범 이름, 주소 추출
                href = a.attrs['href']
                href_list.append(href)
            href_list = list(set(href_list))
            for tmp_href in href_list:
                title_url = tmp_href
                soup= self.url_to_soup(title_url)
                bugs_release_date = soup.select(
                    '#container > section.sectionPadding.summaryInfo.summaryAlbum > div > div.basicInfo > table > tbody > tr:nth-child(3) > td > time')
                site_date = bugs_release_date[0].get_text().replace('.', '-')
                print('사이트 발매일은', site_date)
                print('엑셀 파일 발매일은', album_release_date)
                if site_date == album_release_date:  # 사이트 출시일과 엑셀 출시일이 같으면 앨범 아이디 리턴
                    album_id = str(title_url).split('?')[0].split('/')[-1]  # 트랙 주소에서 앨범 아이디 추출
                    return album_id
        except:
            return 'NULL'

    def get_album_id_set(self, sheet1):
        """ 데이터프레임을 파라미터로 받아 앨범 아이디 set에다 넣어 리턴하는 함수"""
        # df = sheet1['앨범 아이디'].dropna()
        df = sheet1['벅스앨범 아이디'].fillna(0)
        # album_id_set = list(set([int(id) for id in df]))
        album_id_set = list([int(id) for id in df])
        return album_id_set

    def get_track_seq_list(self, album_id_list):
        """ get_album_id_set에서 받은 앨범 아이디 리스트를 토대로 각각의 사이트에 들어가 트랙의 개수를 리턴하는 함수 """
        track_num_list = []
        for album_id in album_id_list:
            url = f"""https://music.bugs.co.kr/album/{album_id}"""
            soup = self.url_to_soup(url)
            track_num = len(soup.find_all('p', {'class': 'trackIndex'}))
            track_num_list.append(track_num)
        return track_num_list

    def get_track_name(self, album_id):
        """ 앨범 아이디를 입력받으면 리스트 안에 타이틀 이름을 순서대로 넣은 값을 리턴하는 함수"""
        url = f"""https://music.bugs.co.kr/album/{album_id}"""
        soup = self.url_to_soup(url)
        track_names = soup.select('th > p > a')  # and soup.find_all('p', {'class': 'trackIndex'}
        track_name_list = []
        for track_name in track_names:
            track_name_list.append(track_name.text)
        return track_name_list

    def get_track_url(self, album_id):  # 여기서 트랙의 개수가 나뉨 url의 개수에 따라
        """앨범 아이디를 받아서 트랙 url를 반환하는 함수"""
        url_list = []
        url = f"""https://music.bugs.co.kr/album/{album_id}"""
        soup = self.url_to_soup(url)
        lyric_icon = soup.select('td:nth-child(5) > a')
        for _ in lyric_icon:
            lyric_url = _.attrs['href']
            url_list.append(lyric_url)
        return url_list

    def get_track_id(self, url_list):
        """ url_list를 파라미터로 받아서 트랙 아이디를 리스트로 반환하는 함수"""
        track_id_list = []
        for _ in url_list:
            track_id = str(str(_).split('?')[0]).split('/')[-1]
            track_id_list.append(track_id)
        return track_id_list

    def get_lyric(self, url_list):
        """ url_list를 파라미터로 받아서 가사를 리스트 형식으로  반환하는 함수"""
        lyric_list = []
        for url in url_list:
            try:
                soup = self.url_to_soup(url)
                lyric = soup.select_one(
                    "#container > section.sectionPadding.contents.lyrics > div > div > xmp").get_text()
                lyric_list.append(lyric)
            except:
                lyric = ''
                lyric_list.append(lyric)
        return lyric_list

    def get_artist(self, url_list):
        """ url_list를 파라미터로 받아서 참여 아티스트를 리스트로 반환하는 함수
        트랙 참여정보가 있는 경우, 이를 출력하고 아닌 경우 아티스트를 출력하는 방식 """
        artist_list = []
        for url in url_list:
            soup = self.url_to_soup(url)

            info_count = soup.find_all('th')
            text_list = [i.get_text() for i in info_count]
            if '참여 정보' in text_list:
                info_index = text_list.index('참여 정보') + 1
            else:
                info_index = text_list.index('아티스트') + 1
            artist = soup.select_one(
                f"#container > section.sectionPadding.summaryInfo.summaryTrack > div > div.basicInfo > table > tbody > tr:nth-child({info_index}) > td").get_text()
            artist = re.sub("[\n\r\t]", "", artist).replace("전체 보기", '').replace("작사", " 작사 : ").replace("작곡",
                                                                                                         " 작곡 : ").replace(
                "보컬", " 보컬 : ").replace("피쳐링", " 피쳐링 : ")
            artist_list.append(artist)
        return artist_list

    def get_track_name_url(self, url_list):
        """url_list를 파라미터로 받아서 트랙 이름을 리스트로 반환하는 함수"""
        track_name_list = []
        for url in url_list:
            soup = self.url_to_soup(url)
            track_name = soup.select_one("#container > header > div > h1").get_text()
            track_name = re.sub("[\n\r\t]", "", track_name).replace('[19금]', '')
            track_name_list.append(track_name)
        return track_name_list

    def check_age_limit(self, url_list):
        """url_list를 파라미터로 받아서 19금 여부를 리스트로 반환하는 함수"""
        age_limit_list = []
        for url in url_list:
            soup = self.url_to_soup(url)
            age_limit = soup.select_one(
                "#container > section.sectionPadding.contents.lyrics > div > div > p").get_text()
            age_limit = re.sub("[\n\r\t]", "", age_limit)
            if '청소년 보호법' in age_limit:
                age_limit_list.append("Y")
            else:
                age_limit_list.append("N")
        return age_limit_list

    @staticmethod
    def album_image_download(album_id, dir_name):  # 앨범 아이디.jpg
        """앨범 커버 이미지를 다운로드 3000*3000 픽셀로 resize 저장 위치는 상위폴더에서 album_cover_image 폴더 생성"""
        try:
            url = f"https://image.bugsm.co.kr/album/images/original/{str(album_id)[0:-2]}/{album_id}.jpg"
            os.chdir("..")
            os.chdir("bugs_crawling/")
            if not os.path.exists(dir_name):
                os.mkdir(dir_name)
            os.chdir(dir_name + "/")
            if os.path.exists(f"{album_id}.jpg"):  # 앨범 파일이 있을 경우
                return 0
            os.system(f"curl " + url + f" > {album_id}.jpg")
            img = Image.open(f'{album_id}.jpg')
            # img_resize = img.resize((3000, 3000), Image.LANCZOS)
            img_resize = img.resize((3000, 3000))
            img_resize.save(f'{album_id}.jpg')
        except:
            return 0

    def check_service_available(self, url_list):
        """트랙의 현재 서비스 여부를 확인하는 함수"""
        play_limit_list = []
        for url in url_list:
            soup = self.url_to_soup(url)
            try:
                play_limit = soup.select_one(
                    "#container > section.sectionPadding.contents.infoMessage > div > ul").get_text()
                play_limit = re.sub("[\n\r\t]", "", str(play_limit))
                if '권리사의 요청' in play_limit:
                    play_limit_list.append("N")
                else:
                    play_limit_list.append("Y")
            except:
                play_limit_list.append("Y")
        return play_limit_list

    def count_bugs_track_number(self, album_id, sheet2_count):  # 중복 건너뛰기도 넣기
        """해당 앨범의 전체 트랙 개수를 불러와 트랙개수를 비교하는 함수"""  # cd번호랑 스퀀스 번호 가져와서 갖대 대고 비교질하면 너무 헤비해진다(진짜로 느려짐)
        xl_count = sheet2_count[album_id]
        soup = self.url_to_soup(f"https://music.bugs.co.kr/album/{album_id}")
        # ret = soup.select("table > tbody > tr[rowtype = 'track']")
        track_num = len(soup.find_all('p', {'class': 'trackIndex'}))
        print(track_num, xl_count)
        # url_soup_dict.pop(bugs.get_track_url(album_id)) 딕셔너리가 너무 많아져서 느려질 때 (soup가 마지막으로 쓰이는 함수를 잘 찾아야 한다.
        if track_num == xl_count:
            return 'Y'
        else:
            return 'N'

    def get_playtime(self, url_list):
        """트랙의 url을 받아 트랙의 플레이타임을 리턴하는 함수"""
        for url in url_list:
            soup = self.url_to_soup(url)
            info_count = soup.find_all('th')
            text_list = [i.get_text() for i in info_count]
            if '재생 시간' in text_list:
                info_index = text_list.index('재생 시간') + 1
            else:
                return ""
            play_time = soup.select_one(
                f"#container > section.sectionPadding.summaryInfo.summaryTrack > div > div.basicInfo > table > tbody > tr:nth-child({info_index}) > td > time").get_text()
            play_time = re.sub("[\n\r\t]", "", str(play_time))
            return play_time

    def get_genre(self, album_id):
        """앨범아이디를 가져와 앨범의 장르를 리턴하는 함수"""
        genre_add = ''
        if album_id in self.genre_dict.keys():
            return self.genre_dict[album_id]
        url = f"https://music.bugs.co.kr/album/{album_id}"
        soup = self.url_to_soup(url)
        genre_list = soup.select("#container > section.sectionPadding.summaryInfo.summaryAlbum > div > div.basicInfo > table > tbody > tr:nth-child(4) > td > a")
        if len(genre_list) == 0:
            return ''
        for genre in genre_list:
            genre_add += ', '+genre.get_text()
        genre = genre_add[2::]         #앞에 붙은 , 제거용
        self.genre_dict[album_id] = genre
        return genre

    def find_audio_language(self, lyric):
        """가사를 파라미터로 받아 한중일 언어를 구분하고 정확도도 높고 공식 라이브러리에 올라와있어 따로 학습모델을 다운받아놓을 필요도 없는 langid모듈을 사용"""
        if lyric == '':
            return ''
        lyric = re.sub("[\n\r\t-=+,#/\?:^.@*\"※~ㆍ!』‘|\(\)\[\]`\'…》\”\“\’·]", "", lyric)
        lang = langid.classify(lyric)[0]
        return lang

    def get_trackname_accuracy(self, excel_trackname, bugs_trackname):
        """엑셀 트랙명과 크롤링한 트랙명의 정확도를 리턴"""
        if excel_trackname == '' or bugs_trackname == '':
            return ''
        accuracy = SequenceMatcher(None,excel_trackname,bugs_trackname).ratio()
        accuracy = round(accuracy, 2)       #소수점 셋째자리에서 반올림
        return accuracy

if __name__ == "__main__":
    bugs = BugsCrawler()        # 가변 문서화 독스트링
    print(bugs.search_by_song_name('해변의 여인', '2006-09-01', 'Various Artists'))
    #print(bugs.search_by_album_name('Forever Best 005 (우리 노래 전시회 Ⅰ Ⅱ Ⅲ)', '2001-09-01 00:00:00'))
    # print("bugs.count_bugs_track_number", bugs.count_bugs_track_number.__doc__)
    # print("bugs.url_to_soup", bugs.url_to_soup.__doc__)
    # print("bugs.get_track_seq_list", bugs.get_track_seq_list.__doc__)
    # print("bugs.search_by_album_name", bugs.search_by_album_name.__doc__)
    # print("search_by_song_name", bugs.search_by_song_name.__doc__)
    # print("get_track_id", bugs.get_track_id.__doc__)
    # print("get_track_url", bugs.get_track_url.__doc__)
    # print("check_service_available", bugs.check_service_available.__doc__)
    # print("check_age_limit", bugs.check_age_limit.__doc__)
    # print("get_artist", bugs.get_artist.__doc__)
    # print("get_lyric", bugs.get_lyric.__doc__)
    # print("get_track_name", bugs.get_track_name.__doc__)
    # print("album_image_download", bugs.album_image_download.__doc__)
    # print("get_album_id_set", bugs.get_album_id_set.__doc__)
    # print("extract_album_id", bugs.extract_album_id.__doc__)
    # print("extract_album_id_from_song", bugs.extract_album_id_from_song.__doc__)
    # print("get_track_name_url", bugs.get_track_name_url.__doc__)


    """

    """
