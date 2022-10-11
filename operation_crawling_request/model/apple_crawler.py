import traceback
import pandas as pd
from urllib import parse
from model.crawler import Crawler
from selenium.webdriver.common.by import By


class AppleCrawler(Crawler):
    def __init__(self):
        super().__init__()
        self.artist_id_dict = dict()  # {artist_id: ["한글명": 한글, "영문명":영문]}

    @staticmethod
    def read_excel(excel_name):
        df = pd.read_excel(excel_name)
        df.fillna("", inplace=True)
        df['애플 아이디'] = ""
        df['비고'] = ""
        print("엑셀 input 읽기완료")
        return df

    # 아티스트 페이지에서 아티스트 이름 가져오는 함수
    def get_name(self, url):
        try:
            print(f'{url.split("/")[-1]} 의 이름 찾는중 ...', end='')
            self.driver.get(url)
            self.driver.implicitly_wait(10)
            artist_div_class = ".artist-header__product-title-product-name"
            self.selenium_wait(self.driver, By.CSS_SELECTOR, artist_div_class)
            name = self.driver.find_element(By.CSS_SELECTOR, artist_div_class).text
            print(name)
            return name
        except Exception as e:
            print(e)
            return ""

    def get_artist_id(self, url, name):
        ''' 작가 프로필에 직접 들어가 애플 아이디를 가져오는 함수'''
        if name.strip() == "":
            return []
        try:
            print(f"검색 url : {url}{name}")
            url = f"{url}{parse.quote(name)}"
            artist_ids = []
            self.driver.get(url)
            self.driver.implicitly_wait(10)
            self.selenium_wait(self.driver, By.CSS_SELECTOR,
                               '.lockup.search-swoosh.linkable.artist.no-subline-destination')
            self.selenium_wait(self.driver, By.CSS_SELECTOR, '.line.lockup__name')
            artists = self.driver.find_elements(By.CSS_SELECTOR,
                                                '.lockup.search-swoosh.linkable.artist.no-subline-destination')
            for artist in artists:
                artist_link = artist.find_element(By.CSS_SELECTOR, '.line.lockup__name').get_attribute('href')
                artist_id = artist_link.split('/')[-1]
                artist_ids.append(artist_id)

            return artist_ids
        except Exception as e:
            print(f"'{name}'에 대한 검색결과 없음", e)
            return []



    def id_to_kor_eng_name(self, artist_id):

        if artist_id in self.artist_id_dict:
            return [self.artist_id_dict[artist_id]['한글명'], self.artist_id_dict[artist_id]['영문명']]

        kor_url = f"https://music.apple.com/kr/artist/{artist_id}"
        eng_url = f"https://music.apple.com/ur/artist/{artist_id}"
        kor_name = self.get_name(kor_url)
        eng_name = self.get_name(eng_url)
        self.artist_id_dict[artist_id] = {"한글명": str(kor_name), "영문명": str(eng_name)}
        return [kor_name, eng_name]

    @staticmethod
    def compare_artist_name(excel_kor, excel_eng, apple_kor, apple_eng):
        excel_kor = excel_kor.replace(" ", "")
        excel_eng = excel_eng.replace(" ", "")
        apple_kor = apple_kor.replace(" ", "")
        apple_eng = apple_eng.replace(" ", "")
        if excel_kor == "":
            excel_kor = excel_eng
        if excel_eng == "":
            excel_eng = excel_kor

        if excel_kor == apple_kor and excel_eng == apple_eng:
            return True

        return False

if __name__ == "__main__":
    crawler = AppleCrawler()
    # artist_list = crawler.read_input_excel("C:\\Users\\jhkim\\Desktop\\midi-deamon\\midi-deamon\\operation_crawling_request\\apple_id_search\\Input_Data.xlsx")
    # print(crawler.check_artist_is_exist(artist_list[0]['국문'], artist_list[0]['영문']))
    #print(crawler.get_artist_id('https://music.apple.com/kr/search?term=','이수영'))
    print(crawler.get_name('https://music.apple.com/ur/artist/1053924796'))