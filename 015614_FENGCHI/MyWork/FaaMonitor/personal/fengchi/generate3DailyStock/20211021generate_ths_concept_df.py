# coding: utf-8
# Author：fengchi863
# Date ：2021/10/21 15:59

import os, sys
sys.path.append('/data/user/015614/MyWork')
sys.path.append('/data/user/015614/MyWork/ShortTermTrading')
sys.path.append('/data/user/015614/MyWork/FaaMonitor')

import pandas as pd, numpy as np
from FaaMonitor.Util.DtUtil import DtUtil
from FaaMonitor.Util.MyUtil import MyUtil
from FaaMonitor.conf.path_conf import new_ths_path, ths_concept_rank_path

output_path = '/data/group/800442/800319/Afengchi/同花顺概念/'


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
    today_date = DtUtil.get_today_date()
    dic = pd.read_json(new_ths_path + '概念板块同花顺%d.json' % today_date, typ='dict')
    new_dict = reverse_dict(dic)
    np.save(output_path + '概念板块同花顺_reverse.npy', new_dict)
    print('已保存好至%s' % (output_path + '概念板块同花顺_reverse.npy'))

    # 开始生成单独的表格
    df = pd.Series(new_dict)
    df = df.to_frame()
    df = df.reset_index()
    df.columns = ['股票代码', '同花顺板块']
    df['股票名称'] = df['股票代码'].apply(lambda x: MyUtil.get_1stock_name(x))
    df.columns = ['股票代码', '同花顺板块', '股票名称']
    df.to_excel(output_path + '概念板块同花顺_reverse.xlsx')
    print('已保存好至%s' % (output_path + '概念板块同花顺_reverse.xlsx'))