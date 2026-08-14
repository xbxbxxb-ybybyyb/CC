# coding: utf-8
# Author：fengchi863
# Date ：2023/9/7 20:09

import sys
import os
sys.path.append('/data/user/015614/Lucien')

import pandas as pd
import numpy as np
np.random.seed(2008)
from dataApi import stockList, tradeDate, getData
from tqdm import tqdm
from LucienUtil.FileUtil import FileUtil

europa = pd.read_hdf("/data/user/015614/factor/digging历史/factor_digging_20230906165418_20230906测试_Trans_TTickab_已经全部提交/(1, 's100', 8).h5")

def calc_limit_max(pre_close):
    cyb = list(filter(lambda x: stockList.trans_int2windcode(x).startswith('3'), pre_close.columns.tolist()))
    not_cyb = list(filter(lambda x: stockList.trans_int2windcode(x).startswith('3') - 1, pre_close.columns.tolist()))
    if pre_close.index[0] >= 20200824:
        pre_close_cyb = pre_close[cyb]
        pre_close_not_cyb = pre_close[not_cyb]
        limit_max_cyb = (pre_close_cyb * 100 * 1.2 + 0.5).apply(np.floor) / 100
        limit_max_not_cyb = (pre_close_not_cyb * 100 * 1.1 + 0.5).apply(np.floor) / 100
        limit_max = pd.concat([limit_max_cyb, limit_max_not_cyb], axis=1)[pre_close.columns]
        return limit_max
    elif pre_close.index[-1] < 20200824:
        limit_max = (pre_close * 100 * 1.1 + 0.5).apply(np.floor) / 100
        return limit_max
    else:
        after_20200824 = pre_close.loc[20200824:]
        before_20200824 = pre_close.loc[:20200823]
        limit_max_before_20200824 = (before_20200824 * 100 * 1.1 + 0.5).apply(np.floor) / 100

        pre_close_cyb = after_20200824[cyb]
        pre_close_not_cyb = after_20200824[not_cyb]
        limit_max_cyb = (pre_close_cyb * 100 * 1.2 + 0.5).apply(np.floor) / 100
        limit_max_not_cyb = (pre_close_not_cyb * 100 * 1.1 + 0.5).apply(np.floor) / 100
        limit_max_after_20200824 = pd.concat([limit_max_cyb, limit_max_not_cyb], axis=1)[pre_close.columns]

        limit_max = pd.concat([limit_max_before_20200824, limit_max_after_20200824], axis=0)
    return limit_max

europa['trade_date'] = europa.index.get_level_values(0).map(lambda x: int(x.strftime('%Y%m%d')))
europa['stk_id'] = europa.index.get_level_values(1).map(lambda x: stockList.trans_windcode2int(x))
europa = europa.set_index(['trade_date', 'stk_id'])

