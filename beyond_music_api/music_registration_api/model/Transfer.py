import json
import os
import sys
import requests
from pathlib import Path
sys.path.append(str(Path(os.path.abspath(__file__)).parent.parent))
class Transfer:
    def __init__(self, transfer_data_list, startdate, enddate, list_num):
        """ input dict 양식 transfer list 안에 header reportOfficer, totalCnt, list가 존재하고 각각이 딕셔너리이다."""
        self.apiKey = "9f72bdae-3d88-46e6-940e-ec23c9121ec8"
        self.clientId = "28067"
        self.apiDiv = "1"
        self.reptChrrName = "김민창"
        self.reptChrrPosi = "개발2팀 수습사원"
        self.reptChrrTelx = "010-7761-3534"
        self.reptChrrMail = "mckim@consalad.net"
        self.trstOrgnCode = 1545
        self.rgsldnt = "luminantent"
        self.commName = "Luminant Entertainment"
        self.commTelx = "02-538-8205"
        self.commRepsName = "고운"
        self.conditionCd = 1
        self.totalCnt = list_num #transfer_data_list['totalCnt']
        self.rgstOrgnName = transfer_data_list['list']['rgstOrgnName']
        self.commWorksId = transfer_data_list['list']['commWorksId']
        self.worksTitle = transfer_data_list['list']['worksTitle']
        self.nationcd = transfer_data_list['list']['nationcd']
        self.albumTitle = transfer_data_list['list']['albumTitle']
        self.albumLable = transfer_data_list['list']['albumLable']
        self.diskSide = transfer_data_list['list']['diskSide']
        self.trackNo = transfer_data_list['list']['trackNo']
        self.albumIssuYear = transfer_data_list['list']['albumIssuYear']

        self.lyrc = transfer_data_list['list']['lyrc']
        self.comp = transfer_data_list['list']['comp']
        self.arra = transfer_data_list['list']['arra']
        self.tran = transfer_data_list['list']['tran']
        self.sing = transfer_data_list['list']['sing']
        self.perf = transfer_data_list['list']['perf']
        self.prod = transfer_data_list['list']['prod']

        self.commMgntCd = 2#int(transfer_data_list['list']['commMgntCd'])
        self.liceMgntCd = 0#int(transfer_data_list['list']['liceMgntCd'])
        self.perfMgntCd = 0#int(transfer_data_list['list']['perfMgntCd'])
        self.prodMgntCd = 0#int(transfer_data_list['list']['prodMgntCd'])
        self.uci = transfer_data_list['list']['uci']
        self.musicType = "음반"
        self.startDate = startdate
        self.endDate = enddate

        self.try_count = 1
        self.fail_list = []

    def get_list(self):
        list = [{
                "rgstOrgnName": self.rgstOrgnName,
                "commWorksId": self.commWorksId,
                "worksTitle": self.worksTitle,
                "nationcd": self.nationcd,
                "albumTitle": self.albumTitle,
                "albumLable": self.albumLable,
                "diskSide": self.diskSide,
                "trackNo": self.trackNo,
                "albumIssuYear": self.albumIssuYear,
                "lyrc": self.lyrc,
                "comp": self.comp,
                "arra": self.arra,
                "tran": self.tran,
                "sing": self.sing,
                "perf": self.perf,
                "prod": self.prod,
                "commMgntCd": self.commMgntCd,
                "liceMgntCd": self.liceMgntCd,
                "perfMgntCd": self.perfMgntCd,
                "prodMgntCd": self.perfMgntCd,
                "uci": self.uci,
                "musicType": self.musicType,
                "startDate": self.startDate,
                "endDate": self.endDate
            }]
        return list

    def make_header(self):
        """ 전송 데이터의 헤더 부분을 생성하는 함수"""
        header_format = {"apiKey": self.apiKey, "clientId": self.clientId, "apiDiv": self.apiDiv, "Content-Type": 'application/json'}
        return header_format

    def make_raw_data(self, data_list):
        """ 전송 데이터의 raw data 부분을 생성하는 함수"""
        total_list = []
        for list in data_list:
            raw_data_format = {
            "reportOfficer": {
                "reptChrrName": self.reptChrrName,
                "reptChrrPosi": self.reptChrrPosi,
                "reptChrrTelx": self.reptChrrTelx,
                "reptChrrMail": self.reptChrrMail
            },
            "trustOfficer": {
                "trstOrgnCode": self.trstOrgnCode,
                "rgstIdnt": self.rgsldnt,
                "commName": self.commName,
                "commTelx": self.commTelx,
                "commRepsName": self.commRepsName,
                "conditionCd": self.conditionCd
            },
            "totalCnt": self.totalCnt,
            "list": [{
                "rgstOrgnName": list['rgstOrgnName'],
                "commWorksId": list['commWorksId'],
                "worksTitle": list['worksTitle'],
                "nationcd": list['nationcd'],
                "albumTitle": list['albumTitle'],
                "albumLable": list['albumLable'],
                "diskSide": list['diskSide'],
                "trackNo": list['trackNo'],
                "albumIssuYear": list['albumIssuYear'],
                "lyrc": list['lyrc'],
                "comp": list['comp'],
                "arra": list['arra'],
                "tran": list['tran'],
                "sing": list['sing'],
                "perf": list['perf'],
                "prod": list['prod'],
                "commMgntCd": list['commMgntCd'],
                "liceMgntCd": list['liceMgntCd'],
                "perfMgntCd": list['perfMgntCd'],
                "prodMgntCd": list['perfMgntCd'],
                "uci": list['uci'],
                "musicType": list['musicType'],
                "startDate": list['startDate'],
                "endDate": list['endDate']
                }]
            }
            if len(total_list) == 0:
                total_list.append(raw_data_format)
            else:
                total_list[0]['list'].append(list)
        return total_list

    def upload(self, data_list):
        """ combine_header_data에서 받은 데이터 리턴 값 request 양식으로 업로드"""
        try:
            headers = self.make_header()
            datas = self.make_raw_data(data_list)
            datas = json.dumps(datas[0])
            url = 'http://15.165.177.253:8989/works/music'
            response = requests.post(url=url, data=datas, headers=headers, timeout=30)
            print(response)
            if response.status_code == 500:
                raise Exception('에러 코드 500')
            res = response.json()
            print(res)
            if res['resultCd'] == 200:
                print('전송 완료')
            elif res['resultCd'] == 400:
                print('전송 실패', self.worksTitle, res['resultMsg'])
                self.fail_list.append({self.worksTitle: res['resultMsg']})
            return self.fail_list

        except Exception as e:
            print('requests 전송 중 오류 발생', self.try_count,'번째 시도', e)
            if self.try_count == 5:
                #slack_logger.slack(msg='mididaemon/beyond_music_api/Transfer.py 오류 발생', channel_name='log_midi_deamon')
                self.fail_list.append({self.worksTitle : 'Connection_Error'})
                return self.fail_list
            self.try_count += 1
            self.upload(data_list)