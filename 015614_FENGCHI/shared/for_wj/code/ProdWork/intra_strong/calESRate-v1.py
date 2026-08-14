# 使用实际的量计算实际买入的股票的模拟第一版收益
import pandas as pd
import numpy as np
from xquant.factordata import FactorData
s = FactorData()
from ProdWork.intra_strong.func_Basic_zt import cal_Basic_zt
from LucienUtil import IO
from xquant.marketdata import MarketData
import datetime as dt
mdp = MarketData()
from ProdWork.Param_config_data import thred_dict_jup_v9 as thred_dict
from ProdWork.CommonTools import excel_saver, ftp_download,ftp_upload,cal_ul_price
import sys

if len(sys.argv) > 1:
    date = sys.argv[1]
else:
    date = s.tradingday(dt.datetime.now().strftime('%Y%m%d'),-1)[0] # 判断当前的日期
    # date = '20230606'# # 若未在当个交易日晚上运行程序，需要在次日早上修改date
print('current date = %s'%date)


## Adate = '2021-04-02'
## lastdate = '20210401'
## Alastdate = '2021-04-01'
Adate = date[0:4]+'-'+date[4:6]+'-'+date[6:8]
lastdate = s.tradingday(date, -2)[0]
print('当前交易日date = %s，前一交易日lastdate = %s'%(date,lastdate))
Alastdate = lastdate[0:4]+'-'+lastdate[4:6]+'-'+lastdate[6:8]
IO_mother_dir = '/data/group/800080/warehouse_event'
MD_data_prod_dir = IO_mother_dir + '/prod/LOCAL_DATA/FLAG/%s/' % date # 大概每日5点20好
import time
import os
while (os.path.exists(MD_data_prod_dir + '%s_MD.success' % date) == False):
    print('等待MD或RDF或RISK或5分钟数据中')
    time.sleep(60)
# ----------------------------更新日内强势股触发文件，添加形态和o2ul信息-------------------------------

def view_bar(num,tot,s):
    rate = (num+1)/(tot)
    rate_num = (int(rate*100))
    n = rate_num//3
    r = '\r[%s>%s]%d%%-%s' % ('='*n,'-'*(33-n), rate_num, s)
    sys.stdout.write(r)
    sys.stdout.flush()
    if rate == 1:
        print('\n')

need_columns = ['dt', 'Ticker', 'ZT_Time', '买入时形态', 'TN_o2ul', 'shouldBuySignal']
if lastdate < '20200706':
    model_columns = ['HighHBXgbModel_local_prob', 'HighPct5XgbClaModel_local_prob', 'HighPct5XgbModel_local_prob',
                 'LowHBXgbModel_local_prob', 'LowPct5XgbClaModel_local_prob', 'LowPct5XgbModel_local_prob',
                 'TotalDjClaModel_local_prob', 'TotalLgbClaModel_local_prob', 'TotalLrModel_local_prob',
                 'TotalXgbModel_local_prob']
if lastdate >= '20200706': # 增加前日涨停模型
    model_columns = ['HighHBXgbModel_local_prob', 'HighPct5XgbClaModel_local_prob', 'HighPct5XgbModel_local_prob',
                 'LowHBXgbModel_local_prob', 'LowPct5XgbClaModel_local_prob', 'LowPct5XgbModel_local_prob',
                 'TotalDjClaModel_local_prob', 'TotalLgbClaModel_local_prob', 'TotalLrModel_local_prob',
                 'TotalXgbModel_local_prob', 'ZTXgbModel_local_prob','ZTBysModel_local_prob']
if lastdate >= '20200821': # 增加王敬的分类模型
    model_columns = ['TotalDjRegModel_local_prob','TotalXgbRegWjModel_local_prob','HighPct5XgbModel_local_prob','HighHBXgbModel_local_prob',
                     'TotalXgbModel_local_prob','TotalLrModel_local_prob','LowHBXgbModel_local_prob','LowPct5XgbModel_local_prob',
                     'ZTBysModel_local_prob','TotalDjClaModel_local_prob','TotalLgbClaWjModel_local_prob','HighPct5XgbClaModel_local_prob',
                     'LowPct5XgbClaModel_local_prob']
if lastdate >= '20201117': # 增加董坚的前日涨停模型
    model_columns = ['TotalDjRegModel_local_prob','TotalXgbRegWjModel_local_prob','HighPct5XgbModel_local_prob','HighHBXgbModel_local_prob',
                     'TotalXgbModel_local_prob','TotalLrModel_local_prob','LowHBXgbModel_local_prob','LowPct5XgbModel_local_prob',
                     'ZTBysModel_local_prob','TotalDjClaModel_local_prob','TotalLgbClaWjModel_local_prob','HighPct5XgbClaModel_local_prob',
                     'LowPct5XgbClaModel_local_prob','ZTDjRegModel_local_prob']
if lastdate >= '20201218': # 模型大版本迭代，在后面加上老模型
    model_columns = ['TotalLgbClaWjModel_local_prob','HighPct5XgbClaModel_local_prob','LowPct5XgbClaModel_local_prob',
                     'TotalDjClaModel_local_prob','TotalDjRegModel_local_prob','TotalLrModel_local_prob','TotalXgbModel_local_prob',
                     'manual_model_result_hml_reg_except_v1_v10_local_prob','manual_model_result_hml_reg_high_v1_v10_local_prob',
                     'manual_model_result_hml_reg_low_v1_v10_local_prob','RollType0lgbClaModel_local_prob','RollType1lgbClaModel_local_prob',
                     'RollType2lgbClaModel_local_prob','TotalLrClaWjModel_local_prob','Type0XgbModel_local_prob','Type1XgbModel_local_prob',
                     'Type2XgbModel_local_prob','ZTBysModel_local_prob','ZTDjRegModel_local_prob']
    model_columns  = model_columns + ['HighPct5XgbModel_local_prob','LowPct5XgbModel_local_prob','HighHBXgbModel_local_prob','LowHBXgbModel_local_prob',
                                      'TotalXgbRegWjModel_local_prob']
if lastdate >= '20210222': # 增加董坚新的前日涨停模型
    model_columns = ['TotalLgbClaWjModel_local_prob','HighPct5XgbClaModel_local_prob','LowPct5XgbClaModel_local_prob',
                     'TotalDjClaModel_local_prob','TotalDjRegModel_local_prob','TotalLrModel_local_prob','TotalXgbModel_local_prob',
                     'manual_model_result_hml_reg_except_v1_v10_local_prob','manual_model_result_hml_reg_high_v1_v10_local_prob',
                     'manual_model_result_hml_reg_low_v1_v10_local_prob','RollType0lgbClaModel_local_prob','RollType1lgbClaModel_local_prob',
                     'RollType2lgbClaModel_local_prob','TotalLrClaWjModel_local_prob','Type0XgbModel_local_prob','Type1XgbModel_local_prob',
                     'Type2XgbModel_local_prob','ZTBysModel_local_prob','ZTDjRegModel_local_prob','ZTDjClaModel_local_prob']
    model_columns  = model_columns + ['HighPct5XgbModel_local_prob','LowPct5XgbModel_local_prob','HighHBXgbModel_local_prob','LowHBXgbModel_local_prob',
                                      'TotalXgbRegWjModel_local_prob']