#%% 读取申万行业
for idx in tqdm(range(len(europa))):
    print(f'{idx+1} / {len(europa)}')
    trade_date, stk_id = europa.iloc[idx].name
    trade_date, stk_id = 20190321, 2592
    trade_date, stk_id = 20191231, 2192
    trade_date, stk_id = 20160105, 20
    try:
        yes_date = tradeDate.get_pre_trade_date(trade_date)
        stk_code = stockList.trans_int2windcode(stk_id)

        ind_df = pd.read_pickle(f'/data/user/015614/daily/basic/basic_wind_sw_history2/BlockData/daily_Wind&SW/{trade_date}.pkl')
        wind_factor = pd.read_pickle(f'/data/user/015614/daily/basic/basic_wind_sw_history2/BlockData/daily_wind_factor/{yes_date}.pkl')
        sw_factor = pd.read_pickle(f'/data/user/015614/daily/basic/basic_wind_sw_history2/BlockData/daily_sw_factor/{yes_date}.pkl')
        concept_list = ind_df.loc[stk_code][ind_df.loc[stk_code]==1].index.tolist()
        wind_concept_list = list(filter(lambda x: str(x).endswith('WI'), concept_list))
        sw_concept_list = list(filter(lambda x: str(x).endswith('SI'), concept_list))

        yes_wind_max_pctchg = wind_factor.loc[wind_concept_list].max().values[0]
        yes_wind_mean_pctchg = wind_factor.loc[wind_concept_list].mean().values[0]
        yes_sw_pctchg = sw_factor.loc[sw_concept_list].max().values[0]

        # 昨日概念内个股涨停数量
        wind_zt_stk_list = list()
        wind_czt_stk_list = list()
        for wind_concept in wind_concept_list:
            concept_stk_list = ind_df[wind_concept][ind_df[wind_concept]==1].index.tolist()
            if len(concept_stk_list) > 100:
                wind_concept_list.remove(wind_concept)
                continue

            pre_close = getData.get_daily_1factor('pre_close', date_list=[yes_date], code_list=concept_stk_list)
            limit_max = calc_limit_max(pre_close)
            close = getData.get_daily_1factor('close', date_list=[yes_date], code_list=concept_stk_list)
            high = getData.get_daily_1factor('high', date_list=[yes_date], code_list=concept_stk_list)
            low = getData.get_daily_1factor('low', date_list=[yes_date], code_list=concept_stk_list)
            zt = pd.DataFrame((close == limit_max))
            daily_pctchg = getData.get_daily_1factor('pct_chg', date_list=[yes_date], code_list=concept_stk_list)
            daily_max_pctchg = (high / pre_close - 1) * 100
            czt = pd.DataFrame((high == limit_max))
            czt = czt & (daily_max_pctchg > 6)

            zt = zt.T
            czt = czt.T

            wind_zt_stk_list += zt[zt==1].dropna().index.tolist()
            wind_czt_stk_list += czt[czt==1].dropna().index.tolist()

        sw_zt_stk_list = list()
        sw_czt_stk_list = list()
        for sw_concept in sw_concept_list:
            concept_stk_list = ind_df[sw_concept][ind_df[sw_concept] == 1].index.tolist()
            pre_close = getData.get_daily_1factor('pre_close', date_list=[yes_date], code_list=concept_stk_list)
            limit_max = calc_limit_max(pre_close)
            close = getData.get_daily_1factor('close', date_list=[yes_date], code_list=concept_stk_list)
            high = getData.get_daily_1factor('high', date_list=[yes_date], code_list=concept_stk_list)
            low = getData.get_daily_1factor('low', date_list=[yes_date], code_list=concept_stk_list)
            zt = pd.DataFrame((close == limit_max))
            daily_pctchg = getData.get_daily_1factor('pct_chg', date_list=[yes_date], code_list=concept_stk_list)
            daily_max_pctchg = (high / pre_close - 1) * 100
            czt = pd.DataFrame((high == limit_max))
            czt = czt & (daily_max_pctchg > 6)

            zt = zt.T
            czt = czt.T

            sw_zt_stk_list += zt[zt == 1].dropna().index.tolist()
            sw_czt_stk_list += czt[czt == 1].dropna().index.tolist()

        europa.loc[(trade_date, stk_id), '所属Wind概念数量'] = len(wind_concept_list)
        europa.loc[(trade_date, stk_id), '所属SW2概念数量'] = len(sw_concept_list)
        europa.loc[(trade_date, stk_id), '昨日所属Wind概念最大涨跌幅'] = yes_wind_max_pctchg
        europa.loc[(trade_date, stk_id), '昨日所属Wind概念平均涨跌幅'] = yes_wind_mean_pctchg
        europa.loc[(trade_date, stk_id), '昨日所属SW2涨跌幅'] = yes_sw_pctchg
        europa.loc[(trade_date, stk_id), '昨日所属Wind概念涨停个数'] = len(set(wind_zt_stk_list))
        europa.loc[(trade_date, stk_id), '昨日所属Wind概念触板个数'] = len(set(wind_czt_stk_list))
        europa.loc[(trade_date, stk_id), '昨日所属SW2涨停个数'] = len(set(sw_zt_stk_list))
        europa.loc[(trade_date, stk_id), '昨日所属SW2触板个数'] = len(set(sw_czt_stk_list))
        # print(trade_date, stk_id, len(wind_concept_list), len(sw_concept_list), yes_wind_max_pctchg, yes_wind_mean_pctchg, yes_sw_pctchg,
        #       len(set(wind_zt_stk_list)), len(set(wind_czt_stk_list)), len(set(sw_zt_stk_list)), len(set(sw_czt_stk_list)))
    except:
        print(trade_date, stk_id, 'Error')
        FileUtil.save_df2pkl(pd.DataFrame(), '/data/user/015614/junkData/error_df/', f'{trade_date}_{stk_id}.pkl')

# europa.to_pickle('/data/user/015614/junkData/concept_factor.pkl')
print('计算完成！保存成功！请查看是否有错误样本！')