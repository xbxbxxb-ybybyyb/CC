# @Time : 2020/6/23 15:23
# @Author : Zhichen Lu
# @File : Intraday_stat.py

import time
from multiprocessing import Pool

import pandas as pd


# temp_record = record[key_list[1]]
def get_pitches(temp_record, key, col_name='price'):
    e = time.time()
    if len(temp_record) == 0:
        return 0, pd.DataFrame()
    if not isinstance(temp_record, pd.DataFrame):
        return 0, pd.DataFrame()
    vol_total = temp_record['vol'].sum()
    if vol_total == 0:
        return pd.DataFrame()
    if vol_total > 0:
        sign = 1
    elif vol_total < 0:
        sign = -1
    temp_record = temp_record[temp_record['vol'] != 0]
    temp_record = temp_record[temp_record['vol'].notnull()]
    temp_record['bias_deal_to_signal'] = temp_record[col_name] / temp_record['signal_base_price'] - 1
    temp_record['bias_future_to_deal'] = temp_record['signal_future_price'] / temp_record[col_name] - 1
    temp_record['bias_future_to_signal'] = temp_record['signal_future_price'] / temp_record['signal_base_price'] - 1
    temp_record['correct_predict'] = temp_record['bias_future_to_signal'] * sign > 0
    # temp_record = temp_record[['bias_deal_to_signal', 'bias_future_to_deal', 'bias_future_to_signal', 'correct_predict']]
    # temp_record['sign'] = sign
    print(key, 'done', temp_record.shape, time.time() - e)
    return sign, temp_record


# out_path = '/data/group/800319/junkData/IntraFactorModel/junkClassification/temp_variable_stat/'
# flag = '_201801'
# record = pd.read_pickle(out_path+'record_lr_rise_down_zero_5min_2018_all_factor_fillnapad_new_portfolio_20200629.pkl')
# record = pd.read_pickle('/data/group/800319/junkData/IntraFactorModel/junkClassification/temp_variable/record_lr_rise_down_zero_5min_from2017_all_factor_fillnapad_20200615.pkl')

# out_path = '/data/group/800319/junkData/IntraFactorModel/junkClassification/temp_variable_mocker/'
# flag = '_new_portfolio_'
# record = pd.read_pickle(out_path+'record_lr_rise_down_zero_5min_2018_all_factor_fillnapad%s_20200630.pkl'%flag)

def get_result(out_path='/data/group/800319/junkData/IntraFactorModel/junkClassification/temp_variable_mocker/',
               tail='lr_rise_down_zero_5min_2018_all_factor_fillnapad_new_portfolio_5m_all_mkt__20200701.pkl'):
    record = pd.read_pickle(out_path + 'record_%s' % tail)
    key_list = list(filter(lambda x: isinstance(record[x], pd.DataFrame), list(record.keys())))

    pool = Pool(20)
    result_list = {}
    for k in key_list:
        # if not k[1].startswith('201801'):
        #     continue
        res = pool.apply_async(get_pitches, (*(record[k], k, 'deal_price'),))
        result_list[k] = res
    pool.close()
    pool.join()

    stat = {1: [], -1: []}
    for each in result_list:
        try:
            sign, temp_record = result_list[each].get()
        except:
            print(each, 'Wrong')
            continue
        if sign == 0:
            continue
        stat[sign].append(temp_record)

    stat[1] = pd.concat(stat[1])
    stat[-1] = pd.concat(stat[-1])

    pos, neg = stat[1].dropna(), stat[-1].dropna()

    col_list = ['bias_deal_to_signal', 'bias_future_to_deal', 'bias_future_to_signal', 'correct_predict']
    correct = pd.DataFrame({'pos': pos[pos['correct_predict']].mean(), 'neg': neg[neg['correct_predict']].mean()})
    incorrect = pd.DataFrame({'pos': pos[~pos['correct_predict']].mean(), 'neg': neg[~neg['correct_predict']].mean()})
    all_ = pd.DataFrame({'pos': pos.mean(), 'neg': neg.mean()})

    win_loss_ratio = correct.loc[col_list[:-1]] / incorrect.loc[col_list[:-1]]
    win_loss_ratio['tag'] = '盈亏比'
    all_['tag'] = '全部信号'
    correct['tag'] = '正确预测'
    incorrect['tag'] = '错误预测'

    result = pd.concat(
        [correct.loc[col_list[:-1]].reset_index(), incorrect.loc[col_list[:-1]].reset_index(), win_loss_ratio.reset_index(), all_.loc[col_list].reset_index()]).set_index(
        ['tag', 'index'])
    outperformance_all = pd.read_pickle(out_path + 'improve_%s' % tail)
    fulfill_percent, outperformance = pd.read_pickle(out_path + 'backtest_performance_%s' % tail)
    result['累计增厚'] = outperformance_all.cumsum().tolist()[-1]
    result['日均增厚'] = outperformance_all.mean()
    result['完成率'] = fulfill_percent['all'].mean()
    return result