if lastdate >='20210825':
    model_columns = ['Hml0DjModel',
                  'Hml1DjModel',
                  'Hml2DjModel',
                  'Hml0PMMLModel',
                  'Hml1PMMLModel',
                  'Hml2PMMLModel',
                  'RisePctHighDjModel',
                  'RisePctLowDjModel',
                  'RollLgbClaModel',
                  'TotalDjClaModel',
                  'TotalDjRegModel',
                  'Type0lgbClaModel',
                  'Type1lgbClaModel',
                  'Type2lgbClaModel',
                  'Type0lrClaModel',
                  'Type1lrClaModel',
                  'Type2lrClaModel',
                  'Type0PMMLModel',
                  'Type1PMMLModel',
                  'Type2PMMLModel',
                  'Type0XgbModel',
                  'Type1XgbModel',
                  'Type2XgbModel',
                  'ZTBysModel',
                  'ZTDjRegModel',
                  'ZTDjClaModel']
    model_columns = [x+'_local_prob' for x in model_columns]
    model_columns = list(set(model_columns +['HighPct5XgbModel_local_prob','LowPct5XgbModel_local_prob','HighHBXgbModel_local_prob','LowHBXgbModel_local_prob',
                                      'TotalXgbRegWjModel_local_prob']))
if lastdate >= '20220222':
    model_columns = ['Hml0DjModel',
                     'Hml1DjModel',
                     'Hml2DjModel',
                     'Hml0XgbModel',
                     'Hml1XgbModel',
                     'Hml2XgbModel',
                     'RisePctHighDjModel',
                     'RisePctLowDjModel',
                     'Hml0XgbWjModel',
                     'Hml1XgbWjModel',
                     'Hml2XgbWjModel',
                     'TotalDjModel',
                     'TotalXgbModel',
                     'TotalXgbWjModel',
                     'Type0PMMLModel',
                     'Type1PMMLModel',
                     'Type2PMMLModel',
                     'Type0XgbWjModel',
                     'Type1XgbWjModel',
                     'Type2XgbWjModel',
                     'ZTBysModel',
                     'ZTDjRegModel',
                     'ZTDjClaModel']
    model_columns = [x + '_local_prob' for x in model_columns]
    model_columns = list(set(
        model_columns + ['HighHBXgbModel_local_prob',
 'HighPct5XgbModel_local_prob',
 'Hml0PMMLModel_local_prob',
 'Hml1PMMLModel_local_prob',
 'Hml2PMMLModel_local_prob',
 'LowHBXgbModel_local_prob',
 'LowPct5XgbModel_local_prob',
 'RollLgbClaModel_local_prob',
 'TotalDjClaModel_local_prob',
 'TotalDjRegModel_local_prob',
 'TotalXgbRegWjModel_local_prob',
 'Type0PMMLModel_local_prob',
 'Type0XgbModel_local_prob',
 'Type0lgbClaModel_local_prob',
 'Type0lrClaModel_local_prob',
 'Type1XgbModel_local_prob',
 'Type1lgbClaModel_local_prob',
 'Type1lrClaModel_local_prob',
 'Type2XgbModel_local_prob',
 'Type2lgbClaModel_local_prob',
 'Type2lrClaModel_local_prob']))
if lastdate >= '20230213':
    model_columns = list(thred_dict.keys())
    last_model_columns = ['Hml0DjModel',
                     'Hml1DjModel',
                     'Hml2DjModel',
                     'Hml0XgbModel',
                     'Hml1XgbModel',
                     'Hml2XgbModel',
                     'RisePctHighDjModel',
                     'RisePctLowDjModel',
                     'Hml0XgbWjModel',
                     'Hml1XgbWjModel',
                     'Hml2XgbWjModel',
                     'TotalDjModel',
                     'TotalXgbModel',
                     'TotalXgbWjModel',
                     'Type0PMMLModel',
                     'Type1PMMLModel',
                     'Type2PMMLModel',
                     'Type0XgbWjModel',
                     'Type1XgbWjModel',
                     'Type2XgbWjModel',
                     'ZTBysModel',
                     'ZTDjRegModel',
                     'ZTDjClaModel']
    model_columns = [x + '_local_prob' for x in model_columns]
    last_model_columns = [x + '_local_prob' for x in last_model_columns]
    model_columns = list(set(
        model_columns + ['HighHBXgbModel_local_prob',
 'HighPct5XgbModel_local_prob',
 'Hml0PMMLModel_local_prob',
 'Hml1PMMLModel_local_prob',
 'Hml2PMMLModel_local_prob',
 'LowHBXgbModel_local_prob',
 'LowPct5XgbModel_local_prob',
 'RollLgbClaModel_local_prob',
 'TotalDjClaModel_local_prob',
 'TotalDjRegModel_local_prob',
 'TotalXgbRegWjModel_local_prob',
 'Type0PMMLModel_local_prob',
 'Type0XgbModel_local_prob',
 'Type0lgbClaModel_local_prob',
 'Type0lrClaModel_local_prob',
 'Type1XgbModel_local_prob',
 'Type1lgbClaModel_local_prob',
 'Type1lrClaModel_local_prob',
 'Type2XgbModel_local_prob',
 'Type2lgbClaModel_local_prob',
 'Type2lrClaModel_local_prob']+last_model_columns))
# 获取昨天的标签汇总、今天的因子耗时和模型差异
Labels_prod_summary_old = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/实盘触发标签汇总_%s.xlsx'%Alastdate)
print(Labels_prod_summary_old.columns.tolist())

print(Labels_prod_summary_old.columns.tolist())
if Alastdate >= '2020-08-21': # 修改名字，使得回滚数据时在这一天不会出错
    Labels_prod_summary_old = Labels_prod_summary_old.rename(columns = {'TotalLgbClaModel_local_prob':'TotalLgbClaWjModel_local_prob'})
if Alastdate >= '2021-08-25': # 修改名字，使得回滚数据时在这一天不会出错
    Labels_prod_summary_old = Labels_prod_summary_old.rename(columns = {'manual_model_result_hml_reg_except_v1_v10_local_prob':'Hml1DjModel_local_prob','manual_model_result_hml_reg_low_v1_v10_local_prob':'Hml0DjModel_local_prob',\
                                                                        'manual_model_result_hml_reg_high_v1_v10_local_prob':'Hml2DjModel_local_prob'})
if Alastdate >= '2022-02-22':
    #Labels_prod_summary_old = Labels_prod_summary_old.rename(columns={'TotalDjRegModel_local_prob': 'TotalDjModel_local_prob'})
    Labels_prod_summary_old.drop(columns=['TotalDjRegModel_local_prob'],inplace=True)
model_columns = list(set(model_columns + Labels_prod_summary_old.filter(regex='_local_prob').columns.tolist()))
print(model_columns)
raw_last_date_factor_time_cost = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/因子耗时_%s_prod.xlsx'%Alastdate)
raw_last_date_factor_time_cost = raw_last_date_factor_time_cost[~raw_last_date_factor_time_cost['Unnamed: 0'].duplicated()]
dropindex_path = '/data/group/800463/xiely/save-file/for_wj/daily_mock_stockList/daily_mock_sp_%s.xlsx'%lastdate
dropindex_df = pd.read_excel(dropindex_path).set_index(['Unnamed: 0'])
dropindex = dropindex_df[0].tolist()
raw_last_date_factor_time_cost.set_index(['Unnamed: 0'], inplace=True)
raw_last_date_factor_time_cost = raw_last_date_factor_time_cost.loc[list(set(raw_last_date_factor_time_cost.index.tolist())-set(dropindex))].sort_index().reset_index()

raw_last_date_model_compare = pd.read_excel('/data/group/800463/日内强势股/log_parse/模型差异/%s/模型差异_%s_prod.xlsx' % (lastdate, lastdate)
                                            , sheet_name='本地投票结果').rename(columns = {'Ticker':'Unnamed: 0'})
# 获取模型的预测结果
# 如果昨天有模型没有给出预测（比如没有前日涨停样本、或者没有前高样本等分场景），则在模型差异中的投票结果中新建一个空的列
for model_name in model_columns:
    if model_name not in raw_last_date_model_compare.columns:
        raw_last_date_model_compare[model_name] = np.nan
