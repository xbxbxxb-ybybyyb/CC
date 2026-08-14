import pandas as pd
import numpy as np
import decimal
import os
from h5data.IO import IO
from xquant.factordata import FactorData
s = FactorData()

def round_(x, n=13):
    x = x + 1e-15
    if n > 0:
        res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),rounding=decimal.ROUND_HALF_UP))
    else:
        res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
    return res

strategy_version = 20250609
start_date, end_date = 20170110,20241231

profit_path = '/data/user/021012/团队分享/for_tsq/neptune/profit_backtest/2017_2023'
long_term_name = 'p2_profit_intervalTwap_931_941_Sell_intervalTwap_931_941_0.10_0.10.h5'
mid_term_name = 'p2_profit_intervalTwap_931_941_Sell_T0_intervalTwap_1430_1440_0.10_0.10.h5'
short_term_name = 'p2_profit_intervalTwap_931_941_Sell_T0_intervalTwap_1000_1010_0.10_0.10.h5'

label_df_long_term = pd.read_hdf(os.path.join(profit_path,long_term_name))
label_df_mid_term = pd.read_hdf(os.path.join(profit_path,mid_term_name))
label_df_short_term = pd.read_hdf(os.path.join(profit_path,short_term_name))

label_df_long_term_neg = label_df_long_term.copy()
label_df_mid_term_neg = label_df_mid_term.copy()
label_df_short_term_neg = label_df_short_term.copy()

label_df_long_term_neg['pct'] = -1*label_df_long_term_neg['pct']
label_df_mid_term_neg['pct'] = -1*label_df_mid_term_neg['pct']
label_df_short_term_neg['pct'] = -1*label_df_short_term_neg['pct']

IO.pd_hdf5_writer(label_df_long_term, hdf5='/data/group/800463/tangsq/neptune/profit/20250609/p2_profit_intervalTwap_s1_long_term_0.10_0.10.h5', dataset='neptune')
IO.pd_hdf5_writer(label_df_mid_term, hdf5='/data/group/800463/tangsq/neptune/profit/20250609/p2_profit_intervalTwap_s1_mid_term_0.10_0.10.h5', dataset='neptune')
IO.pd_hdf5_writer(label_df_short_term, hdf5='/data/group/800463/tangsq/neptune/profit/20250609/p2_profit_intervalTwap_s1_short_term_0.10_0.10.h5', dataset='neptune')

IO.pd_hdf5_writer(label_df_long_term_neg, hdf5='/data/group/800463/tangsq/neptune/profit/20250609/neg/p2_profit_intervalTwap_s1_long_term_0.10_0.10.h5', dataset='neptune')
IO.pd_hdf5_writer(label_df_mid_term_neg, hdf5='/data/group/800463/tangsq/neptune/profit/20250609/neg/p2_profit_intervalTwap_s1_mid_term_0.10_0.10.h5', dataset='neptune')
IO.pd_hdf5_writer(label_df_short_term_neg, hdf5='/data/group/800463/tangsq/neptune/profit/20250609/neg/p2_profit_intervalTwap_s1_short_term_0.10_0.10.h5', dataset='neptune')

