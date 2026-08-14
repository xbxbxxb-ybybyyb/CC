# coding: utf-8
# Author：fengchi863
# Date ：2021/1/12 13:11
import requests
import json
import h5py
import os
import pickle
from datetime import datetime
import pandas as pd, numpy as np
from ShortTermTrading.conf.path_conf import active_concept_data_path
from ShortTermTrading.dataApi.tradeDate import get_pre_trade_date
from ShortTermTrading.dataApi.stockList import trans_int2windcode
from ShortTermTrading.dataApi import stockList
from xquant.factordata import FactorData


def get_stock_name_dict():
    # stock_code_and_name = pd.read_excel('/data/user/fengchi/MyWork/BullClient/other_data/stock_code_and_name.xlsx',
    #                                     encoding='gb18030')
    # stock_code_and_name_dict = {}
    #
    # for idx, curr in stock_code_and_name.iterrows():
    #     stock_code = curr['证券代码']
    #     stock_name = curr['证券简称']
    #     stock_code_and_name_dict[stock_code] = stock_name
    today_date = get_today_date()
    fd = FactorData()
    df = fd.get_factor_value('Basic_factor', mddate=['%s' % today_date], factor_names=['short_name'])
    stock_code_and_name_dict = df['short_name'].to_dict()
    return stock_code_and_name_dict

def get_stock_name(stk_id):
    if type(stk_id) == int:
        stk_id = trans_int2windcode(stk_id)
    stock_name_dict = get_stock_name_dict()
    if stk_id in list(stock_name_dict.keys()):
        return stock_name_dict[stk_id]
    else:
        return stk_id

# 铃客发消息
def send_message(users, msg):
    token_url = ('http://168.7.124.15:1080/cgi-bin/gettoken?corpid=wwd53282142c96185d&corpsecret='
                 'Pk0ewu3nuo6JhEaBj_EkuCyiALj0RuISWuZeJcoPdhI')
    send_url = " http://168.7.124.15:1080/cgi-bin/message/send?access_token={}"
    con = requests.get(token_url)
    json_text = json.loads(con.text)
    access_token = json_text["access_token"]
    post_url = send_url.format(access_token)

    for user in users:
        data = {"touser": user,
                "msgtype": "text",
                "agentid": 1000033,
                "text": {"content": msg}}
        json_data = json.dumps(data)
        requests.post(post_url, json_data)


def send_file(users, file):
    token_url = ('http://168.7.124.15:1080/cgi-bin/gettoken?corpid=wwd53282142c96185d&corpsecret='
                 'Pk0ewu3nuo6JhEaBj_EkuCyiALj0RuISWuZeJcoPdhI')
    send_url = "http://168.7.124.15:1080/cgi-bin/message/send?access_token={}"
    con = requests.get(token_url)
    json_text = json.loads(con.text)
    access_token = json_text["access_token"]
    post_url = send_url.format(access_token)

    img_url = "http://168.7.124.15:1080/cgi-bin/media/upload?access_token={}&type=file".format(access_token)
    files = {'file': open(file, 'rb')}
    media_id = requests.post(img_url, files=files).json()['media_id']
    if isinstance(users, list):
        users = '|'.join(users)

    media = {"touser": users,
             "msgtype": "file",
             "agentid": 1000033,
             "file": {"media_id": media_id}}
    json_media = json.dumps(media, ensure_ascii=False).encode('utf-8')
    requests.post(post_url, json_media)

def get_active_concept_list():
    f = h5py.File(active_concept_data_path)
    active_concept_list2020 = list(f.keys())
    return active_concept_list2020

# 计算大小
def get_df_sum(df: pd.DataFrame):
    return df.sum().sum()

def save_pickle(file, floder_path, file_name):
    if not os.path.exists(floder_path):
        os.makedirs(floder_path)
    if type(file) == pd.Series or type(file) == pd.DataFrame:
        file.to_pickle(floder_path + file_name)
    if type(file) == list or type(file) == dict:
        op = open(floder_path + file_name, 'wb+')
        pickle.dump(file, op)
        op.close()
    print('file has been saved in %s' % (floder_path + file_name))

def load_pickle(file_path):
    op = open(file_path, 'rb+')
    return pickle.load(op)

def save_xlsx(file, floder_path, file_name):
    if not os.path.exists(floder_path):
        os.makedirs(floder_path)
    file.to_excel(floder_path + file_name)

def get_today_date():
    now_datetime = datetime.now()
    now_date = int(now_datetime.strftime('%Y%m%d'))
    return now_date

def get_yesterday_date():
    now_datetime = datetime.now()
    now_date = int(now_datetime.strftime('%Y%m%d'))
    yes_date = get_pre_trade_date(now_date)
    return yes_date

def get_tomorrow_date():
    now_datetime = datetime.now()
    now_date = int(now_datetime.strftime('%Y%m%d'))
    yes_date = get_pre_trade_date(now_date, -1)
    return yes_date

def get_curr_datetime():
    now_datetime = datetime.now()
    now_time = int(now_datetime.strftime('%H%M%S'))
    return now_time

# 剔除科创板股票
def del_star_stk(df:pd.DataFrame):
    col = df.columns.tolist()
    col = [x for x in col if not x // 1000 == 688]
    df = df[col]
    return df