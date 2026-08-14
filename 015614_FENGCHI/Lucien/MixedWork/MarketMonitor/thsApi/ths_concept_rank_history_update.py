# coding: utf-8
# Author：fengchi863
# Date ：2021/10/19 14:26

from xquant.thirdpartydata.fic_api_data import FicApiData
from dataApi import tradeDate, stockList
import pandas as pd
import numpy as np
import time
import os
import json
import pickle

root_path = '/data/user/015614/daily/同花顺数据/'
ths_concept_rank_temp_path = root_path + '同花顺概念排名/everyday_temp/'
ths_concept_rank_path = root_path + '同花顺概念排名/everyday/'
ths_concept_rank_history_path = root_path + '同花顺概念排名/history/'

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

def get_top3_concept(df, date):
    df = df.sort_values(['ENTRYDATE'])
    df = df[df['ENTRYDATE'].astype(int) <= date * 1000000]
    top3_concept = list()
    for rank in ['1', '2', '3']:
        try:
            tmp_df = df.query('FITDEGRANK == %s' % rank)
            top3_concept.append(tmp_df.iloc[-1]['CONCEPTTYPENAME'])
        except:
            pass
    return top3_concept


top3_concept_dict = dict()
fad = FicApiData()
resource = 'ZX_CONCEPTION'
step = 1000
today_date = tradeDate.get_today(dividing_point=0)
# stk_list = stockList.clean_stock_list()
# stk_code_list = list(map(lambda x: str(x).zfill(6), stk_list.columns.tolist()))


def fetch_and_save():
    ret_df = pd.DataFrame()
    for concept_type in ['1', '2', '3']:
        print(f'查询{concept_type}')
        paramMaps = {"CONCEPTTYPE": concept_type}
        orderBy = "SECUABBR"
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
            col = ['CONCEPTLEADRANK',
                   'CONCEPTTYPE',
                   'CONCEPTTYPECODE',
                   'CONCEPTTYPENAME',
                   'ENTRYDATE',
                   'EXCHANGECODE',
                   'EXCHANGENAME',
                   'FITDEGRANK',
                   'SECUABBR',
                   'TRADINGCODE']
            df = df[col]
            ret_df = ret_df.append(df, ignore_index=True)
        # if len(df) == 0:
        #     top3_concept_dict.update({stockList.trans_int2windcode(int(stk_code)): ''})
        # df['ENTRYDATE'] = df['ENTRYDATE'].map(lambda x: time.strftime('%Y%m%d%H%M%S', time.localtime(x / 1000)))
        # top3_concept = get_top3_concept(df, stk_code)
        # top3_concept_dict.update({stockList.trans_int2windcode(int(stk_code)): ','.join(top3_concept)})
    ret_df['ENTRYDATE'] = ret_df['ENTRYDATE'].map(lambda x: time.strftime('%Y%m%d%H%M%S', time.localtime(x / 1000)))
    save_pickle(ret_df, ths_concept_rank_temp_path, f'{today_date}.pkl')
    return ret_df


if os.path.exists(ths_concept_rank_temp_path + f'{today_date}.pkl'):
    ret_df = load_pickle(ths_concept_rank_temp_path + f'{today_date}.pkl')
else:
    ret_df = fetch_and_save()

date_list = tradeDate.get_date_range(20210101, today_date)

for tmp_date in date_list:
    print(tmp_date)
    tmp = ret_df.groupby(['TRADINGCODE', 'SECUABBR']).apply(lambda x: get_top3_concept(x, tmp_date))
    tmp = tmp.reset_index()
    ret_dict = {}
    for idx in tmp.index:
        tmp_cont = tmp.iloc[idx]
        stk_code = stockList.trans_int2windcode(int(tmp_cont['TRADINGCODE']))
        stk_name = tmp_cont['SECUABBR']
        stk_concept = ','.join(tmp_cont[0])
        ret_dict.update({stk_code: stk_concept})

    ret_json = json.dumps(ret_dict, ensure_ascii=False)

    file_object = open(ths_concept_rank_history_path + '同花顺概念排名%d.json' % tmp_date, 'w')
    file_object.write(ret_json)
    file_object.close()