raw_last_date_model_compare = raw_last_date_model_compare[['Unnamed: 0'] + model_columns].rename(columns={'Unnamed: 0': 'Ticker'})*1
raw_last_date_model_compare['dt'] = pd.Timestamp(Alastdate)
# 计算买入时形态
for index,row in raw_last_date_factor_time_cost.iterrows():
    stock_code,pre_date = row['Unnamed: 0'],lastdate
    # view_bar(int(index), len(raw_last_date_factor_time_cost), stock_code + pre_date)
    pre_close, close,ul_price = IO.read_data([pre_date, pre_date], columns=['pre_close', 'close','high']
            ,alt=IO_mother_dir+'/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5').loc[pre_date, stock_code].values
    #ul_price = cal_ul_price(IO.read_data([pre_date, pre_date], columns=['pre_close', 'close','high'],alt=IO_mother_dir+'/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')).loc[pre_date, stock_code].values
    raw_last_date_factor_time_cost.loc[index,'买入时形态'] = cal_Basic_zt(mdp, stock_code, pre_date, pre_close, close)['label_pattern'].values[0]
# 将耗时、模型预测拼入标签汇总
raw_last_date_factor_time_cost['dt'] = pd.Timestamp(lastdate)
raw_last_date_factor_time_cost['TN_o2ul'] = np.nan
raw_last_date_factor_time_cost = raw_last_date_factor_time_cost.rename(columns = {'Unnamed: 0':'Ticker'})
Labels_prod_summary_new = pd.concat([Labels_prod_summary_old,
                         raw_last_date_factor_time_cost.set_index(['dt', 'Ticker']).join(
                         raw_last_date_model_compare.set_index(['dt', 'Ticker'])).reset_index()[need_columns + model_columns]]) \
        .reset_index()[need_columns + model_columns + ['ZTXgbModel_local_prob'] + ['old_finish_indicator' ,'old_pct','new_finish_indicator','new_pct','new_absolute_profit']]
