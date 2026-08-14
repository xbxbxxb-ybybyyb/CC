# coding: utf-8
# Author：fengchi863
# Date ：2021/10/14 14:29

from xquant.thirdpartydata.fic_api_data import FicApiData
import json
import pandas as pd
import numpy as np
from ShortTermTrading.dataApi import stockList
from FaaMonitor.conf.path_conf import new_ths_path
from FaaMonitor.Util.DtUtil import DtUtil
from FaaMonitor.Util.tools import send_message


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

today_date = DtUtil.get_today_date()
file_object = open(new_ths_path + '概念板块同花顺%d.json' % today_date, 'w')
file_object.write(ret_json)
file_object.close()
send_message(['015614'], '概念板块同花顺%d更新完成' % today_date)
