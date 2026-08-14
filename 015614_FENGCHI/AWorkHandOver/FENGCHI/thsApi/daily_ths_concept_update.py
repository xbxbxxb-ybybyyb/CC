# coding: utf-8
# Author：fengchi863
# Date ：2021/10/14 14:29

from xquant.thirdpartydata.fic_api_data import FicApiData
import json
import pandas as pd
import numpy as np
from dataApi import stockList
import datetime as dt
import requests

new_ths_path = '/data/group/800442/800319/Afengchi/概念板块同花顺/'


def get_today_date():
    return int(dt.datetime.today().strftime('%Y%m%d'))


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


def update_dict(concept_dict, concept_name, stk_id, stk_name, filter_concept):
    if concept_name in filter_concept:
        return
    stk_code = stockList.trans_int2windcode(stk_id)
    if concept_name in concept_dict:
        concept_dict[concept_name].update({stk_code: stk_name})
    else:
        concept_dict[concept_name] = dict({stk_code: stk_name})


# 清洗新兴概念和其他概念
def filter_concept():
    filter_concepts = set()
    step = 1000
    for concept_type in ['2', '3']:
        fad = FicApiData()
        resource = 'ZX_CONCEPTION'
        paramMaps = {"CONCEPTTYPE": concept_type}
        orderBy = "ENTRYDATE"
        selectedFields = ''
        rownum = step
        startrow = 0
        ret = fad.get_fic_api_data(resource, paramMaps, selectedFields, startrow, rownum, orderBy)
        total_count = ret['totalCount']

        startrows = list(map(lambda x: x * step, list(range(0, int(np.ceil(total_count / step))))))

        for startrow in startrows:
            print(f'filter_concept: {startrow}/{total_count}')
            ret = fad.get_fic_api_data(resource, paramMaps, selectedFields, startrow, rownum, orderBy)
            df = pd.DataFrame(ret['data'])
            filter_concepts = filter_concepts | set(df['CONCEPTTYPENAME'].tolist())

    return filter_concepts


filter_concepts = filter_concept()

concept_dict = dict()
fad = FicApiData()
resource = 'ZX_CONCEPTIONSECU'
exchange_codes = ['101', '105']
step = 1000

for exchange_code in exchange_codes:
    paramMaps = {"EXCHANGECODE": exchange_code}
    orderBy = "TRADINGCODE"
    selectedFields = ''
    rownum = step
    startrow = 0
    ret = fad.get_fic_api_data(resource, paramMaps, selectedFields, startrow, rownum, orderBy)
    total_count = ret['totalCount']

    startrows = list(map(lambda x: x * step, list(range(0, int(np.ceil(total_count / step))))))
    if startrows is []:
        print('今日无数据，用昨日的概念数据')

    for startrow in startrows:
        print(f'{startrow}/{total_count}')
        ret = fad.get_fic_api_data(resource, paramMaps, selectedFields, startrow, rownum, orderBy)
        df = pd.DataFrame(ret['data'])
        for idx in df.index:
            tmp_row = df.loc[idx]
            concept_name = tmp_row['CONCEPTIONNAME']
            stk_id = int(tmp_row['TRADINGCODE'])
            stk_name = tmp_row['SECUABBR']
            update_dict(concept_dict, concept_name, stk_id, stk_name, filter_concepts)

ret_json = json.dumps(concept_dict, ensure_ascii=False)

today_date = get_today_date()
file_object = open(new_ths_path + '概念板块同花顺%d.json' % today_date, 'w')
file_object.write(ret_json)
file_object.close()
send_message(['015614'], '概念板块同花顺%d更新完成' % today_date)