# 'lr_全市场累积成交量':('/data/group/800319/junkData/IntraFactorModel/junkClassification/temp_variable_mocker/',
#                                 'lr_rise_down_zero_5min_2018_all_factor_fillnapad_new_portfolio_5m_all_mkt__20200701.pkl'),
#              'lr_全市场不累积成交量':('/data/group/800319/junkData/IntraFactorModel/junkClassification/temp_variable_mocker/',
#                                 'lr_rise_down_zero_5min_2018_all_factor_fillnapad_new_portfolio_nocumsignal__20200701.pkl'),
#              'mlp_全市场累积成交量':('/data/group/800319/junkData/IntraFactorModel/junkClassification/temp_variable_mocker/',
#                                     'lr_rise_down_zero_5min_2018_all_factor_fillnapad_new_portfolio_5m_all_mkt_mlp__20200701.pkl'),
#              'mlp_全市场不累积成交量': ('/data/group/800319/junkData/IntraFactorModel/junkClassification/temp_variable_mocker/',
#                               'lr_rise_down_zero_5min_2018_all_factor_fillnapad_new_portfolio_nocumsignal_5m_all_mkt_mlp__20200701.pkl')
para_dict = {'xgb_全市场累积成交量': ('/data/group/800319/junkData/IntraFactorModel/junkClassification/temp_variable_mocker/',
                              'rise_down_zero_5min_2018_all_factor_fillnapad_new_portfolio_5m_all_mkt_xgb__20200701.pkl'),
             'xgb_全市场不累积成交量': ('/data/group/800319/junkData/IntraFactorModel/junkClassification/temp_variable_mocker/',
                               'rise_down_zero_5min_2018_all_factor_fillnapad_new_portfolio_nocumsignal_5m_all_mkt_xgb__20200701.pkl')
             }

for res_name in para_dict:
    result = get_result(*para_dict[res_name])
    result.to_excel('/data/user/015664/日内结果/%s.xlsx' % res_name)

# result.to_excel('/data/user/015664/日内结果/成交假设0.5回测信号.xlsx')
# pos[pos['correct_predict']].mean()
# pos.mean()
# pos[~pos['correct_predict']].mean()
# neg[neg['correct_predict']].mean()#/neg[~neg['correct_predict']].mean()
# neg.mean()
# pos.mean()
# pd.to_pickle(stat, out_path+'/stat_lr_rise_down_zero_5min%s_all_factor_fillnapad_20200629.pkl'%flag)
#
# stat = pd.read_pickle(out_path+'/stat_lr_rise_down_zero_5min%s_all_factor_fillnapad_20200629.pkl'%flag)
#

# pd.read_pickle(out_path + 'backtest_performance_lr_rise_down_zero_5min_2018_all_factor_fillnapad%s_20200701.pkl'%flag)
#


"""
import os
ret = os.sep.join(__file__.split('/')[:-2])
name = os.path.basename(ret)
sum = 0
def func(dirpath):
    lst = os.listdir(dirpath)  # 大文件夹下文件列表,包括文件夹
    for el in lst:
        new_dir = dirpath+'/'+el
        if os.path.isfile(new_dir):
            getsize = os.path.getsize(new_dir)
            global sum
            sum += getsize
        else:
            func(new_dir)
    return sum

num = func( '/data/group/800319/junkData/IntraFactorModel/')
print('文件夹%s的大小为%s字节' % (name,num))
"""
