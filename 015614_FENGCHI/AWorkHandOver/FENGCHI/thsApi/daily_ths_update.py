import pandas as pd
import numpy as np
import datetime as dt
from dataApi import stockList
from xquant.factordata import FactorData

output_path = '/data/group/800442/800319/Afengchi/同花顺概念/'
new_ths_path = '/data/group/800442/800319/Afengchi/概念板块同花顺/'


def get_today_date():
    return int(dt.datetime.today().strftime('%Y%m%d'))


class MyUtil:
    def __init__(self):
        stock_name_dict = self.get_stock_name_dict()

        self.stock_name_dict = stock_name_dict

    def get_tip_str(self, stk: list or int):
        if type(stk) == int:
            wincode = stockList.trans_int2windcode(stk)
            ret = wincode + ',' + self.stock_name_dict[wincode]
            return ret
        elif type(stk) == str:
            ret = stk + ',' + self.stock_name_dict[stk]
            return ret
        elif type(stk) == list:
            ret = list()
            for s in stk:
                wincode = stockList.trans_int2windcode(s)
                ret.append(wincode + ',' + self.stock_name_dict[wincode])
            ret = '；'.join(ret)
            return ret

    @staticmethod
    def get_stock_name_dict():
        today_date = get_today_date()
        fd = FactorData()
        df = fd.get_factor_value('Basic_factor', mddate=['%s' % today_date], factor_names=['short_name'])
        stock_name_dict = df['short_name'].to_dict()
        return stock_name_dict

    def get_1stock_name(self, stk_code):
        if type(stk_code) == int:
            stk_code = stockList.trans_int2windcode(stk_code)
        try:
            return self.stock_name_dict[stk_code]
        except:
            return stk_code


MyUtil = MyUtil()


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
    today_date = get_today_date()
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
