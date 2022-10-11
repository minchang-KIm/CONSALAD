import json
import sys
import csv
import argparse
import requests
from datetime import datetime, timedelta
from math import ceil
import slack_logger


def main():
    """조회 기간별 음악 사용로그를 페이징하여 조회한다."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--startdate', required=False, default=(datetime.today() - timedelta(2)).strftime("%Y%m%d"))
    parser.add_argument('--enddate', required=False, default=(datetime.today() - timedelta(2)).strftime("%Y%m%d"))
    args = parser.parse_args()
    startdate = str(args.startdate).replace('-', '')
    enddate = str(args.enddate).replace('-', '')

    condition = True
    numOfRows = 10
    totalCount = 1
    pageNo = 1 #로 두고 리스폰스 계산값으로 변경 while break
    clientId = '28067'
    apiKey = '9f72bdae-3d88-46e6-940e-ec23c9121ec8'

    f = open('result.csv', 'w', newline='', encoding='utf-8')
    wr = csv.writer(f)
    wr.writerow(['totalCount', 'serviceDt', 'ospSysCd', 'serviceCd', 'serviceNm', 'uci', 'useCnt'])

    while condition == True:
        datas = {'pageNo': pageNo,
                 'numOfRows': numOfRows, #페이지당 로우 수 default 10, (인수로 받을 만큼 바뀌는 경우가 많지는 않을 것 같다.)
                 'searchStartDt': startdate,
                 'searchEndDt': enddate
                 }   #search StartDt는 해당 일로부터 2일 전으로 + date format은 20220706
        datas = json.dumps(datas)
        print(datas)
        #exit()
        url = 'http://15.165.177.253:8989/works/music'

        try:
            response = requests.get(url, headers={'clientId': clientId, 'apiKey': apiKey, "Content-Type": 'application/json'}, params=datas)
            res = response.json()
            print(res)
        except Exception as e:
            print(pageNo,'페이지 전송 오류발생', e)
            #slack_logger.slack(msg='전송 오류발생', channel_name='log_midi_deamon')
            pageNo += 1
            response = requests.get(url, headers={'clientId': clientId, 'apiKey': apiKey}, params=datas)
            res = response.json()
            print(res)

        for dict in res:        #페이지 안 딕셔너리 개수만큼 반복 페이지당 row 수 default 10
            resultCd = dict['resultCd']
            resultMsg = dict['resultMsg']
            numOfRows = dict['numOfRows']
            pageNo = dict['pageNo']
            totalCount = dict['totalCount']
            serviceDt = dict['serviceDt']
            ospSysCd = dict['ospSysCd']
            serviceCd = dict['serviceCd']
            serviceNm = dict['serviceNm']
            uci = dict['uci']
            useCnt = dict['useCnt']
            wr.writerow(totalCount, serviceDt, ospSysCd, serviceCd, serviceNm, uci, useCnt) #함수로 빼면 문서 열었다 닫았다 반복
        if ceil(totalCount/numOfRows) == pageNo:    #올림으로 총 페이지 수 확인 페이지수로 for문 돌리고 전체 결과 수 나누기 한 페이지 결과 수 = 페이지 수
            condition = False
        pageNo += 1  #페이지 수 증가
    f.close()


if __name__ == '__main__':
    #date format은 20220706
    main()