# 对于o2ul还未算出的样本进行计算
o2ul_nan_samples = Labels_prod_summary_new[Labels_prod_summary_new['TN_o2ul'].isnull()]
date_ini = o2ul_nan_samples['dt'].apply(lambda x:x.strftime('%Y%m%d')).min()
end_date = o2ul_nan_samples['dt'].apply(lambda x:x.strftime('%Y%m%d')).max()
end_date_ = int(s.tradingday(end_date, 30)[-1])
md_data = IO.read_data([20200317, end_date_], columns=['pre_close', 'open', 'high', 'low','close','vwap', 'adjfactor'],
                            alt=IO_mother_dir+'/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
md_data['ul_price'] = np.floor(md_data['pre_close'] * 100 * 1.1 + 0.5) / 100
md_data['new_300'] = (md_data.reset_index()['Ticker'].apply(lambda x:x[0]=='3') & (md_data.reset_index()['dt']>='20200824')).values
md_data.loc[md_data['new_300'],'ul_price'] = np.floor(md_data.loc[md_data['new_300'],'pre_close'] * 100 * 1.2 + 0.5) / 100
md_data['next_ul_price'] = np.floor(md_data['close'] * 100 * 1.1 + 0.5) / 100
md_data.loc[md_data['new_300'],'next_ul_price'] = np.floor(md_data.loc[md_data['new_300'],'close'] * 100 * 1.2 + 0.5) / 100
md_data['label_T_zt'] = (md_data['close'] == md_data['ul_price']).astype(int)
md_data['raw_close'] = md_data['close']

md_data['open'], md_data['close'] = md_data['open'] * md_data['adjfactor'], md_data['close'] * md_data['adjfactor']
md_data['vwap'], md_data['pre_close'] = md_data['vwap'] * md_data['adjfactor'], md_data['pre_close'] * md_data['adjfactor']
md_data['high'], md_data['low'] = md_data['high'] * md_data['adjfactor'], md_data['low'] * md_data['adjfactor']
md_data['ul_price'] = md_data['ul_price'] * md_data['adjfactor']
md_data['label_T_o2ul'] = md_data['open'].unstack().shift(-1).stack() / md_data['ul_price'] - 1
md_data.loc[md_data['high'] == md_data['low'], 'open'] = np.nan
md_data.loc[md_data['high'] == md_data['low'], 'vwap'] = np.nan
md_data['next_open'] = md_data['open'].unstack().shift(-1).stack()
md_data['next_close'] = md_data['close'].unstack().shift(-1).stack()
md_data['next_vwap'] = md_data['vwap'].unstack().shift(-1).stack()
md_data['next_raw_close'] = md_data['raw_close'].unstack().shift(-1).stack()
md_data['next_open'] = md_data['next_open'].unstack().fillna(method='bfill', axis=0).stack()
md_data['next_close'] = md_data['next_close'].unstack().fillna(method='bfill', axis=0).stack()
md_data['next_raw_close'] = md_data['next_raw_close'].unstack().fillna(method='bfill', axis=0).stack()
md_data['next_vwap'] = md_data['next_vwap'].unstack().fillna(method='bfill', axis=0).stack()
#md_data['next_ul'] = md_data['next_ul'].unstack().fillna(method='bfill', axis=0).stack()
md_data['label_TN_o2ul'] = md_data['next_open'] / md_data['ul_price'] - 1
md_data['label_Tc2Tul'] = md_data['close']/ md_data['ul_price'] - 1
md_data['label_T1o2Tc'] = md_data['next_open']/ md_data['close'] - 1
md_data['label_T1c2Tc'] = md_data['next_close']/ md_data['close'] - 1
md_data['label_T1_zt'] = (md_data['next_raw_close'] == md_data['next_ul_price']).astype(int)
Labels_prod_summary_new.set_index(['dt','Ticker'], inplace=True)
Labels_prod_summary_new['label_Tc2Tul'] = md_data.loc[Labels_prod_summary_new.index,'label_Tc2Tul']
Labels_prod_summary_new['label_T1o2Tc'] = md_data.loc[Labels_prod_summary_new.index,'label_T1o2Tc']
Labels_prod_summary_new['label_T1c2Tc'] = md_data.loc[Labels_prod_summary_new.index,'label_T1c2Tc']
Labels_prod_summary_new['label_T1_zt'] = md_data.loc[Labels_prod_summary_new.index,'label_T1_zt']
Labels_prod_summary_new = Labels_prod_summary_new.reset_index()
Labels_prod_summary_new_copy = Labels_prod_summary_new.copy()
for i in o2ul_nan_samples.index:
    buy_date = Labels_prod_summary_new.loc[i]['dt']
    stock = Labels_prod_summary_new.loc[i]['Ticker']
    Labels_prod_summary_new.loc[i,'TN_o2ul'] = 100*md_data.reindex(Labels_prod_summary_new_copy.set_index(['dt','Ticker']).index)['label_TN_o2ul']\
                                                .loc[buy_date.strftime('%Y%m%d'),stock]

# ------------------------------------更新触发文件，计算模拟收益-------------------------------------------------
import os
import pickle
import datetime as dt
import sys
sys.path.append("../../")
sys.path.append("/../..")
from xquant.factordata import FactorData
from xquant.xqutils.xqfile import HDFSFile
s = FactorData()
hf = HDFSFile()
import ProdWork.intra_strong.factor_LabelProfit_zt_r as fLPzt
import ProdWork.intra_strong.factor_LabelProfit_zt_n as fLPztn
from ProdWork.Param_config_data import param
if __name__ == "__main__":
    #param = {'sell_vol_pct': 0.2, 'max_amt': 800 * 10000, 'lag_ms_SH': 900, 'lag_ms_SZ': 400}
    # -----计算老卖出收益-----
    if 'old_finish_indicator' not in Labels_prod_summary_new.columns:
        Labels_prod_summary_new['old_finish_indicator'] = np.nan
    not_finished_old_holdings = Labels_prod_summary_new[(Labels_prod_summary_new['old_finish_indicator']!=1)&(Labels_prod_summary_new['dt']>='2020-05-22')]
    not_finished_old_holdings = not_finished_old_holdings[(not_finished_old_holdings['dt'] != pd.Timestamp('20200727')) &
                                                          (not_finished_old_holdings['Ticker'] != '000403.SZ')]
    old_pct_start_date,old_pct_end_date = not_finished_old_holdings['dt'].min(),not_finished_old_holdings['dt'].max()
    #start_date = s.tradingday(old_pct_end_date,-10)[0]
    #old_pct_start_date = start_date[:4]+'-'+start_date[4:6]+'-'+start_date[6:]
    print(old_pct_start_date,old_pct_end_date)
    old_pct_basic_file = pd.DataFrame()
    for dates in s.tradingday(old_pct_start_date.strftime('%Y%m%d'),old_pct_end_date.strftime('%Y%m%d')):
        '''if dates == '20200820':
            date_basic = pd.read_hdf('/data/user/013600/generalStrong_v2/daily_data/%s_bak/Basic_zt_%s_%s.h5' % (dates, dates, dates))
        elif dates < '20210825':
            date_basic = pd.read_hdf('/data/user/013600/generalStrong_v2/daily_data_300/%s/Basic_zt_%s_%s.h5'%(dates,dates,dates))
        else:
            date_basic = pd.read_hdf('/data/user/013600/generalStrong_v3/daily_data/%s/Basic_zt_%s_%s.h5' % (dates, dates, dates))'''
        date_basic = pd.read_hdf('/data/group/800463/project/project1_prod/generalStrong_v3/Basic_zt/Basic_zt.h5').loc[pd.Timestamp(dates):pd.Timestamp(dates)]
        if dates == '20200727': # 有个000403.SZ,头疼的样本
            special_not_finished_tickers = not_finished_old_holdings[not_finished_old_holdings['dt'] == dates]['Ticker']
            if len(special_not_finished_tickers) == 1:
                pass
            else:
                old_pct_basic_file = pd.concat([old_pct_basic_file,
                                                date_basic.loc[not_finished_old_holdings[not_finished_old_holdings['dt'] == dates].set_index(
                                                    ['dt', 'Ticker']).index]])
        else:
            old_pct_basic_file = pd.concat([old_pct_basic_file,
                            date_basic.loc[not_finished_old_holdings[not_finished_old_holdings['dt']==dates].set_index(['dt','Ticker']).index]])

    factor_df_old_pct = fLPzt.factor_LabelProfit_zt(param=param,basic_file=old_pct_basic_file)
    for index, row in not_finished_old_holdings.iterrows():
        buy_date = row['dt']
        stock = row['Ticker']
        if (buy_date.strftime('%Y%m%d') == '20200727') & (stock == '000403.SZ'):
            pass
        else:
            Labels_prod_summary_new.loc[index,'old_pct'],Labels_prod_summary_new.loc[index,'old_finish_indicator']= \
            factor_df_old_pct.loc[pd.Timestamp(buy_date),stock][['pct','finish_indicator']]

    # ----计算理论新卖出收益----
    if 'new_finish_indicator' not in Labels_prod_summary_new.columns:
        Labels_prod_summary_new['new_finish_indicator'] = np.nan
    not_new_finished_holdings = Labels_prod_summary_new[(Labels_prod_summary_new['new_finish_indicator']!=1)&(Labels_prod_summary_new['dt']>='2020-05-22')]
    not_new_finished_holdings = not_new_finished_holdings[(not_new_finished_holdings['dt'] != pd.Timestamp('20200727')) &
                                                          (not_new_finished_holdings['Ticker'] != '000403.SZ')]
    new_pct_start_date,new_pct_end_date = not_new_finished_holdings['dt'].min(),not_new_finished_holdings['dt'].max()
    new_pct_basic_file = pd.DataFrame()
    for dates in s.tradingday(new_pct_start_date.strftime('%Y%m%d'),new_pct_end_date.strftime('%Y%m%d')):
        if dates == '20200820':
            date_basic = pd.read_hdf('/data/group/800463/project/project1_prod/generalStrong_v2/daily_data/%s_bak/Basic_zt_%s_%s.h5' % (dates, dates, dates))
        elif date < '20210825':
            date_basic = pd.read_hdf('/data/group/800463/project/project1_prod/generalStrong_v2/daily_data_300/%s/Basic_zt_%s_%s.h5'%(dates,dates,dates))
        else:
            date_basic = pd.read_hdf('/data/group/800463/project/project1_prod/generalStrong_v3/daily_data/%s/Basic_zt_%s_%s.h5' % (dates, dates, dates))
        new_pct_basic_file = pd.concat([new_pct_basic_file,
                            date_basic.loc[not_new_finished_holdings[not_new_finished_holdings['dt']==dates].set_index(['dt','Ticker']).index]])
    factor_df_new_pct = fLPztn.factor_LabelProfit_zt(param=param,basic_file=new_pct_basic_file)
    factor_df_new_pct['absolute_profit'] = factor_df_new_pct['pct']*factor_df_new_pct['buy_amt']

    for index, row in not_new_finished_holdings.iterrows():
        buy_date = row['dt']
        stock = row['Ticker']
        if (buy_date.strftime('%Y%m%d') == '20200727') & (stock == '000403.SZ'):
            pass
        else:
            Labels_prod_summary_new.loc[index,'new_pct'],Labels_prod_summary_new.loc[index,'new_finish_indicator'],Labels_prod_summary_new.loc[index,'new_absolute_profit'] = \
            factor_df_new_pct.loc[pd.Timestamp(buy_date),stock][['pct','finish_indicator','absolute_profit']]
    dropcols = Labels_prod_summary_new.filter(regex='_prob.1').columns.tolist()
    print('dropcols:', dropcols)
    Labels_prod_summary_new.drop(columns=dropcols, inplace=True)
    Labels_prod_summary_new.to_excel('/data/group/800463/日内强势股/log_parse/因子耗时/实盘触发标签汇总_%s.xlsx'%Adate,index=False)
    print('create file %s!!!!!!!!!!'%'/data/group/800463/日内强势股/log_parse/因子耗时/实盘触发标签汇总_%s.xlsx'%Adate)
    # -----------------------------------------------标签汇总更新完毕---------------------------------------------------------
    '''Labels_prod_summary_new = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/实盘触发标签汇总_%s.xlsx'%Adate)
    # 20201125增加进行实盘和模拟总收益的对比图
    sellDf = pd.read_excel('/data/group/800463/日内强势股/实盘分析记录/日内强势股总卖出记录/日内强势股总卖出记录-%s.xlsx'%(date))
    sellDf_copy = sellDf.copy()
    sellDf_copy['买入日期'] = sellDf_copy['买入日期'].apply(lambda x:pd.Timestamp(x))
    sellDf_copy = sellDf_copy.rename(columns = {'证券代码':'Ticker',
                             '买入日期':'dt'}).set_index(['dt','Ticker'])
    sellDf_copy['模拟收益率'] = Labels_prod_summary_new.set_index(['dt','Ticker']).reindex(sellDf_copy.index)['new_pct']
    sellDf_copy['模拟收益'] = sellDf_copy['模拟收益率'] * sellDf_copy['买入金额']
    sellDf_copy = sellDf_copy.rename(columns = {'卖出部分盈利金额':'实际收益',
                                  '卖出部分收益率(%)':'实际收益率'})
    sellDf_copy['实际收益率'] = sellDf_copy['实际收益率']/100
    comparison_plot_data = sellDf_copy.loc['20200522':].groupby(['dt']).sum()[['模拟收益','实际收益','模拟收益率','实际收益率']].fillna(0).cumsum()
    # -----------------------------------------------计算各个模型的表现和实盘策略的表现---------------------------------------
    Labels_prod_summary_new = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/实盘触发标签汇总_%s.xlsx'%Adate)
    Labels_prod_summary_new_cal_raw = Labels_prod_summary_new[Labels_prod_summary_new['new_finish_indicator']==1]
    Labels_prod_summary_new_cal_raw['real_positive'] = (Labels_prod_summary_new_cal_raw['TN_o2ul']>0) & (Labels_prod_summary_new_cal_raw['买入时形态']==4)
    Labels_prod_summary_new_cal = Labels_prod_summary_new_cal_raw[Labels_prod_summary_new_cal_raw['ZTBysModel_local_prob'].isnull()]

    model_singular_columns = ['TotalDjClaModel_local_prob','TotalDjRegModel_local_prob', 'TotalLgbClaWjModel_local_prob', 'TotalXgbRegWjModel_local_prob',
                              'TotalLrModel_local_prob','TotalXgbModel_local_prob','HBXgbModel_local_prob','Pct5XgbClaModel_local_prob',
                              'Pct5XgbModel_local_prob','TotalLrClaWjModel_local_prob','HmlDjRegModel_local_prob','RollTypelgbClaModel_local_prob',
                              'TypeXgbModel_local_prob']
    model_dual_column_dict = {'HighHBXgbModel_local_prob':'LowHBXgbModel_local_prob',
                              'HighPct5XgbClaModel_local_prob':'LowPct5XgbClaModel_local_prob',
                              'HighPct5XgbModel_local_prob':'LowPct5XgbModel_local_prob'}

    all_model_return_rate = pd.DataFrame()
    all_model_return = pd.DataFrame()
    all_model_recall = pd.DataFrame()
    all_model_win = pd.DataFrame()

    def cal_return_rate(data,model_name):
        return pd.Series({model_name+'_daily_pct_sum': ((1+data['new_pct'])*0.998-1).sum()})
    def cal_return(data,model_name):
        buy_amt = data['new_absolute_profit']/data['new_pct']
        sell_amt = buy_amt*(1+data['new_pct'])*0.998
        return pd.Series({model_name+'_daily_profit_sum': (sell_amt-buy_amt).sum()})
    def cal_recall_win(data,model_name):
        data_need = data[data[model_name+'_local_prob'].notnull()]
        raw_stats = data_need.groupby(['dt']).apply(lambda x:pd.Series({'总正样本数量':x['real_positive'].sum(),
                         '预测正确正样本数量':(x['real_positive'] & (x[model_name+'_local_prob'] == 1)).sum(),
                         '预测正样本数量':x[model_name+'_local_prob'].sum()}))
        rolling_stats = raw_stats.rolling(20,10).sum()
        recall = pd.DataFrame(rolling_stats['预测正确正样本数量']/rolling_stats['总正样本数量'],columns = [model_name])
        win_rate = pd.DataFrame(rolling_stats['预测正确正样本数量']/rolling_stats['预测正样本数量'],columns = [model_name])
        return recall, win_rate


    Labels_prod_summary_new_cal['HmlDjRegModel_local_prob'] = (Labels_prod_summary_new_cal['Hml0DjModel_local_prob']==1)|\
                                                              (Labels_prod_summary_new_cal['Hml1DjModel_local_prob']==1)|\
                                                              (Labels_prod_summary_new_cal['Hml2DjModel_local_prob']==1)
    nanindex_HmlDjRegModel = Labels_prod_summary_new_cal[(Labels_prod_summary_new_cal['Hml0DjModel_local_prob'].isnull())&\
               (Labels_prod_summary_new_cal['Hml1DjModel_local_prob'].isnull())&\
               (Labels_prod_summary_new_cal['Hml2DjModel_local_prob'].isnull())].index
    Labels_prod_summary_new_cal.loc[nanindex_HmlDjRegModel,'HmlDjRegModel_local_prob'] = np.nan

    Labels_prod_summary_new_cal['RollTypelgbClaModel_local_prob'] =(Labels_prod_summary_new_cal['RollType0lgbClaModel_local_prob']==1)|\
                                                                   (Labels_prod_summary_new_cal['RollType1lgbClaModel_local_prob']==1)|\
                                                                   (Labels_prod_summary_new_cal['RollType2lgbClaModel_local_prob']==1)
    nanindex_HmlDjRegModel = Labels_prod_summary_new_cal[(Labels_prod_summary_new_cal['RollType0lgbClaModel_local_prob'].isnull())&\
               (Labels_prod_summary_new_cal['RollType1lgbClaModel_local_prob'].isnull())&\
               (Labels_prod_summary_new_cal['RollType2lgbClaModel_local_prob'].isnull())].index
    Labels_prod_summary_new_cal.loc[nanindex_HmlDjRegModel,'RollTypelgbClaModel_local_prob'] = np.nan

    Labels_prod_summary_new_cal['RollTypelrClaModel_local_prob'] = (Labels_prod_summary_new_cal[
                                                                         'Type0lrClaModel_local_prob'] == 1) | \
                                                                    (Labels_prod_summary_new_cal[
                                                                         'Type1lrClaModel_local_prob'] == 1) | \
                                                                    (Labels_prod_summary_new_cal[
                                                                         'Type2lrClaModel_local_prob'] == 1)
    nanindex_HmlDjRegModel = Labels_prod_summary_new_cal[
        (Labels_prod_summary_new_cal['Type0lrClaModel_local_prob'].isnull()) & \
        (Labels_prod_summary_new_cal['Type1lrClaModel_local_prob'].isnull()) & \
        (Labels_prod_summary_new_cal['Type2lrClaModel_local_prob'].isnull())].index
    Labels_prod_summary_new_cal.loc[nanindex_HmlDjRegModel, 'TypelrClaModel_local_prob'] = np.nan

    Labels_prod_summary_new_cal['TypeXgbModel_local_prob'] =(Labels_prod_summary_new_cal['Type0XgbModel_local_prob']==1)|\
                                                            (Labels_prod_summary_new_cal['Type1XgbModel_local_prob']==1)|\
                                                            (Labels_prod_summary_new_cal['Type2XgbModel_local_prob']==1)
    nanindex_HmlDjRegModel = Labels_prod_summary_new_cal[(Labels_prod_summary_new_cal['Type0XgbModel_local_prob'].isnull())&\
               (Labels_prod_summary_new_cal['Type1XgbModel_local_prob'].isnull())&\
               (Labels_prod_summary_new_cal['Type2XgbModel_local_prob'].isnull())].index
    Labels_prod_summary_new_cal.loc[nanindex_HmlDjRegModel,'TypeXgbModel_local_prob'] = np.nan

    for model_name,dual_model_name in model_dual_column_dict.items():
        model_real_name,dual_model_real_name = model_name[:~10],dual_model_name[:~10]
        Labels_prod_summary_new_cal[model_real_name[4:]+'_local_prob'] = Labels_prod_summary_new_cal[model_real_name + '_local_prob'].fillna(0) + Labels_prod_summary_new_cal[dual_model_real_name + '_local_prob'].fillna(0)
    for model_name in model_singular_columns:
        model_real_name = model_name[:~10]
        Labels_prod_summary_new_cal_model = Labels_prod_summary_new_cal[Labels_prod_summary_new_cal[model_real_name+'_local_prob']==1]
        single_model_performance_rate = Labels_prod_summary_new_cal_model.groupby(['dt']).apply(lambda x:cal_return_rate(x,model_real_name))
        single_model_performance_return = Labels_prod_summary_new_cal_model.groupby(['dt']).apply(lambda x:cal_return(x,model_real_name))
        all_model_return_rate = pd.concat([all_model_return_rate,single_model_performance_rate],axis = 1)
        all_model_return = pd.concat([all_model_return,single_model_performance_return],axis = 1)
        this_model_recall, this_model_win = cal_recall_win(Labels_prod_summary_new_cal, model_real_name)
        all_model_recall = pd.concat([all_model_recall,this_model_recall],axis = 1)
        all_model_win = pd.concat([all_model_win,this_model_win],axis = 1)
    prod_tot_signal = Labels_prod_summary_new_cal[Labels_prod_summary_new_cal['shouldBuySignal'] == True]
    prod_tot_return_rate = prod_tot_signal.groupby(['dt']).apply(lambda x:cal_return_rate(x,'shouldBuySignal'))
    prod_tot_return = prod_tot_signal.groupby(['dt']).apply(lambda x:cal_return(x,'shouldBuySignal'))
    all_model_return_rate = pd.concat([all_model_return_rate, prod_tot_return_rate], axis=1)
    all_model_return = pd.concat([all_model_return, prod_tot_return], axis=1)
    prod_model_raw_stats = Labels_prod_summary_new_cal.groupby(['dt']).apply(lambda x: pd.Series({'总正样本数量': x['real_positive'].sum(),
                                                                '预测正确正样本数量': (x['real_positive'] & (x['shouldBuySignal'] == 1)).sum(),
                                                                '预测正样本数量': x['shouldBuySignal'].sum()}))
    prod_model_rolling_stats = prod_model_raw_stats.rolling(20, 10).sum()
    prod_model_recall = pd.DataFrame(prod_model_rolling_stats['预测正确正样本数量'] / prod_model_rolling_stats['总正样本数量'], columns=['shouldBuySignal'])
    prod_model_win_rate = pd.DataFrame(prod_model_rolling_stats['预测正确正样本数量'] / prod_model_rolling_stats['预测正样本数量'], columns=['shouldBuySignal'])
    all_model_recall = pd.concat([all_model_recall, prod_model_recall], axis=1)
    all_model_win = pd.concat([all_model_win, prod_model_win_rate], axis=1)

    # -----------------------------------------------------20200706添加前日收盘涨停模型--------------------------------------
    if lastdate >= '20200706':
        Labels_prod_summary_new_cal_ZT = Labels_prod_summary_new_cal_raw[Labels_prod_summary_new_cal_raw['ZTBysModel_local_prob'].notnull()]
        ZT_model_singular_columns = ['ZTXgbModel_local_prob','ZTBysModel_local_prob','Pct5XgbClaModel_local_prob','ZTDjRegModel_local_prob','ZTDjClaModel_local_prob']
        ZT_model_dual_column_dict = {'HighPct5XgbClaModel_local_prob':'LowPct5XgbClaModel_local_prob'}
        ZT_model_return_rate = pd.DataFrame()
        ZT_model_return = pd.DataFrame()
        ZT_model_recall = pd.DataFrame()
        ZT_model_win = pd.DataFrame()
        def cal_return_rate(data, model_name):
            return pd.Series({model_name + '_daily_pct_sum': ((1 + data['new_pct']) * 0.998 - 1).sum()})
        def cal_return(data, model_name):
            buy_amt = data['new_absolute_profit'] / data['new_pct']
            sell_amt = buy_amt * (1 + data['new_pct']) * 0.998
            return pd.Series({model_name + '_daily_profit_sum': (sell_amt - buy_amt).sum()})
        def cal_recall_win(data,model_name):
            raw_stats = data.groupby(['dt']).apply(lambda x:pd.Series({'总正样本数量':x['real_positive'].sum(),
                             '预测正确正样本数量':(x['real_positive'] & (x[model_name+'_local_prob'] == 1)).sum(),
                             '预测正样本数量':x[model_name+'_local_prob'].sum()}))
            rolling_stats = raw_stats.rolling(20,10).sum()
            recall = pd.DataFrame(rolling_stats['预测正确正样本数量']/rolling_stats['总正样本数量'],columns = [model_name])
            win_rate = pd.DataFrame(rolling_stats['预测正确正样本数量']/rolling_stats['预测正样本数量'],columns = [model_name])
            return recall, win_rate
        for model_name, dual_model_name in ZT_model_dual_column_dict.items():
            model_real_name, dual_model_real_name = model_name[:~10], dual_model_name[:~10]
            Labels_prod_summary_new_cal_ZT[model_real_name[4:] + '_local_prob'] = Labels_prod_summary_new_cal_ZT[model_real_name + '_local_prob'].fillna(0) + \
                                                                               Labels_prod_summary_new_cal_ZT[dual_model_real_name + '_local_prob'].fillna(0)
        for model_name in ZT_model_singular_columns:
            model_real_name = model_name[:~10]
            Labels_prod_summary_new_cal_model = Labels_prod_summary_new_cal_ZT[Labels_prod_summary_new_cal_ZT[model_real_name+'_local_prob']==1]
            single_model_performance_rate = Labels_prod_summary_new_cal_model.groupby(['dt']).apply(lambda x:cal_return_rate(x,model_real_name))
            single_model_performance_return = Labels_prod_summary_new_cal_model.groupby(['dt']).apply(lambda x:cal_return(x,model_real_name))
            ZT_model_return_rate = pd.concat([ZT_model_return_rate,single_model_performance_rate],axis = 1)
            ZT_model_return = pd.concat([ZT_model_return,single_model_performance_return],axis = 1)
            this_model_recall, this_model_win = cal_recall_win(Labels_prod_summary_new_cal_ZT, model_real_name)
            ZT_model_recall = pd.concat([ZT_model_recall,this_model_recall],axis = 1)
            ZT_model_win = pd.concat([ZT_model_win,this_model_win],axis = 1)
        prod_ZT_signal = Labels_prod_summary_new_cal_ZT[Labels_prod_summary_new_cal_ZT['shouldBuySignal'] == True]
        prod_ZT_return_rate = prod_ZT_signal.groupby(['dt']).apply(lambda x:cal_return_rate(x,'shouldBuySignal'))
        prod_ZT_return = prod_ZT_signal.groupby(['dt']).apply(lambda x:cal_return(x,'shouldBuySignal'))
        ZT_model_return_rate = pd.concat([ZT_model_return_rate, prod_ZT_return_rate], axis=1)
        ZT_model_return = pd.concat([ZT_model_return, prod_ZT_return], axis=1)
        prod_ZT_model_raw_stats = Labels_prod_summary_new_cal_ZT.groupby(['dt']).apply(lambda x: pd.Series({'总正样本数量': x['real_positive'].sum(),
                                                                    '预测正确正样本数量': (x['real_positive'] & (x['shouldBuySignal'] == 1)).sum(),
                                                                    '预测正样本数量': x['shouldBuySignal'].sum()}))
        prod_ZT_model_rolling_stats = prod_ZT_model_raw_stats.rolling(20, 10).sum()
        prod_ZT_model_recall = pd.DataFrame(prod_ZT_model_rolling_stats['预测正确正样本数量'] / prod_ZT_model_rolling_stats['总正样本数量'], columns=['shouldBuySignal'])
        prod_ZT_model_win_rate = pd.DataFrame(prod_ZT_model_rolling_stats['预测正确正样本数量'] / prod_ZT_model_rolling_stats['预测正样本数量'], columns=['shouldBuySignal'])
        ZT_model_recall = pd.concat([ZT_model_recall, prod_ZT_model_recall], axis=1).fillna(0)
        # ZTXgbModel 20200820 卒；ZTDjRegModel 20201117 生
        ZT_model_recall.loc['20200821':,'ZTXgbModel'] = np.nan
        ZT_model_recall.loc[:'20201116','ZTDjRegModel'] = np.nan
        ZT_model_win = pd.concat([ZT_model_win, prod_ZT_model_win_rate], axis=1).fillna(0)
        ZT_model_win.loc['20200821':,'ZTXgbModel'] = np.nan
        ZT_model_win.loc[:'20201116','ZTDjRegModel'] = np.nan
        # --------------20200717新增原模型在涨停样本上的表现---------------------
        Labels_prod_summary_new_cal_origin_ZT = Labels_prod_summary_new_cal_raw[Labels_prod_summary_new_cal_raw['ZTXgbModel_local_prob'].notnull()]
        model_singular_columns = ['TotalDjClaModel_local_prob','TotalDjRegModel_local_prob', 'TotalLgbClaWjModel_local_prob',
                                  'TotalXgbRegWjModel_local_prob','TotalLrModel_local_prob', 'TotalXgbModel_local_prob'
                            , 'HBXgbModel_local_prob', 'Pct5XgbClaModel_local_prob', 'Pct5XgbModel_local_prob']
        model_dual_column_dict = {'HighHBXgbModel_local_prob': 'LowHBXgbModel_local_prob',
                                  'HighPct5XgbClaModel_local_prob': 'LowPct5XgbClaModel_local_prob',
                                  'HighPct5XgbModel_local_prob': 'LowPct5XgbModel_local_prob'}
        ZT_origin_model_return_rate = pd.DataFrame()
        ZT_origin_model_return = pd.DataFrame()
        ZT_origin_model_recall = pd.DataFrame()
        ZT_origin_model_win = pd.DataFrame()
        for model_name, dual_model_name in model_dual_column_dict.items():
            model_real_name, dual_model_real_name = model_name[:~10], dual_model_name[:~10]
            Labels_prod_summary_new_cal_origin_ZT[model_real_name[4:] + '_local_prob'] = Labels_prod_summary_new_cal_origin_ZT[model_real_name + '_local_prob'].fillna(0) + \
                                                                               Labels_prod_summary_new_cal_origin_ZT[dual_model_real_name + '_local_prob'].fillna(0)
        for model_name in model_singular_columns:
            model_real_name = model_name[:~10]
            Labels_prod_summary_new_cal_model = Labels_prod_summary_new_cal_origin_ZT[Labels_prod_summary_new_cal_origin_ZT[model_real_name+'_local_prob']==1]
            single_model_performance_rate = Labels_prod_summary_new_cal_model.groupby(['dt']).apply(lambda x:cal_return_rate(x,model_real_name))
            single_model_performance_return = Labels_prod_summary_new_cal_model.groupby(['dt']).apply(lambda x:cal_return(x,model_real_name))
            ZT_origin_model_return_rate = pd.concat([ZT_origin_model_return_rate,single_model_performance_rate],axis = 1)
            ZT_origin_model_return = pd.concat([ZT_origin_model_return,single_model_performance_return],axis = 1)
            this_model_recall, this_model_win = cal_recall_win(Labels_prod_summary_new_cal_origin_ZT, model_real_name)
            ZT_origin_model_recall = pd.concat([ZT_origin_model_recall,this_model_recall],axis = 1)
            ZT_origin_model_win = pd.concat([ZT_origin_model_win,this_model_win],axis = 1)
        # 原集成模型信号
        old_cla_vote = Labels_prod_summary_new_cal_origin_ZT[['Pct5XgbClaModel_local_prob','TotalLgbClaWjModel_local_prob','TotalDjClaModel_local_prob']].sum(axis = 1)
        old_reg_vote = Labels_prod_summary_new_cal_origin_ZT[['TotalLrModel_local_prob', 'TotalXgbModel_local_prob', 'HBXgbModel_local_prob','Pct5XgbModel_local_prob']].sum(axis = 1)
        Labels_prod_summary_new_cal_origin_ZT['old_shouldBuySignal'] = (old_cla_vote+old_reg_vote) >= 3

        prod_origin_ZT_signal = Labels_prod_summary_new_cal_origin_ZT[Labels_prod_summary_new_cal_origin_ZT['old_shouldBuySignal'] == True]
        prod_origin_ZT_return_rate = prod_origin_ZT_signal.groupby(['dt']).apply(lambda x:cal_return_rate(x,'old_shouldBuySignal'))
        prod_origin_ZT_return = prod_origin_ZT_signal.groupby(['dt']).apply(lambda x:cal_return(x,'old_shouldBuySignal'))
        ZT_origin_model_return_rate = pd.concat([ZT_origin_model_return_rate, prod_origin_ZT_return_rate], axis=1)
        ZT_origin_model_return = pd.concat([ZT_origin_model_return, prod_origin_ZT_return], axis=1)
        prod_origin_ZT_model_raw_stats = Labels_prod_summary_new_cal_origin_ZT.groupby(['dt']).apply(lambda x: pd.Series({'总正样本数量': x['real_positive'].sum(),
                                                                    '预测正确正样本数量': (x['real_positive'] & (x['old_shouldBuySignal'] == 1)).sum(),
                                                                    '预测正样本数量': x['old_shouldBuySignal'].sum()}))
        prod_origin_ZT_model_rolling_stats = prod_origin_ZT_model_raw_stats.rolling(20, 10).sum()
        prod_origin_ZT_model_recall = pd.DataFrame(prod_origin_ZT_model_rolling_stats['预测正确正样本数量'] / prod_origin_ZT_model_rolling_stats['总正样本数量'], columns=['old_shouldBuySignal'])
        prod_origin_ZT_model_win_rate = pd.DataFrame(prod_origin_ZT_model_rolling_stats['预测正确正样本数量'] / prod_origin_ZT_model_rolling_stats['预测正样本数量'], columns=['old_shouldBuySignal'])
        ZT_origin_model_recall = pd.concat([ZT_origin_model_recall, prod_origin_ZT_model_recall], axis=1)
        ZT_origin_model_win = pd.concat([ZT_origin_model_win, prod_origin_ZT_model_win_rate], axis=1)

        # 合并涨停样本的走势
        ZT_model_return_rate = ZT_model_return_rate[['ZTXgbModel_daily_pct_sum', 'ZTBysModel_daily_pct_sum','ZTDjRegModel_daily_pct_sum','ZTDjClaModel_daily_pct_sum','shouldBuySignal_daily_pct_sum']].join(
            ZT_origin_model_return_rate)
        ZT_model_return = ZT_model_return[['ZTXgbModel_daily_profit_sum', 'ZTBysModel_daily_profit_sum','ZTDjRegModel_daily_profit_sum','ZTDjClaModel_daily_profit_sum', 'shouldBuySignal_daily_profit_sum']].join(
            ZT_origin_model_return)
        ZT_model_recall = ZT_model_recall[['ZTXgbModel', 'ZTBysModel', 'ZTDjRegModel', 'ZTDjClaModel', 'shouldBuySignal']].join(
            ZT_origin_model_recall)
        ZT_model_win = ZT_model_win[['ZTXgbModel', 'ZTBysModel', 'ZTDjRegModel', 'ZTDjClaModel', 'shouldBuySignal']].join(
            ZT_origin_model_win)
        for column in ['TotalXgbRegWjModel','HBXgbModel','Pct5XgbModel']:
            all_model_recall.loc['20201218':,column] = np.nan
            all_model_win.loc['20201218':,column] = np.nan
        excel_saver({'收益对比':comparison_plot_data,
                     '模型理论收益率':all_model_return_rate.loc[pd.Timestamp('20200603'):].cumsum().fillna(method = 'ffill'),
                     '模型理论获得收益':all_model_return.loc[pd.Timestamp('20200603'):].cumsum().fillna(method = 'ffill'),
                     '模型召回率':all_model_recall.loc[pd.Timestamp('20200603'):],
                     '模型胜率':all_model_win.loc[pd.Timestamp('20200603'):],
                     'ZT模型理论收益率': ZT_model_return_rate.loc[pd.Timestamp('20200706'):].cumsum().fillna(method = 'ffill'),
                     'ZT模型理论获得收益': ZT_model_return.loc[pd.Timestamp('20200706'):].cumsum().fillna(method = 'ffill'),
                     'ZT模型召回率': ZT_model_recall.loc[pd.Timestamp('20200706'):],
                     'ZT模型胜率': ZT_model_win.loc[pd.Timestamp('20200706'):]
                     },'/data/group/800463/日内强势股/log_parse/模型表现/模型表现_%s.xlsx'%date)
    else:
        excel_saver({'模型理论收益率': all_model_return_rate.loc[pd.Timestamp('20200603'):].cumsum().fillna(method = 'ffill'),
                     '模型理论获得收益': all_model_return.loc[pd.Timestamp('20200603'):].cumsum().fillna(method = 'ffill'),
                     '模型召回率': all_model_recall.loc[pd.Timestamp('20200603'):],
                     '模型胜率': all_model_win.loc[pd.Timestamp('20200603'):]
                     }, '/data/group/800463/日内强势股/log_parse/模型表现/模型表现_%s.xlsx' % date)'''




'''Adate='2023-03-09'
Label_summary = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/实盘触发标签汇总_%s.xlsx' % Adate)
Label_summary['label_T_is_zt'] = (Label_summary['买入时形态'] >= 3).astype(int)
Label_summary['label_zt_lianxu_in3days'] = 0
Label_summary.loc[Label_summary.query('label_T_is_zt==1 and label_T1_zt==0').index, 'label_zt_lianxu_in3days'] = 1
Label_summary.loc[Label_summary.query('label_T_is_zt==1 and label_T1_zt==1').index, 'label_zt_lianxu_in3days'] = 2
if 'ZTBysModel_local_prob' in Label_summary.columns.tolist():
    Label_summary = Label_summary[Label_summary['ZTBysModel_local_prob'].isna()]
print(Label_summary.label_zt_lianxu_in3days.value_counts())
Label_summary['real_positive'] = (Label_summary['买入时形态'] == 4) & (Label_summary['TN_o2ul'] > 0)
Label_summary['dt'] = Label_summary['dt'].apply(lambda x: x.strftime('%Y-%m-%d'))
Label_summary_stats = Label_summary.groupby('dt').apply(lambda x: pd.Series({'触发总数': len(x)
                                                                                , '形态4数量': (x['买入时形态'] == 4).sum()
                                                                                , '形态3数量': (x['买入时形态'] == 3).sum()
                                                                                , '形态2数量': (x['买入时形态'] == 2).sum()
                                                                                , '收盘涨停数量': (
                (x['买入时形态'] == 3) | (x['买入时形态'] == 4)).sum()
                                                                                , '形态2_o2ul_总和': x[x['买入时形态'] == 2][
        'TN_o2ul'].sum()
                                                                                , '形态4_o2ul_总和': x[x['买入时形态'] == 4][
        'TN_o2ul'].sum()
                                                                                , '形态3_o2ul_总和': x[x['买入时形态'] == 3][
        'TN_o2ul'].sum()
                                                                                , '买入当日十点前突破数量': x['ZT_Time'].apply(
        lambda x: int(x) < 100000000).sum()
                                                                                , '首板_o2ul_总和':
                                                                                 x[x['label_zt_lianxu_in3days'] == 1][
                                                                                     'TN_o2ul'].sum()
                                                                                , '二连板_o2ul_总和':
                                                                                 x[x['label_zt_lianxu_in3days'] == 2][
                                                                                     'TN_o2ul'].sum()
                                                                                , '三连板_o2ul_总和':
                                                                                 x[x['label_zt_lianxu_in3days'] == 3][
                                                                                     'TN_o2ul'].sum()
                                                                                , '首板数量': (
                x['label_zt_lianxu_in3days'] == 1).sum()
                                                                                , '二连板数量': (
                x['label_zt_lianxu_in3days'] == 2).sum()
                                                                                , '三连板数量': (
                x['label_zt_lianxu_in3days'] == 3).sum()
                                                                             }))
rolldays_num=5
Label_summary_stats_rolling_3 = Label_summary_stats.rolling(rolldays_num,1).sum()
Label_summary_stats_rolling_3['触发总数_roll%ddays'%rolldays_num] = Label_summary_stats['触发总数'].rolling(rolldays_num,1).mean()
Label_summary_basic = Label_summary.copy()#
#Label_summary_basic['dt'] = Label_summary_basic['dt'].apply(lambda x: pd.Timestamp(x))
Label_summary_basic = Label_summary_basic.set_index(['dt','Ticker']).sort_index()
if 'ZTBysModel_local_prob' in Label_summary_basic.columns.tolist():
    Label_summary_basic = Label_summary_basic[(Label_summary_basic['ZTBysModel_local_prob'].isna())]#.loc['2021-01-01':]
Label_summary_basic_stats = Label_summary_basic.groupby('dt').apply(lambda x: pd.Series({'触发总数': len(x),
                                                                                 'Tc2Tul': (x['label_Tc2Tul'].fillna(0)).sum(),
                                                                                 'T1o2Tc': (x['label_T1o2Tc'].fillna(0)).sum(),
                                                                                 'T1c2Tc': (x['label_T1c2Tc'].fillna(0)).sum(),
                                                                                 '收盘涨停数量': ((x['买入时形态'] == 3) | (x['买入时形态'] == 4)).sum()}
                                                                                 ))
daily_basic_metrics = Label_summary_basic_stats.copy()#[['触发总数','收盘涨停数量']]
daily_basic_metrics['封板率'] = (daily_basic_metrics['收盘涨停数量']/daily_basic_metrics['触发总数']).fillna(0)
daily_basic_metrics['Tc2Tul均值'] = 100*(daily_basic_metrics['Tc2Tul']/daily_basic_metrics['触发总数']).fillna(0)
daily_basic_metrics['T1o2Tc均值'] = 100*(daily_basic_metrics['T1o2Tc'] / daily_basic_metrics['触发总数']).fillna(0)
daily_basic_metrics['T1c2Tc均值'] = 100*(daily_basic_metrics['T1c2Tc'] / daily_basic_metrics['触发总数']).fillna(0)
daily_basic_metrics.drop(columns=['收盘涨停数量','Tc2Tul','T1o2Tc','T1c2Tc'], inplace=True)
Label_summary_stats_rolling_3_2021 = Label_summary_stats.loc[
                                         '2021-01-04':].sort_index()  # [Label_summary_stats_rolling_3['dt'] >= '2022-01-04']
all_zt_1_o2ul = pd.DataFrame(Label_summary_stats_rolling_3_2021['首板_o2ul_总和'] / Label_summary_stats_rolling_3_2021['首板数量'])#.fillna(0)
all_zt_1_o2ul.columns = ['CZT1']
all_zt_2o2ul = pd.DataFrame(Label_summary_stats_rolling_3_2021['二连板_o2ul_总和'] / Label_summary_stats_rolling_3_2021['二连板数量'])#.fillna(0)
all_zt_2o2ul.columns = ['CZT2']
all_zt_df = pd.concat([all_zt_1_o2ul,all_zt_2o2ul],axis=1).fillna(0)
all_zt_df.rename(columns = {'CZT1':'CZT1_o2ul','CZT2':'CZT2_o2ul'},inplace=True)
# daily_basic_metrics['dt'] = [pd.Timestamp(x) for x in all_zt_df.index.tolist()]
# all_zt_df.set_index(['dt'],inplace=True)
daily_basic_metrics = daily_basic_metrics.loc['2021-01-01':].sort_index()
all_stats_df = pd.concat([all_zt_df,daily_basic_metrics],axis=1,join_axes=[daily_basic_metrics.index])
all_stats_df.to_excel('/data/user/013550/Jupiter/成交记录/样本统计_%s.xlsx'%Adate)'''
























