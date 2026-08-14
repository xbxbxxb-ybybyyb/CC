# coding: utf-8
# Author：fengchi863
# Date ：2021/10/21 15:59

import sys
sys.path.append('/data/user/015614/Lucien')

import pandas as pd, numpy as np
from dataApi import tradeDate
from LucienUtil.FileUtil import FileUtil
from xquant.factordata import FactorData
from dataApi.sendInfo import send_message

output_path = '/data/user/015614/daily/同花顺数据/同花顺概念/'
new_ths_path = '/data/user/015614/daily/同花顺数据/概念板块同花顺/'

def reverse_dict(concept_dict):
    new_dict = dict()
    for key in concept_dict.keys():
        stk_list = list(concept_dict[key].keys())
        for stk in stk_list:
            if stk not in new_dict.keys():
                new_dict[stk] = key
            else:
                new_dict[stk] = new_dict[stk] + '，%s' % key
    new_dict = dict(sorted(new_dict.items(), key=lambda x: x[0], reverse=False))
    return new_dict


if __name__ == '__main__':
    today_date = tradeDate.get_today(dividing_point=0)
    dic = pd.read_json(new_ths_path + '概念板块同花顺%d.json' % today_date, typ='dict')
    new_dict = reverse_dict(dic)
    np.save(output_path + '概念板块同花顺_reverse.npy', new_dict)
    print('已保存好至%s' % (output_path + '概念板块同花顺_reverse.npy'))

    fd = FactorData()
    short_name = fd.get_factor_value('Basic_factor', mddate=[str(today_date)], factor_names=['short_name'])
    short_name = short_name.to_dict()['short_name']

    # 开始生成单独的表格
    df = pd.Series(new_dict)
    df = df.to_frame()
    df = df.reset_index()
    df.columns = ['股票代码', '同花顺板块']

    def get_stock_name(x):
        return short_name[x] if x in short_name.keys() else np.nan

    df['股票名称'] = df['股票代码'].apply(lambda x: get_stock_name(x))
    df.columns = ['股票代码', '同花顺板块', '股票名称']
    FileUtil.save_df2xls(df, output_path, '概念板块同花顺_reverse.xlsx')
    send_message('%d概念板块同花顺字典已转置完成' % today_date)