md = IO.read_data([20170110,20250331],columns=['pre_close','close','amt'], alt='/data/group/800080/warehouseJG/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
md['zcz'] = (((md.reset_index()['Ticker'].apply(lambda x: x[0] == '3'))&(md.reset_index()['dt'] >= '2020-08-24')) | (md.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
md['ul_price'] = md['pre_close'].apply(lambda x: round_(x * 1.1, 2))
md['dl_price'] = md['pre_close'].apply(lambda x: round_(x * 0.9, 2))
md.loc[md['zcz'],'ul_price'] = md.loc[md['zcz'],'pre_close'].apply(lambda x: round_(x * 1.2, 2))
md.loc[md['zcz'],'dl_price'] = md.loc[md['zcz'],'pre_close'].apply(lambda x: round_(x * 0.8, 2))

md['label_T_close_is_zt'] = (md['close']==md['ul_price']).astype(float)
md = md[md['amt']>0]
md = md.sort_index(level=['Ticker', 'dt'])
md['label_Next_close_is_zt'] = md.groupby('Ticker')['label_T_close_is_zt'].shift(-1)

label_df_long_term[['label_T_close_is_zt','label_Next_close_is_zt']] = md[['label_T_close_is_zt','label_Next_close_is_zt']]
label_df_mid_term[['label_T_close_is_zt','label_Next_close_is_zt']] = md[['label_T_close_is_zt','label_Next_close_is_zt']]
label_df_short_term[['label_T_close_is_zt','label_Next_close_is_zt']] = md[['label_T_close_is_zt','label_Next_close_is_zt']]

label_df_long_term['label_pct'] = label_df_long_term['pct']
label_df_long_term['label_Tc2b10'] = label_df_long_term['label_pct']
label_df_long_term['label_TNo2Tc'] = label_df_long_term['label_pct']
label_df_long_term['label_TNv2TNo'] = label_df_long_term['label_pct']

label_df_mid_term['label_pct'] = label_df_mid_term['pct']
label_df_mid_term['label_Tc2b10'] = label_df_mid_term['label_pct']
label_df_mid_term['label_TNo2Tc'] = label_df_mid_term['label_pct']
label_df_mid_term['label_TNv2TNo'] = label_df_mid_term['label_pct']

label_df_short_term['label_pct'] = label_df_short_term['pct']
label_df_short_term['label_Tc2b10'] = label_df_short_term['label_pct']
label_df_short_term['label_TNo2Tc'] = label_df_short_term['label_pct']
label_df_short_term['label_TNv2TNo'] = label_df_short_term['label_pct']

# neg
label_df_long_term_neg[['label_T_close_is_zt','label_Next_close_is_zt']] = md[['label_T_close_is_zt','label_Next_close_is_zt']]
label_df_mid_term_neg[['label_T_close_is_zt','label_Next_close_is_zt']] = md[['label_T_close_is_zt','label_Next_close_is_zt']]
label_df_short_term_neg[['label_T_close_is_zt','label_Next_close_is_zt']] = md[['label_T_close_is_zt','label_Next_close_is_zt']]

label_df_long_term_neg['label_pct'] = label_df_long_term_neg['pct']
label_df_long_term_neg['label_Tc2b10'] = label_df_long_term_neg['label_pct']
label_df_long_term_neg['label_TNo2Tc'] = label_df_long_term_neg['label_pct']
label_df_long_term_neg['label_TNv2TNo'] = label_df_long_term_neg['label_pct']

label_df_mid_term_neg['label_pct'] = label_df_mid_term_neg['pct']
label_df_mid_term_neg['label_Tc2b10'] = label_df_mid_term_neg['label_pct']
label_df_mid_term_neg['label_TNo2Tc'] = label_df_mid_term_neg['label_pct']
label_df_mid_term_neg['label_TNv2TNo'] = label_df_mid_term_neg['label_pct']

label_df_short_term_neg['label_pct'] = label_df_short_term_neg['pct']
label_df_short_term_neg['label_Tc2b10'] = label_df_short_term_neg['label_pct']
label_df_short_term_neg['label_TNo2Tc'] = label_df_short_term_neg['label_pct']
label_df_short_term_neg['label_TNv2TNo'] = label_df_short_term_neg['label_pct']

# label_long_term = profit.copy()[['label_t2o10dc_pos','label_Tc2b10_pos','label_TNo2Tc_pos','label_TNv2TNo_pos','label_T_close_is_zt','label_Next_close_is_zt']].rename(
#     columns={'label_t2o10dc_pos':'label_t2o10dc','label_Tc2b10_pos':'label_Tc2b10','label_TNo2Tc_pos':'label_TNo2Tc','label_TNv2TNo_pos':'label_TNv2TNo'})
# label_neg = profit.copy()[['label_t2o10dc_neg','label_Tc2b10_neg','label_TNo2Tc_neg','label_TNv2TNo_neg','label_T_close_is_zt','label_Next_close_is_zt']].rename(
#     columns={'label_t2o10dc_neg':'label_t2o10dc','label_Tc2b10_neg':'label_Tc2b10','label_TNo2Tc_neg':'label_TNo2Tc','label_TNv2TNo_neg':'label_TNv2TNo'})

IO.pd_hdf5_writer(label_df_long_term[['label_pct','label_Tc2b10','label_TNo2Tc','label_TNv2TNo','label_T_close_is_zt','label_Next_close_is_zt']], hdf5=f'/dfs/user/023859/share_file/for_skk/neptune/{strategy_version}/zz1000_labels_file_s1_long_term.h5', dataset='neptune',override=True)
IO.pd_hdf5_writer(label_df_mid_term[['label_pct','label_Tc2b10','label_TNo2Tc','label_TNv2TNo','label_T_close_is_zt','label_Next_close_is_zt']], hdf5=f'/dfs/user/023859/share_file/for_skk/neptune/{strategy_version}/zz1000_labels_file_s1_mid_term.h5', dataset='neptune',override=True)
IO.pd_hdf5_writer(label_df_short_term[['label_pct','label_Tc2b10','label_TNo2Tc','label_TNv2TNo','label_T_close_is_zt','label_Next_close_is_zt']], hdf5=f'/dfs/user/023859/share_file/for_skk/neptune/{strategy_version}/zz1000_labels_file_s1_short_term.h5', dataset='neptune',override=True)


IO.pd_hdf5_writer(label_df_long_term_neg[['label_pct','label_Tc2b10','label_TNo2Tc','label_TNv2TNo','label_T_close_is_zt','label_Next_close_is_zt']], hdf5=f'/dfs/user/023859/share_file/for_skk/neptune/{strategy_version}/zz1000_labels_file_s1_long_term_neg.h5', dataset='neptune')
IO.pd_hdf5_writer(label_df_mid_term_neg[['label_pct','label_Tc2b10','label_TNo2Tc','label_TNv2TNo','label_T_close_is_zt','label_Next_close_is_zt']], hdf5=f'/dfs/user/023859/share_file/for_skk/neptune/{strategy_version}/zz1000_labels_file_s1_mid_term_neg.h5', dataset='neptune')
IO.pd_hdf5_writer(label_df_short_term_neg[['label_pct','label_Tc2b10','label_TNo2Tc','label_TNv2TNo','label_T_close_is_zt','label_Next_close_is_zt']], hdf5=f'/dfs/user/023859/share_file/for_skk/neptune/{strategy_version}/zz1000_labels_file_s1_short_term_neg.h5', dataset='neptune')

# profit['buy_vol']=np.nan
# profit['buy_vwap']=np.nan
# profit['pct_T']=np.nan
# profit['buy_tick_num']=np.nan
# profit['last_buy_time']=np.nan
# profit['target_vol']=np.nan
# profit['pct_T1']=np.nan
# profit['sell_len']=np.nan
# profit['date_list']=np.nan
# profit['touch_list']=np.nan
# profit['vol_list']=np.nan
# profit['Sell_ratio']=np.nan
# profit_pos = profit.copy()[['buy_vol','buy_amt','buy_vwap','pct_T','buy_tick_num','last_buy_time','target_vol','pct_T1','sell_len','date_list','touch_list','vol_list','Sell_ratio','label_t2o10dc_pos']].rename(columns={'label_t2o10dc_pos':'pct'})
# profit_neg = profit.copy()[['buy_vol','buy_amt','buy_vwap','pct_T','buy_tick_num','last_buy_time','target_vol','pct_T1','sell_len','date_list','touch_list','vol_list','Sell_ratio','label_t2o10dc_neg']].rename(columns={'label_t2o10dc_neg':'pct'})
#
# IO.pd_hdf5_writer(profit_pos, hdf5=f'/dfs/user/023859/share_file/for_wj/neptune/{strategy_version}/zz1000_profit_interval_sc_pos.h5', dataset='neptune')
# IO.pd_hdf5_writer(profit_neg, hdf5=f'/dfs/user/023859/share_file/for_wj/neptune/{strategy_version}/zz1000_profit_interval_sc_neg.h5', dataset='neptune')
# IO.pd_hdf5_writer(profit_pos, hdf5=f'/dfs/user/023859/share_file/for_skk/neptune/{strategy_version}/zz1000_profit_interval_sc_pos.h5', dataset='neptune')
# IO.pd_hdf5_writer(profit_neg, hdf5=f'/dfs/user/023859/share_file/for_skk/neptune/{strategy_version}/zz1000_profit_interval_sc_neg.h5', dataset='neptune')