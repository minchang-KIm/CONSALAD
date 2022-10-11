# -*- coding: utf-8 -*-
import os
import sys
import argparse
from pathlib import Path
sys.path.append(str(Path(os.path.abspath(__file__)).parent.parent) + '\handler')
from model.Transfer import Transfer
from handler import query_define
from datetime import datetime, timedelta
from handler import slack_logger

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--flag', required=False, default='daily')
    parser.add_argument('--date', required=False, default=(datetime.today() - timedelta(2)).strftime("%Y-%m-%d"))
    args = parser.parse_args()
    flag = args.flag
    date = args.date

    total_list = []
    fail_list = []
    MAX_LIST_NUM = 2

    if 'total' in flag:
        total_data_list = query_define.get_transfer_total_dict()
        startdate = '2020-02-20'    #토탈 시작 날짜 기입
        enddate  = date
    if 'daily' in flag:
        total_data_list = query_define.get_transfer_daily_dict(date)
        startdate = date
        enddate = date
    sliced_list = [total_data_list[i*MAX_LIST_NUM:(i+1)*MAX_LIST_NUM] for i in range((len(total_data_list) - 1 + MAX_LIST_NUM) // MAX_LIST_NUM )]
    for transfer_data_list in sliced_list:
        list_num = len(transfer_data_list)
        for transfer_data in transfer_data_list:
            transfer = Transfer(transfer_data, startdate, enddate, list_num)
            list = transfer.get_list()
            total_list += list
        fail = transfer.upload(total_list)
        total_list = []
        fail_list.append(fail)

    print(fail_list)
    #slack_logger.slack(msg=fail_list, channel_name='log_midi_deamon')

if __name__ == '__main__':
    main()